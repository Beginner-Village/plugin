
from typing import Annotated, Any
import asyncio
from fastapi import Body
from pydantic import BaseModel
from rq.job import JobStatus
from rq.command import send_stop_job_command

from app.api.v1.common import api_v1
from app.schema.common import CommonResponse, HttpException
from app.schema.plugin import PackageMetaBrief, PackageMeta, PackageMetaBriefWithEntry
from app.package_mgr import install_pkg, install_pkg_wrapper, get_package_meta
from app.config import get_worker_queue
import app.runtime.sock_client as runtime


@api_v1.post("/InstallPackage")
async def install_package(
    uri: Annotated[str, Body(embed=True)],
    filename: Annotated[str, Body(embed=True)],
    force: Annotated[bool, Body(embed=True)] = True,
) -> CommonResponse[PackageMeta]:
    """导入插件"""
    pkg_meta = await asyncio.to_thread(install_pkg, uri, filename, force)
    metadata = await runtime.run_pkg_metadata(pkg_meta.name, pkg_meta.version)
    ret = PackageMeta(
        name=pkg_meta.name,
        version=pkg_meta.version,
        uri=uri,
        filename=filename,
        plugins=metadata,
    )
    return CommonResponse(data=ret)


@api_v1.post("/ReadPackageMetadata")
async def read_package_metadata(
    uri: Annotated[str, Body(embed=True)],
    filename: Annotated[str, Body(embed=True)],
) -> CommonResponse[PackageMetaBriefWithEntry]:
    """获取包的元数据, 不安装包"""
    pkg_meta = await asyncio.to_thread(get_package_meta, uri, filename)
    return CommonResponse(data=pkg_meta)


class ImportPackageAsyncResp(BaseModel):
    job_id: str


@api_v1.post("/InstallPackageAsync")
def install_package_async(
    uri: Annotated[str, Body(embed=True)],
    filename: Annotated[str, Body(embed=True)],
    force: Annotated[bool, Body(embed=True)] = False,
) -> CommonResponse[ImportPackageAsyncResp]:
    """异步导入插件"""
    q = get_worker_queue()
    job = q.enqueue(install_pkg_wrapper, args=(uri, filename, force))
    return CommonResponse(data=ImportPackageAsyncResp(job_id=job.id))


class ImportStatusResp(BaseModel):
    status: JobStatus
    reason: str | None = None
    data: PackageMetaBrief | None = None


@api_v1.post("/GetInstallPackageAsyncStatus")
def get_install_package_async_status(
    job_id: Annotated[str, Body(embed=True)],
) -> CommonResponse[ImportStatusResp]:
    """异步导入插件"""
    q = get_worker_queue()
    job = q.fetch_job(job_id)
    if job is None:
        raise HttpException(code="ImportPluginError",
                            message=f"job {job_id} not found", http_code=404)
    status = job.get_status()
    if status is None:
        raise HttpException(
            code="ImportPluginError",
            message=f"job {job_id} status is None",
            http_code=500,
        )
    if not job.is_finished:
        return CommonResponse(data=ImportStatusResp(status=status, reason=job.exc_info))
    data: CommonResponse[PackageMetaBrief] | None = job.return_value()
    if data is None:
        raise HttpException(
            code="ImportPluginError",
            message=f"job {job_id} return value is None",
            http_code=500,
        )
    if data.error is not None:
        return CommonResponse(data=ImportStatusResp(status=JobStatus.FAILED, reason=f'{data.error.code}: {data.error.message}'))
    return CommonResponse(data=ImportStatusResp(status=status, data=data.data))


@api_v1.post("/RetryInstallPackage")
def retry_install_package(
    job_id: Annotated[str, Body(embed=True)],
) -> CommonResponse[None]:
    """重试导入"""
    q = get_worker_queue()
    job = q.fetch_job(job_id)
    if job is None:
        raise HttpException(code="RetryInstallPackageError",
                            message=f"job {job_id} is expired", http_code=404)
    # stop and recreate
    send_stop_job_command(q.connection, job_id)
    q.enqueue(job.func, args=job._args, kwargs=job._kwargs, job_id=job.id)
    return CommonResponse(data=None)


@api_v1.post("/CancelInstallPackage")
def cancel_install_package(
    job_id: Annotated[str, Body(embed=True)],
) -> CommonResponse[None]:
    """重试导入"""
    q = get_worker_queue()
    job = q.fetch_job(job_id)
    if job is None:
        raise HttpException(code="CancelInstallPackageError",
                            message=f"job {job_id} is expired", http_code=404)
    status = job.get_status()
    if status not in [JobStatus.QUEUED, JobStatus.STARTED, JobStatus.DEFERRED, JobStatus.SCHEDULED]:
        raise HttpException(code="CancelInstallPackageError",
                            message=f"job {job_id} is {status}: can not cancel", http_code=400)
    send_stop_job_command(q.connection, job_id)
    return CommonResponse(data=None)

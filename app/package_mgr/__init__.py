import requests
import logging
from typing import List
import os
from pathlib import Path
from app.config import load
import subprocess
import logging
from urllib import parse
from app.lib.wheel_entry import Wheel
from app.config import PLUGIN_ENTRY_GROUP
from app.schema.common import  HttpException, CommonResponse, HttpError
from app.schema.plugin import PackageMetaBrief, PackageMetaBriefWithEntry

logger = logging.getLogger(__name__)

def install_pkg_wrapper(uri: str, filename: str, force=False) -> CommonResponse[PackageMetaBrief]:
    """安装插件"""
    try:
        ret = install_pkg(uri, filename, force)
        res = CommonResponse(data=ret)
    except Exception as e:
        res = CommonResponse(error=HttpError.from_exception(e))
    # print("install_pkg_wrapper: ", res)
    return res

def install_pkg(uri: str, filename: str, force=False) -> PackageMetaBrief:
    """安装插件"""
    u = parse.urlparse(uri)
    if u.scheme == "file":
        pkg_path = u.path
    elif u.scheme == "http" or u.scheme == "https":
        pkg_path = download_pkg(uri, filename)
    else:
        raise HttpException(code="ImportPluginError", message=f"unsupported uri {uri}")

    whl = Wheel(pkg_path)
    pkg_name = whl.name
    version = whl.version
    if pkg_name is None or version is None:
        raise HttpException(code="ImportPluginError.InvalidPackage", message="pkg name or version is None")
    package_path = load().get_package_path(pkg_name, version)
    if os.path.exists(package_path) and not force:
        raise HttpException(code="ImportPluginError.AlreadyInstalled", message=f"pkg {pkg_name} version {version} already installed")
    # tmp_dir = f"/tmp/vendor/{pkg_name}-{version}"
    from tempfile import TemporaryDirectory as tmpdir
    with tmpdir() as tmp:
        if whl.extract_dependencies(tmp):
            install_offline(pkg_path, tmp, package_path)
        else:
            install_online(pkg_path, package_path)
    return PackageMetaBrief(
        name=pkg_name,
        version=version,
        uri=uri,
        filename=filename,
    )

def install_offline(wheel_path: str, dep_dir: str, target_path: str):
    cmd = [
        "pip", "install", wheel_path, "-t", target_path,
        "--no-index",
        "--find-link", f"{dep_dir}/dependencies", "--no-build-isolation",
    ]
    logging.info(f'pip install offline: {" ".join(cmd)}')

    ret = subprocess.run(cmd, stderr=subprocess.PIPE)
    err_msg = ret.stderr.decode('utf-8')
    if ret.returncode != 0:
        # output = ret.stdout.decode('utf-8')
        logging.error(f"pip install offline {wheel_path} failed: {err_msg}")

def install_online(wheel_path: str, target_path: str):
    cmd = [
        'pip','install', wheel_path, '-t', target_path, '-U',
    ]
    cfg = load()
    if cfg.package.index_url:
        cmd += ["--index-url", cfg.package.index_url]
    if cfg.package.extra_index_url:
        cmd += ["--extra-index-url", cfg.package.extra_index_url]
    if cfg.package.trusted_host:
        cmd += ["--trusted-host", cfg.package.trusted_host]
    result = subprocess.run(cmd, stderr=subprocess.PIPE)
    err_msg = result.stderr.decode('utf-8')
    # output = result.stdout.decode('utf-8')
    logging.info(f'pip install online: {" ".join(cmd)}')
    if result.returncode != 0:
        logging.error(f"pip install {wheel_path} failed: {err_msg}")
        raise HttpException(code="ImportPluginError.InstallFailed", message=err_msg)

def delete_pkg(pkg_name: str, version: str) -> None:
    """删除插件"""
    package_path = load().get_package_path(pkg_name, version)
    import shutil
    parent =  Path(package_path).parent
    if not os.path.exists(package_path):
        return
    shutil.rmtree(package_path)
    if os.listdir(parent) == []:
        os.rmdir(parent)
    return

def download_pkg(uri: str, filename: str) -> str:
    """下载插件"""
    local_path = load().local_storage_path
    pkg_path = os.path.join(local_path, "pkg", filename)
    # already downloaded
    if os.path.exists(pkg_path):
        return pkg_path
    try:
        resp = requests.get(uri, stream=True)
        os.makedirs(os.path.dirname(pkg_path), exist_ok=True)
        with open(pkg_path, 'wb') as f:
            for chunk in resp.iter_content(chunk_size=8192):
                f.write(chunk)
        resp.close()
    except Exception:
        if os.path.exists(pkg_path):
            os.remove(pkg_path)
        raise
    return pkg_path

def get_package_meta(uri: str, filename: str) -> PackageMetaBriefWithEntry:
    """获取插件包元数据, 但不安装"""
    u = parse.urlparse(uri)
    if u.scheme == "file":
        pkg_path = u.path
    elif u.scheme == "http" or u.scheme == "https":
        pkg_path = download_pkg(uri, filename)
    else:
        raise HttpException(code="ImportPluginError", message=f"unsupported uri {uri}")
    whl = Wheel(pkg_path)
    metadata = whl.extract_metadata()
    # logger.debug(f"metadata from file: {metadata}")
    if metadata is None:
        # 从旧版本中获取信息
        ret = PackageMetaBriefWithEntry(
            name=whl.name or "",
            version=whl.version or "",
            uri=uri,
            filename=filename,
        )
        # print(whl.entry_points)
        for k, v in whl.entry_points.items():
            if k == PLUGIN_ENTRY_GROUP:
                for ep in v:
                    ret.plugins.append(ep)
    else:
        ret = PackageMetaBriefWithEntry(
            name=whl.name or "",
            version=whl.version or "",
            uri=uri,
            filename=filename,
            plugins=[metadata.name,],
        )
    return ret

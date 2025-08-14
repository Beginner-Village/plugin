from typing import *
from functools import lru_cache
import asyncio
from collections import OrderedDict
from functools import partial

from reretry import retry  # type: ignore

from app.config import load
from app.schema.plugin import PluginMeta
from app.runtime.process_socket import ProcessWorker
from app.runtime.sock_handler import *
from app.schema.common import HttpException
from aiorwlock import RWLock
from hiagent_plugin_sdk.schema import Metadata

class ProcessManager:
    """lru process manager"""

    def __init__(self, max_process: int = 20):
        self.process: OrderedDict[str, ProcessWorker] = OrderedDict()
        self.lock = RWLock()
        self.max_process = max_process

    def key_fn(self, pkg, version):
        return f"{pkg}-{version}"

    async def ensure_process(self, pkg, version, addr) -> Tuple[ProcessWorker, bool]:
        # nfs 文件同步存在延迟, 这里先不检查文件是否存在
        # import os
        # package_path = load().get_package_path(pkg, version)
        # if not os.path.exists(package_path):
        #     raise HttpException(
        #         http_code=404,
        #         code="PackageNotFound",
        #         message=f"package {pkg} version {version} not found"
        #     )
        key = self.key_fn(pkg, version)
        # async with self.lock.reader:
        if key in self.process:
            if self.process[key].is_running():
                self.process.move_to_end(key)
                logger.debug(f"process {key} is exist and running")
                return self.process[key], False
        # async with self.lock.writer:
        if key in self.process:
            logger.info(f"process {key} is not running, removing")
            del self.process[key]
        logger.debug(f"process {key} is starting")
        p = ProcessWorker(pkg, version, addr, SockHandler())
        if len(self.process) >= self.max_process:
            oldKey, oldP = self.process.popitem(False)
            logger.info(f"process {oldKey} is limited: {self.max_process}, removing")
            del oldP
        self.process[key] = p
        return p, True

    def stop_process(self, pkg, version):
        key = self.key_fn(pkg, version)
        if key in self.process:
            del self.process[key]

default_manager = ProcessManager(load().max_subprocess)


# @lru_cache(maxsize=load().max_subprocess)
# def get_process_worker(pkg, version) -> ProcessWorker:
#     # addr = f"{BASE_DIR}/run/hiagent.{pkg}.{version}.sock"
#     addr = f"/tmp/hiagent.{pkg}.{version}.sock"
#     return ProcessWorker(pkg, version, addr, SockHandler())


async def get_process_worker(pkg, version) -> Tuple[ProcessWorker, bool]:
    # addr = f"{BASE_DIR}/run/hiagent.{pkg}.{version}.sock"
    addr = f"/tmp/hiagent.{pkg}.{version}.sock"
    return await default_manager.ensure_process(pkg, version, addr)


async def run_plugin_tool(pkg: str, plugin: str, version: str, tool: str, input: Any, cfg: dict | None) -> Any:
    p, new = await get_process_worker(pkg, version)
    if new:
        fn = request_with_retry
    else:
        fn = request
    return await fn(p.addr, RunToolReq(plugin=plugin, tool=tool, input=input, config=cfg))

async def run_plugin_tool_stream(pkg: str, plugin: str, version: str, tool: str, input: Any, cfg: dict | None, stream: bool = False) -> AsyncGenerator[Any, None]:
    p, new = await get_process_worker(pkg, version)
    fn = request_stream
    if new:
        # wait for bootstrap
        # bootstrap_wait = bootstrap_retry(request)
        await request_with_retry(p.addr, RunPingReq(plugin=plugin))
    # async for ret in fn(p.addr, RunToolStreamReq(plugin=plugin, tool=tool, input=input, config=cfg)):
    #     yield ret
    return fn(p.addr, RunToolStreamReq(plugin=plugin, tool=tool, input=input, config=cfg))

async def run_plugin_registry(pkg: str, plugin: str, version: str) -> PluginMeta:
    p, new = await get_process_worker(pkg, version)
    if new:
        fn = request_with_retry
    else:
        fn = request
    return await fn(p.addr, RunMetadataReq(plugin=plugin))


async def run_pkg_metadata(pkg: str, version: str) -> List[Metadata]:
    p, new = await get_process_worker(pkg, version)
    if new:
        fn = request_with_retry
    else:
        fn = request
    res = await fn(p.addr, RunPkgMetadataReq())
    ret = []
    for item in res:
        ret.append(Metadata(**item))
    return ret


async def run_plugin_validate(pkg: str, plugin: str, version: str, cfg: dict | None) -> None:
    p, new = await get_process_worker(pkg, version)
    if new:
        fn = request_with_retry
    else:
        fn = request
    return await fn(p.addr,  RunValidateReq(plugin=plugin, config=cfg))

# bootstrap_retry = partial(retry, tries=8, delay=0.2)

@retry(tries=load().start_process_max_retries, delay=load().start_process_retry_delay)
async def request_with_retry(addr, req: BaseModel) -> Any:
    # logger.debug("request_with_retry")
    return await request(addr, req)

async def request(addr, req: BaseModel) -> Any:
    reader, writer = await asyncio.open_unix_connection(addr)
    data = req.model_dump_json()
    secretLogger.debug(f"request: {data}")
    writer.write(data.encode())
    writer.write_eof()
    await writer.drain()

    ret = await reader.read()
    resp: Resp = Resp(**json.loads(ret))
    if resp.error:
        raise HttpException(
            http_code=resp.error.http_code,
            code=resp.error.code,
            message=resp.error.message,
            data=resp.error.data
        )
    return resp.data

async def request_stream(addr, req: BaseModel) -> AsyncGenerator[Any, None]:
    reader, writer = await asyncio.open_unix_connection(addr)
    data = req.model_dump_json()
    secretLogger.debug(f"request: {data}")
    writer.write(data.encode())
    writer.write_eof()
    await writer.drain()
    # TODO(lujinghao): 客户端断开连接时, 应该停止工具的执行
    while not reader.at_eof():
        ret = await reader.readline()
        secretLogger.debug(f'response: {ret.decode("utf-8")}')
        if not ret:
            continue
        resp: Resp = Resp(**json.loads(ret))
        if resp.error:
            raise HttpException(
                http_code=resp.error.http_code,
                code=resp.error.code,
                message=resp.error.message,
                data=resp.error.data
            )
        yield resp.data

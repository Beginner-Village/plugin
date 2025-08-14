"""
每个插件使用常驻进程, 使用 socket 进行通信
"""
from typing import Any, List
import logging
import functools
import os
import asyncio
import signal
from multiprocessing import Process

from app.config import load
from app.runtime.sock_handler import SockHandler

logger = logging.getLogger(__name__)


class SocketServer:
    def __init__(self, handler):
        self.handler = handler

    def stop(self, signum):
        logging.info(f"catch: {signum}, stopping: {self.addr}")
        self.loop.create_task(self.async_stop())

    async def async_stop(self):
        logging.info(f"closing server: {self.addr}")
        self.server.close()
        await self.server.wait_closed()
        os.remove(self.addr)
        self.loop.stop()

    async def start(self, addr, loop):
        self.loop = loop
        self.addr = addr
        os.makedirs(os.path.dirname(addr), exist_ok=True)
        self.server = await asyncio.start_unix_server(self.handler, addr)
        logging.info(f"start server: {addr}")
        for signum in (signal.SIGTERM, signal.SIGINT):
            loop.add_signal_handler(
                signum, functools.partial(self.stop, signum))
        await self.server.serve_forever()


class ProcessWorker:
    def __init__(self, pkg, version, addr, handler: SockHandler):
        self.handler = handler
        self.pkg = pkg
        self.version = version
        self.addr = addr
        self.p = Process(name=f"{pkg}-{version}", target=self.worker, args=(addr, ), daemon=True)
        self.p.start()
        logger.info(f"start process {pkg}-{version}")

    def __repr__(self):
        return self.name

    @property
    def name(self) -> str:
        return self.p.name

    def is_running(self):
        return self.p.is_alive()

    def __del__(self):
        # TODO add timeout
        logger.info(f"removing process: {self.pkg}-{self.version}")
        self.p.terminate()

    def worker(self, addr):
        import sys
        package_path = load().get_package_path(self.pkg, self.version)
        sys.path.insert(0, package_path)
        s = SocketServer(self.handler.dispatch)
        self.server = s
        loop = asyncio.new_event_loop()
        loop.create_task(s.start(addr, loop))
        loop.run_forever()
        logger.info("terminated")

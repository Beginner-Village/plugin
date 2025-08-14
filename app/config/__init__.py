import logging
import yaml
import os
import asyncio
from concurrent.futures import ThreadPoolExecutor
from hiagent_plugin_sdk.extensions import Config as SDKConfig
from hiagent_plugin_sdk.extensions import setup_logger
from pathlib import Path
from rq import Queue
from functools import cache
from dotenv import load_dotenv


def get_base_dir() -> Path:
    c = os.path.dirname(os.path.abspath(__file__))
    return Path(c).parent.parent


BASE_DIR = get_base_dir()

PLUGIN_ENTRY_GROUP = "hiagent.plugins"

class Config(SDKConfig):
    """配置"""
    # model_config = ConfigDict(frozen=True)

    version: str = ""
    # 最大进程数
    max_subprocess: int = 20
    extensions_path: str = f"{BASE_DIR}/extensions"
    # 本地下载包文件路径
    local_storage_path: str = "/tmp/"
    worker_job_timeout: int = 180

    def get_package_path(self, pkg: str, version: str) -> str:
        return f"{Path(self.extensions_path) / pkg / version}"

@cache
def load() -> Config:
    """加载配置"""
    loaded = load_dotenv(f"{BASE_DIR}/.env")
    if not loaded:
        print("load .env failed")

    path = os.environ.get('CONFIG', f"{BASE_DIR}/config.yaml")
    print(f"load config from {path}, CONFIG={os.environ.get('CONFIG')}")
    try:
        with open(path, 'r') as stream:
            data_loaded = yaml.safe_load(stream)
        cfg = Config(**data_loaded)
    except Exception as e:
        print(f"load config failed: {e}")
        cfg = Config()
    setup_logger(cfg.logger)
    setup_loop()
    logging.info(f"config:\n{cfg.model_dump_json(indent=2)}")
    return cfg

def setup_loop():
    """初始化事件循环"""
    loop = asyncio.get_event_loop()
    loop.set_default_executor(ThreadPoolExecutor(max_workers=20))

@cache
def get_worker_queue(name: str = "default") -> Queue:
    """获取redis队列"""
    cfg = load()
    logging.debug(f"get_worker_queue: name {name}, timeout {cfg.worker_job_timeout} ")
    return Queue(name, connection=cfg.redis.get_redis_client(), default_timeout=cfg.worker_job_timeout)

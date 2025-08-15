import logging
import yaml
import os
from functools import cache

from dotenv import load_dotenv
from pydantic import BaseModel, ConfigDict

from hiagent_plugin_sdk.extensions.redis_cfg import RedisConfig
from hiagent_plugin_sdk.extensions.storage_cfg import StorageConfig
from hiagent_plugin_sdk.extensions.openai_cfg import OpenAIConfig
from hiagent_plugin_sdk.consts import BASE_DIR

class SSRFProxy(BaseModel):
    http_proxy: str | None = ""
    https_proxy: str | None = ""
    no_proxy: str | None = ""


class Package(BaseModel):
    index_url: str | None = ""
    extra_index_url: str | None = ""
    trusted_host: str | None = ""

class LoggerConfig(BaseModel):
    level: str|int = "INFO"
    logger_level: dict[str, str|int] = {
        "sensitive": logging.CRITICAL + 1,
    }

class Config(BaseModel):
    """配置"""
    model_config = ConfigDict(frozen=True)
    enable_sensitive_log: bool = False
    start_process_max_retries: int = 10
    start_process_retry_delay: float = 0.5
    logger: LoggerConfig = LoggerConfig()

    redis: RedisConfig = RedisConfig()
    storage: StorageConfig = StorageConfig()
    package: Package = Package()
    openai: OpenAIConfig = OpenAIConfig()
    ssrf_proxy: SSRFProxy = SSRFProxy()

@cache
def load() -> Config:
    """加载配置"""
    env_path = BASE_DIR / ".env"
    loaded = load_dotenv(env_path)
    print(f"load .env from {env_path}")
    if not loaded:
        print("load .env failed")

    config_path = os.getenv('CONFIG', BASE_DIR / "config.yaml")
    print(f"load config from {config_path}")
    try:
        with open(config_path, 'r') as stream:
            data_loaded = yaml.safe_load(stream)
        cfg = Config(**data_loaded)
    except Exception as e:
        print(f"load config failed: {e}")
        cfg = Config()
        raise e
    setup_logger(cfg.logger)
    logging.info(f"config:\n{cfg.model_dump_json(indent=2)}")
    return cfg

@cache
def setup_ssrf_proxy_env():
    """设置 ssrf 代理环境变量"""
    cfg = load()
    ssrf_cfg = cfg.ssrf_proxy
    if ssrf_cfg.http_proxy:
        os.environ["HTTP_PROXY"] = ssrf_cfg.http_proxy
    if ssrf_cfg.https_proxy:
        os.environ["HTTPS_PROXY"] = ssrf_cfg.https_proxy
    if ssrf_cfg.no_proxy:
        os.environ["NO_PROXY"] = ssrf_cfg.no_proxy

def setup_logger(cfg: LoggerConfig):
    """初始化日志"""
    logging.basicConfig(
        level=cfg.level,
        format='[%(levelname)-.1s] %(asctime)s %(processName)s %(filename)s:%(lineno)d: %(message)s',
        datefmt='%Y-%m-%dT%H:%M:%S',
    )
    for name, level in cfg.logger_level.items():
        logging.getLogger(name).setLevel(level)

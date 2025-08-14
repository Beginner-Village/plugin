
from typing import Tuple, Any, Callable, AsyncGenerator
from contextlib import asynccontextmanager
import yaml
from dataclasses import dataclass
import inspect
import logging
import aiohttp
import asyncio
import time
import threading
from pydantic import BaseModel, RootModel, create_model, ConfigDict
from hiagent_plugin_sdk.extensions import load

logger = logging.getLogger(__name__)

@dataclass
class ArgsField:
    name: str
    anno: type | None = None
    default: Any = ...

class NullModel(RootModel):
    root: None

def get_fn_schema(fn: Callable, cls = None, ignore_return_not_set=True) -> Tuple[type[BaseModel], type[RootModel]]:
    skip_first_arg = False
    if cls:
        if type(cls.__dict__.get(fn.__name__)) != staticmethod:
            skip_first_arg = True
    arg_spec = inspect.getfullargspec(fn)
    # check if fn has fully annotated
    if arg_spec.annotations is None:
        raise ValueError('fn must be fully annotated')
    if 'return' not in arg_spec.annotations and not ignore_return_not_set:
        raise ValueError('fn must have return annotated')
    return_type = arg_spec.annotations.get('return', None)
    fields: dict[str, ArgsField] = {}
    cfg = ConfigDict()
    # set args
    for arg in arg_spec.args[skip_first_arg:]:
        fields[arg] = ArgsField(name=arg)
    for arg in arg_spec.kwonlyargs:
        fields[arg] = ArgsField(name=arg)
    if arg_spec.varargs:
        raise ValueError('fn must not have varargs')
    if arg_spec.varkw:
        cfg["extra"] = 'allow'
    # set anno
    for k, v in arg_spec.annotations.items():
        # ignore return and kwargs
        if k == 'return' or k == arg_spec.varkw:
            continue
        fields[k].anno = v
    # set default
    if arg_spec.defaults:
        for idx, item in enumerate(arg_spec.defaults):
            arg_name = arg_spec.args[idx-len(arg_spec.defaults)+len(arg_spec.args)]
            fields[arg_name].default = item
    if arg_spec.kwonlydefaults:
        for k, v in arg_spec.kwonlydefaults.items():
            fields[k].default = v
    model_fields: dict[str, Any] = {}
    for v in fields.values():
        if v.anno is None:
            raise ValueError(f'arg {v.name} must be annotated')
        model_fields[v.name] = (v.anno, v.default)
    input = create_model('InModel', __config__=cfg, **model_fields)
    if return_type is None:
        output: type[RootModel] = NullModel
    else:
        output = create_model('OutModel', __base__=RootModel, root=(return_type, ...))
    return input, output

async def run_maybe_async(fn, *args, **kwargs):
    import functools
    if asyncio.iscoroutinefunction(fn):
        return await fn(*args, **kwargs)
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, functools.partial(fn, *args, **kwargs))

def rpm_limit(max_requests_per_minute: int):
    # 计算每次请求的最小间隔时间（秒）
    interval = 60 / max_requests_per_minute
    last_request_time = 0
    lock = threading.Lock()

    def decorator(func):
        def wrapper(*args, **kwargs):
            nonlocal last_request_time
            with lock:
                # 计算当前时间与上一次请求时间的差值
                current_time = time.time()
                elapsed_time = current_time - last_request_time
                # 如果间隔时间小于最小间隔，则等待
                if elapsed_time < interval:
                    time_to_wait = interval - elapsed_time
                    time.sleep(time_to_wait)
                # 更新上一次请求时间
                last_request_time = time.time()
            # 调用原始函数
            return func(*args, **kwargs)
        return wrapper
    return decorator

@asynccontextmanager
async def arequest(method, url, headers=None, json=None, params=None, data=None, timeout_sec=None) -> AsyncGenerator[aiohttp.ClientResponse, None]:
    async with aiohttp.ClientSession(trust_env=True, timeout=aiohttp.ClientTimeout(total=timeout_sec)) as ss:
        async with ss.request(method, url, headers=headers, json=json, params=params, data=data) as resp:
            yield resp

@asynccontextmanager
async def assrf_request(method, url, headers=None, json=None, params=None, data=None, timeout_sec=None) -> AsyncGenerator[aiohttp.ClientResponse, None]:
    ssrf_cfg = load().ssrf_proxy
    if ssrf_cfg.http_proxy:
        proxy = ssrf_cfg.http_proxy
    elif ssrf_cfg.https_proxy:
        proxy = ssrf_cfg.https_proxy
    else:
        proxy = None
    async with aiohttp.ClientSession(trust_env=True, proxy=proxy, timeout=aiohttp.ClientTimeout(total=timeout_sec)) as ss:
        async with ss.request(method, url, headers=headers, json=json, params=params, data=data) as resp:
            yield resp


"""
使用子进程来执行插件的注册函数和工具函数
"""
from fastapi import APIRouter, Body, HTTPException
from typing import Annotated, Any, Tuple, Callable
import asyncio
from app.config import BASE_DIR
from multiprocessing import Process, Manager
from multiprocessing.managers import DictProxy

def run_plugin_registry(plugin: str, version: str) -> dict:
    store = Manager().dict()
    p = Process(target=_run_plugin_registry, args=(store, plugin, version), daemon=True)
    p.start()
    p.join()
    e = store.get("exception", None)
    if e is not None:
        raise e
    return store.get("ret", {})

def run_plugin_tool(plugin: str, version: str, tool: str, input: Any, cfg: dict | None) -> Any:
    store = Manager().dict()
    p = Process(target=_run_plugin_tool, args=(store, plugin, version, tool, input, cfg), daemon=True)
    p.start()
    p.join()
    e = store.get("exception", None)
    if e is not None:
        raise e
    return store.get("ret", None)

def _run_plugin_registry(store: DictProxy,  plugin: str, version: str):
    import sys
    import importlib
    import importlib.metadata
    try:
        sys.path.append(f"{BASE_DIR / 'extensions'}/{plugin}-{version}")
        entries = importlib.metadata.entry_points(name="registry", group=f"hiagent.{plugin}.registry")
        if len(entries) == 0:
            raise HTTPException(status_code=404, detail=f"{plugin}-{version}/registry not found")
        registry_fn = entries[0].load()
        ret = registry_fn()
    except Exception as e:
        store.update(exception=e)
        raise e
    else:
        store.update(ret=ret)

# @pop_exception
def _run_plugin_tool(store: DictProxy, plugin: str, version: str, tool: str, input: Any, cfg: dict | None):
    import sys
    import importlib
    import importlib.metadata
    try:
        sys.path.append(f"{BASE_DIR / 'extensions'}/{plugin}-{version}")
        print(sys.path[-1])
        entries = importlib.metadata.entry_points(name=tool, group=f"hiagent.{plugin}.tools")
        if len(entries) == 0:
            raise HTTPException(status_code=404, detail=f"{plugin}-{version}/{tool} not found")
        print(entries)
        tool_fn = entries[0].load()
        if cfg is None:
            args = (input)
        else:
            args = (cfg, input)
        if asyncio.iscoroutinefunction(tool_fn):
            result = asyncio.run(tool_fn(args))
        else:
            result = tool_fn(args)
    except Exception as e:
        store.update(exception=e)
        raise e
    else:
        store.update(ret=result)

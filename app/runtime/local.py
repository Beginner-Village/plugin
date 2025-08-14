
"""
使用本地进程来执行插件的注册函数和工具函数
"""
from typing import Any
import asyncio
from fastapi import HTTPException
from app.config import BASE_DIR

async def run_plugin_tool(plugin: str, version: str, tool: str, input: Any, cfg: dict | None) -> Any:
    import sys
    import importlib
    import importlib.metadata
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
        result = await tool_fn(args)
    else:
        result = await asyncio.to_thread(tool_fn, args)
    return result

def run_plugin_tool_sync(plugin: str, version: str, tool: str, input: Any, cfg: dict | None) -> Any:
    import sys
    import importlib
    import importlib.metadata
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
    return result

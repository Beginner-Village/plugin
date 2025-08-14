from typing import Annotated, Any, AsyncGenerator
import logging
import json
from fastapi import Body, Query, Header, Request
from sse_starlette.sse import EventSourceResponse

from app.schema.common import CommonResponse, HttpError
from app.api.v1.common import api_v1
import app.runtime.sock_client as runtime

@api_v1.post("/RunPluginTool")
async def run_plugin_tool(
    pkg: Annotated[str, Body(embed=True)],
    version: Annotated[str, Body(embed=True)],
    plugin: Annotated[str, Body(embed=True)],
    tool: Annotated[str, Body(embed=True)],
    input: Annotated[dict, Body(embed=True)] = {},
    cfg: Annotated[dict | None, Body(embed=True)] = None,
    stream: Annotated[bool, Body(embed=True)] = False,
) -> CommonResponse[Any]:
    """
    执行插件的工具
    """
    # logging.debug(f"call {pkg}{version}/{plugin}/{tool}: {input} {cfg}")
    if stream:
        g = await runtime.run_plugin_tool_stream(pkg, plugin, version, tool, input, cfg)
        return EventSourceResponse(g) # type: ignore
    ret = await runtime.run_plugin_tool(pkg, plugin, version, tool, input, cfg)
    return CommonResponse(data=ret)

@api_v1.post("/RunPluginToolAdapterRuntime")
async def run_plugin_tool_adapter_runtime(
    pkg: Annotated[str, Query(embed=True)],
    version: Annotated[str, Query(embed=True)],
    plugin: Annotated[str, Query(embed=True)],
    tool: Annotated[str, Query(embed=True)],
    input: Annotated[dict, Body()] = {},
    cfg: Annotated[str, Header(embed=True)] = "",
) -> CommonResponse[Any]:
    """
    执行插件的工具, runtime 调用, input schema 需要和 body 对齐
    """
    cfg_dict = json.loads(cfg) if cfg else None
    # logging.debug(f"call {pkg}{version}/{plugin}/{tool}: {input} {cfg_dict}")
    stream = input.pop("stream", False)
    if stream:
        g = await runtime.run_plugin_tool_stream(pkg, plugin, version, tool, input, cfg_dict)
        return EventSourceResponse(g) # type: ignore
    ret = await runtime.run_plugin_tool(pkg, plugin, version, tool, input, cfg_dict)
    return CommonResponse(data=ret)

@api_v1.post("/RunPluginValidate")
async def run_plugin_validate(
    pkg: Annotated[str, Body(embed=True)],
    version: Annotated[str, Body(embed=True)],
    plugin: Annotated[str, Body(embed=True)],
    cfg: Annotated[Any | None, Body(embed=True)] = None,
) -> CommonResponse[None]:
    """
    校验插件配置
    """
    # logging.debug(f"call {pkg}{version}/{plugin}: {cfg}")
    await runtime.run_plugin_validate(pkg, plugin, version, cfg)
    return CommonResponse(data=None)

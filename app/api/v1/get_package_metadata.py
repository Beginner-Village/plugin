from typing import Annotated, List
from fastapi import Body
import aiofile
import base64
from urllib.parse import urlparse
from pydantic import BaseModel

from app.schema.common import CommonResponse, HttpError, HttpException
from app.schema.plugin import PluginMeta
from app.api.v1.common import api_v1
import app.runtime.sock_client as runtime
from hiagent_plugin_sdk.schema import Metadata

@api_v1.post("/GetPackageMetadata")
async def get_package_metadata(
    pkg: Annotated[str, Body(embed=True)],
    version: Annotated[str, Body(embed=True)],
) -> CommonResponse[List[Metadata]]:
    """获取插件元数据"""
    ret =  await runtime.run_pkg_metadata(pkg, version)
    return CommonResponse(data=ret)

class PluginIcon(BaseModel):
    filename: str
    content: str

@api_v1.post("/GetPluginIcon")
async def get_package_plugin_icon(
    pkg: Annotated[str, Body(embed=True)],
    version: Annotated[str, Body(embed=True)],
    plugin: Annotated[str, Body(embed=True)],
) -> CommonResponse[PluginIcon]:
    """获取插件icon"""
    ret =  await runtime.run_pkg_metadata(pkg, version)
    for p in ret:
        if p.name == plugin:
            plg = p
            break
    else:
        raise HttpException(code="PluginNotFound", message=f"plugin {plugin} not found")
    ext = plg.icon.split(".")[-1]
    parsed_url = urlparse(plg.icon)
    if parsed_url.scheme != "file":
        raise HttpException(code="PluginIconError", message=f"plugin {plugin} icon {plg.icon} is not file")
    async with aiofile.async_open(parsed_url.path, "rb") as f:
        data = await f.read()
    content = base64.b64encode(data).decode("utf-8")
    return CommonResponse(data=PluginIcon(filename=f"icon.{ext}", content=content))

from pydantic import BaseModel
from typing import List, Any
from hiagent_plugin_sdk.schema import Metadata


class PackageMetaBrief(BaseModel):
    name: str
    version: str
    uri: str
    filename: str

class PackageMetaBriefWithEntry(PackageMetaBrief):
    plugins: List[str] = []

class ToolMeta(BaseModel):
    name: str
    labels: dict[str, Any] = {}
    description: str
    input_schema: dict
    output_schema: dict


class PluginMeta(BaseModel):
    name: str
    category: str = ""
    class_name: str
    labels: dict[str, Any] = {}
    description: str
    icon_uri: str
    tools: dict[str, ToolMeta]
    config_required: bool
    config_schema: dict


class PackageMeta(BaseModel):
    name: str
    version: str
    uri: str
    filename: str
    plugins: List[Metadata] = []

from typing import Any, Callable, List
from pydantic import BaseModel, Field
from functools import wraps
import yaml
import logging
import traceback
from jsonpath_ng import jsonpath, parse  # type: ignore
from hiagent_plugin_sdk.utils import get_fn_schema
from hiagent_plugin_sdk.llm import try_translate
from hiagent_plugin_sdk.consts import *

logger = logging.getLogger(__name__)

class ServerSentEvent(BaseModel):
    event: str | None = None
    data: str | None = None
    id: str | None = None
    retry: int | None = None

class Labels(BaseModel):
    name_en: str | None = None
    name_zh_hans: str | None = None
    name_zh_hant: str | None = None

    description_en: str | None = None
    description_zh_hans: str | None = None
    description_zh_hant: str | None = None


class PackageInfo(BaseModel):
    name: str = Field("", description="包名")
    version: str = Field("", description="包版本")

class ToolMetadata(BaseModel):
    name: str = Field(description="工具名称")
    description: str = Field(description="工具描述")
    labels: Labels = Labels()
    input_schema: dict = {}
    output_schema: dict = {}
    func_name: str | None = None
    stream_func_name: str | None = None
    runtime_features: List[str] = []

class Metadata(BaseModel):
    meta_version: str = Field(description="元数据版本")
    name: str = Field(description="插件名称")
    category: str = Field(description="插件分类")
    description: str = Field("", description="插件描述")
    icon: str = Field("", description="插件图标")
    metadata_path: str = Field(description="元数据文件路径")
    labels: Labels = Labels()
    config_schema: dict = {}
    package_info: PackageInfo = PackageInfo(
        name="", version="",
        # config_validate_entry_point=None,
    )
    tools: dict[str, ToolMetadata] = {}


class HttpError(BaseModel):
    code: str
    message: str
    data: dict[str, Any] | None = None
    http_code: int = 500

    def __repr__(self):
        return f"{self.code}: {self.message}"

    @classmethod
    def from_exception(cls, e: Exception) -> "HttpError":
        traceback.print_exc()
        logger.info(f"from_exception: {e}, is HttpException: {isinstance(e, HttpException)}")
        if isinstance(e, HttpException):
            return HttpError(
                code=e.code,
                message=e.message,
                data=e.data,
                http_code=e.http_code,
            )
        from pydantic import ValidationError
        if isinstance(e, ValidationError):
            data = {}
            for error in e.errors():
                field = error["loc"][0]
                data[f"{field}"] = error["msg"]
            return HttpError(
                code=e.__class__.__name__,
                message=str(e),
                data=data,
                http_code=422,
            )
        from fastapi.exceptions import RequestValidationError
        if isinstance(e, RequestValidationError):
            data = {}
            for error in e.errors():
                field = error["loc"][0]
                data[f"{field}"] = error["msg"]
            return HttpError(
                code=e.__class__.__name__,
                message=str(e),
                data=data,
                http_code=422,
            )
        ret = HttpError(
            code=e.__class__.__name__,
            message=str(e),
            data={},
            http_code=500,
        )
        logger.info(f"from_exception ret: {ret.code, ret.message}")
        return ret

class HttpException(Exception):
    def __init__(self, code: str, message: str, data: dict[str, Any] | None = None, http_code: int = 500):
        self.code = code
        self.message = message
        self.data = data
        self.http_code = http_code
        super().__init__(f"{code}: {message}")


    @classmethod
    def from_exception(cls, e: Exception) -> "HttpException":
        traceback.print_exc()
        logger.info(f"from_exception: {e}, is HttpError: {isinstance(e, HttpException)}")
        if isinstance(e, HttpException):
            return e
        ret = HttpException(
            code=e.__class__.__name__,
            message=str(e),
            data={},
            http_code=500,
        )
        logger.info(f"from_exception ret: {ret.code, ret.message}")
        return ret


def try_get_value(data: dict, path: str) -> Any:
    expr = parse(path)
    try:
        ret = expr.find(data)[0].value
        return ret
    except Exception as e:
        logger.error(f"get value from data via {path} failed: {e}")
        return None


def translate_if_not_get_value(text: str, data: dict, path: str, lang: str, limit: int) -> Any:
    logger.debug(f"translate {text} to {lang}")
    if text == "":
        return ""
    v = try_get_value(data, path)
    if not v:
        return try_translate(text, lang, limit)
    return v


def complete_metadata(path: str, meta: Metadata):
    logger.debug(f"complete metadata: {path}")
    import os
    if os.path.exists(path):
        with open(path, 'r') as f:
            data = yaml.safe_load(f)
    else:
        data = {}
    text = meta.name
    meta.labels.name_en = meta.labels.name_en or translate_if_not_get_value(
        text, data, "$.labels.name_en", "en", 128)
    meta.labels.name_zh_hans = meta.labels.name_zh_hans or translate_if_not_get_value(
        text, data, "$.labels.name_zh_hans", "zh_hans", 128)
    meta.labels.name_zh_hant = meta.labels.name_zh_hant or translate_if_not_get_value(
        text, data, "$.labels.name_zh_hant", "zh_hant", 128)
    logger.debug(f"complete metadata labels: {meta.labels}")

    text = meta.description
    meta.labels.description_en = meta.labels.description_en or translate_if_not_get_value(
        text, data, "$.labels.description_en", "en", 500)
    meta.labels.description_zh_hans = meta.labels.description_zh_hans or translate_if_not_get_value(
        text, data, "$.labels.description_zh_hans", "zh_hans", 500)
    meta.labels.description_zh_hant = meta.labels.description_zh_hant or translate_if_not_get_value(
        text, data, "$.labels.description_zh_hant", "zh_hant", 500)

    complete_json_schema(data, "$.config_schema", meta.config_schema)

    for k, tool in meta.tools.items():
        complete_json_schema(
            data, f"$.tools.{k}.input_schema", tool.input_schema)
        complete_json_schema(
            data, f"$.tools.{k}.output_schema", tool.output_schema)
        text = tool.name
        tool.labels.name_en = tool.labels.name_en or translate_if_not_get_value(
            text, data, f"$.tools.{k}.labels.name_en", "en", 128)
        tool.labels.name_zh_hans = tool.labels.name_zh_hans or translate_if_not_get_value(
            text, data, f"$.tools.{k}.labels.name_zh_hans", "zh_hans", 128)
        tool.labels.name_zh_hant = tool.labels.name_zh_hant or translate_if_not_get_value(
            text, data, f"$.tools.{k}.labels.name_zh_hant", "zh_hant", 128)
        text = tool.description
        tool.labels.description_en = tool.labels.description_en or translate_if_not_get_value(
            text, data, f"$.tools.{k}.labels.description_en", "en", 500)
        tool.labels.description_zh_hans = tool.labels.description_zh_hans or translate_if_not_get_value(
            text, data, f"$.tools.{k}.labels.description_zh_hans", "zh_hans", 500)
        tool.labels.description_zh_hant = tool.labels.description_zh_hant or translate_if_not_get_value(
            text, data, f"$.tools.{k}.labels.description_zh_hant", "zh_hant", 500)


def complete_json_schema(data: dict, path: str, meta: dict):
    extra = {}
    for k, v in meta.items():
        if k == "type":
            continue
        if k == "description":
            if not v:
                continue
            text = v
            val = try_get_value(data, f"{path}.{EXT_DESC_EN}")
            if not val:
                extra[EXT_DESC_EN] = try_translate(text, "en", 500)
            else:
                extra[EXT_DESC_EN] = val
            val = try_get_value(data, f"{path}.{EXT_DESC_ZH_HANS}")
            if not val:
                extra[EXT_DESC_ZH_HANS] = try_translate(
                    text, "zh_hans", 500)
            else:
                extra[EXT_DESC_ZH_HANS] = val
            val = try_get_value(data, f"{path}.{EXT_DESC_ZH_HANT}")
            if not val:
                extra[EXT_DESC_ZH_HANT] = try_translate(
                    text, "zh_hant", 500)
            else:
                extra[EXT_DESC_ZH_HANT] = val
            continue
        if k == "properties":
            for kk, vv in v.items():
                complete_json_schema(data, f"{path}.{k}.{kk}", vv)
            continue
        if k == "$defs":
            for kk, vv in v.items():
                complete_json_schema(data, f'{path}."$defs".{kk}', vv)
            continue
        if k == "items":
            complete_json_schema(data, f"{path}.{k}[0]", v)
            continue
        if k == "title":
            continue
        if k == "required":
            continue
        if k == "enum":
            continue
        if k == "default":
            continue
        if k == "const":
            continue
        if k == "minimum":
            continue
    meta.update(**extra)

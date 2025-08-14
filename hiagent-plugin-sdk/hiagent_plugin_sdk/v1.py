from typing import List, Any, Sequence
from functools import cache
import logging
import yaml
from functools import partial
from abc import ABC, abstractmethod
from dataclasses import dataclass

from pydantic import Field, BaseModel, RootModel, create_model

from hiagent_plugin_sdk.schema import Metadata, PackageInfo, ToolMetadata, complete_metadata, HttpError
from hiagent_plugin_sdk.utils import get_fn_schema, run_maybe_async
from hiagent_plugin_sdk.consts import *
from hiagent_plugin_sdk.abc import AdapterRuntime

logger = logging.getLogger(__name__)

SecretField = partial(Field, json_schema_extra={EXT_SECRET: True})

META_STREAM_FN = "stream_fn"
META_FEAT_RUNTIME_INTENTION = "feat_runtime_intention"

class ConfigValidateMixin(ABC):
    @abstractmethod
    async def _validate(self):
        """
        Validate the plugin.
        """
        pass


class BasePlugin(AdapterRuntime, ABC):
    meta_version = "v1"
    hiagent_tools: List[str]
    hiagent_category: str

    @classmethod
    @abstractmethod
    def _icon_uri(cls) -> str:
        """
        Return the URI of the icon for the plugin.
        eg: file:///home/user/icon.svg
        eg: https://example.com/icon.svg
        """
        pass

    @classmethod
    def _read_metadata_via_pkg(cls) -> Metadata | None:
        file_path = metadata_filename(cls)
        from importlib import resources
        try:
            content = resources.read_text(cls.__module__, file_path)
            data = yaml.safe_load(content)
            return Metadata(**data)
        except Exception as e:
            logger.error(f"read metadata file failed: {e}")
            return None

    @classmethod
    @cache
    def _get_metadata(cls) -> Metadata:
        # read metadata file first
        meta = cls._read_metadata_via_pkg()
        if not meta:
            meta = cls._build_metadata()
        # override icon_url
        meta.icon = cls._icon_uri()
        return meta

    @classmethod
    def _build_metadata(cls) -> Metadata:
        # generate metadata
        lb = get_meta(cls)
        name = lb.get("cn_name", cls.__name__)
        desc = cls.__doc__ or ""
        desc = desc.strip()
        meta = Metadata(
            metadata_path=metadata_filename(cls),
            meta_version=cls.meta_version,
            name=name,
            category=getattr(cls, "hiagent_category", ""),
            description=desc,
            icon=cls._icon_uri(),
            config_schema={},
            package_info=PackageInfo(
                name=cls.__module__, version="",
                # config_validate_entry_point=None,
            ),
            tools={},
        )
        if hasattr(cls, "__init__") and hasattr(cls.__init__, "__code__"):
            if cls.__init__.__code__.co_argcount > 0:
                config_model: type[BaseModel]
                config_model, _ = get_fn_schema(
                    cls.__init__, cls, ignore_return_not_set=True)
                meta.config_schema = config_model.model_json_schema()
        for tool_name in cls.hiagent_tools:
            if not hasattr(cls, tool_name):
                raise ValueError(f"tool {tool_name} not implemented")
            tool_fn = getattr(cls, tool_name)
            lb = get_meta(tool_fn)
            desc = tool_fn.__doc__ or ""
            desc = desc.strip()
            # logger.debug(f"lb: {lb}")
            tool_meta = ToolMetadata(
                name=tool_name,
                func_name=tool_name,
                stream_func_name=lb.get(META_STREAM_FN, None),
                description=desc,
                input_schema={},
                output_schema={},
            )
            if lb.get(META_FEAT_RUNTIME_INTENTION, False) == True:
                tool_meta.runtime_features.append("agent_intention")
            if tool_meta.stream_func_name is not None:
                tool_meta.runtime_features.append("stream")
            input_model: type[BaseModel]
            output_model: type[RootModel]
            input_model, output_model = get_fn_schema(tool_fn, cls)
            output_resp_model = create_model('OutputRespModel', data=(
                output_model, None), error=(HttpError, None))
            tool_meta.input_schema, tool_meta.output_schema = input_model.model_json_schema(
            ), output_resp_model.model_json_schema()
            meta.tools[tool_name] = tool_meta
        return meta

    @classmethod
    def _gen_metadata(cls):
        meta = cls._build_metadata()
        module_root = cls.__module__.split(".")[0]
        filename = metadata_filename(cls)
        local_path = f"{module_root}/{filename}"
        complete_metadata(local_path, meta)
        with open(local_path, "w") as f:
            meta_dict = meta.model_dump(exclude_none=True)
            yaml.dump(meta_dict, f, encoding="utf-8", allow_unicode=True)

    @classmethod
    def get_metadata(cls) -> Metadata:
        return cls._get_metadata()

    @classmethod
    async def run_plugin_tool(cls, tool: str, input: dict, cfg: dict | None) -> Any:
        """
        Run the plugin tool.
        """
        meta = cls._get_metadata()
        tool_meta = meta.tools.get(tool, None)
        if tool_meta is None:
            raise ValueError(f"tool {tool} not found")
        if not tool_meta.func_name:
            raise ValueError(f"tool {tool} func_name not found")

        if cfg is not None:
            ins: BasePlugin = cls(**cfg)
        else:
            ins = cls()
        tool_fn = getattr(ins, tool_meta.func_name, None)
        if not tool_fn:
            raise ValueError(f"tool {tool} not implemented")
        return await run_maybe_async(tool_fn, **input)

    @classmethod
    def run_plugin_tool_stream(cls, tool: str, input: dict, cfg: dict | None) -> Any:
        """
        Run the plugin tool stream.
        """
        meta = cls._get_metadata()
        tool_meta = meta.tools.get(tool, None)
        if tool_meta is None:
            raise ValueError(f"tool {tool} not found")
        if not tool_meta.stream_func_name:
            raise ValueError(f"tool {tool} not support stream")

        if cfg is not None:
            ins: BasePlugin = cls(**cfg)
        else:
            ins = cls()
        stream_fn = getattr(ins, tool_meta.stream_func_name, None)
        if not stream_fn:
            raise ValueError(f"tool {tool} stream not implemented")
        return stream_fn(**input)

    @classmethod
    async def run_plugin_validate(cls, cfg: dict | None) -> Any:
        """
        Validate the plugin.
        """
        if cfg is None:
            cfg = {}
        if isinstance(cls, ConfigValidateMixin):
            return await run_maybe_async(cls._validate, **cfg)


def metadata_filename(cls) -> str:
    lb = get_meta(cls)
    name = lb.get("cn_name", cls.__name__)
    return f"{name}_metadata.yaml"


def set_meta(*,
    cn_name: str = "",
    en_name: str = "",
):
    """
    Set the meta data of the plugin.
    """
    def wrapper(inner):
        setattr(inner, META_PREFIX + "cn_name", cn_name)
        setattr(inner, META_PREFIX + "en_name", en_name)
        return inner
    return wrapper

def set_tool_meta(*,
    stream_fn: str = "",
    feat_runtime_intention: bool,
):
    def wrapper(inner):
        setattr(inner, META_PREFIX + META_STREAM_FN, stream_fn)
        setattr(inner, META_PREFIX + META_FEAT_RUNTIME_INTENTION, feat_runtime_intention)
        return inner
    return wrapper

def get_meta(obj) -> dict[str, Any]:
    """
    Get the meta data of the plugin.
    """
    meta = {}
    for attr_name in dir(obj):
        if not attr_name.startswith(META_PREFIX):
            continue
        k = attr_name.removeprefix(META_PREFIX)
        v = getattr(obj, attr_name)
        meta[k] = v
    return meta


@dataclass
class BuiltinCategory:
    # 网页搜索
    WebSearch: str = "WebSearch"
    # 工具效率
    Productivity: str = "Productivity"
    # 文本处理
    TextProcessing: str = "TextProcessing"
    # 图像处理
    ImageProcessing: str = "ImageProcessing"
    # 语音视频
    AudioVideo: str = "AudioVideo"
    # 生活助手
    LifeAssistant: str = "LifeAssistant"
    # 科学教育
    Education: str = "Education"
    # 新闻阅读
    News: str = "News"
    # 游戏娱乐
    Entertainment: str = "Entertainment"
    # 物流
    Logistics: str = "Logistics"

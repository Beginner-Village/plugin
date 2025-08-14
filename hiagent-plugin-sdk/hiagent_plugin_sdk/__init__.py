import logging
from hiagent_plugin_sdk.v1 import BasePlugin, ConfigValidateMixin, set_meta, set_tool_meta, SecretField, BuiltinCategory
from hiagent_plugin_sdk.utils import arequest, assrf_request
from hiagent_plugin_sdk.extensions import setup_ssrf_proxy_env

secretLogger = logging.getLogger("sensitive")

from typing import Annotated
import os
from pathlib import Path
from pydantic import Field
from hiagent_plugin_sdk import BasePlugin, set_meta, BuiltinCategory, setup_ssrf_proxy_env
from hiagent_plugin_webscraper.third_party.dify.web_reader_tool import get_url

current_dir = Path(os.path.dirname(os.path.abspath(__file__)))
default_ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.1000.0 Safari/537.36"

@set_meta(cn_name="网页抓取", en_name="WebScraper")
class WebscraperPlugin(BasePlugin):
    """一个用于抓取网页的工具。支持 html, pdf"""
    hiagent_tools = ["get_url"]
    hiagent_category = BuiltinCategory.WebSearch


    @classmethod
    def _icon_uri(cls) -> str:
        return f"file://{current_dir}/icon.png"

    def get_url(self,
        url: Annotated[str, Field(description="访问的 url 地址")],
        user_agent: Annotated[str, Field(description="访问标识")] = default_ua,
    ) -> str:
        """A tool for scraping webpages. Input should be a URL. support html, pdf"""
        setup_ssrf_proxy_env()
        if user_agent == "":
            user_agent = default_ua
        return get_url(url, user_agent)

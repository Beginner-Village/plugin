
from typing import List, Annotated
import os
import logging
from datetime import datetime
import pytz
import json
from pathlib import Path
from pydantic import Field
from hiagent_plugin_sdk import BasePlugin, set_meta, SecretField, BuiltinCategory, arequest
from hiagent_plugin_taopiaopiao.sign import sign_top_request
from hiagent_plugin_taopiaopiao.movieandshow import FilmOpenShowNowAndSoonGetResponse, RespWrapper

logger = logging.getLogger(__name__)
current_dir = Path(os.path.dirname(os.path.abspath(__file__)))

class APIErrCode(Exception):
    def __init__(self, code: str, message: str):
        self.code = code
        self.message = message
        super().__init__(f"API error: code={code}, message={message}")

@set_meta(cn_name="淘票票")
class TaopiaopiaoPlugin(BasePlugin):
    """用户通过输入页码和页大小这两个参数，可以访问淘票票的影片信息库，获取正在上映或即将上映的影片。"""

    hiagent_tools = ["GetMovieAndShow"]
    hiagent_category = BuiltinCategory.Entertainment

    def __init__(self,
        app_key: Annotated[str, Field(description="申请说明: <https://work.open.taobao.com/workspace-home>")],
        app_secret: Annotated[str, SecretField()],
    ):
        self.app_key = app_key
        self.app_secret = app_secret

    @classmethod
    def _icon_uri(cls) -> str:
        return f"file://{current_dir}/icon.png"

    # https://open.taobao.com/api.htm?docId=69004&docType=2&scopeId=30349
    async def GetMovieAndShow(self,
        page_index: Annotated[int, Field(1, description="页码，从1开始")] = 1,
        page_size: Annotated[int, Field(10, description="页大小，取值范围[1-100]")] = 10,
    ) -> FilmOpenShowNowAndSoonGetResponse:
        """获取正在上映/即将上映的影片/演出，注意：无法搜索过去的、已下映的影片。"""
        # "2024-11-30 11:36:00"
        timestamp = datetime.now(pytz.timezone("Asia/Shanghai")).strftime("%Y-%m-%d %H:%M:%S")
        common_params = {
            "method": "taobao.film.open.show.nowandsoon.get",
            "timestamp": timestamp,
            "v": "2.0",
            "app_key": self.app_key,
            "sign_method": "md5",
            "format": "json",
        }
        biz_params = {
            "platform": 1,
            "page_index": page_index,
            "page_size": page_size,
        }
        params: dict[str, int | str] = {**common_params, **biz_params}
        sign = sign_top_request(params, self.app_secret, "md5")
        params["sign"] = sign
        url = "https://eco.taobao.com/router/rest"
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        async with arequest("GET", url, params=params, headers=headers) as resp:
            ret_text =  await resp.text()
        ret_dict = json.loads(ret_text)
        # print(json.dumps(ret_dict, indent=2, ensure_ascii=False))
        data = RespWrapper(**ret_dict).film_open_show_nowandsoon_get_response
        if data.return_code != "0":
            raise APIErrCode(data.return_code, data.error_response)
        return data

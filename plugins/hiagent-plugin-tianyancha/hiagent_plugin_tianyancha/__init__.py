
from typing import List, Annotated
import os
from pathlib import Path
from pydantic import Field
from yarl import Query
from hiagent_plugin_sdk import BasePlugin, set_meta, SecretField, BuiltinCategory, arequest
from hiagent_plugin_tianyancha.common import CommonResp
from hiagent_plugin_tianyancha.news import NewsResult
from hiagent_plugin_tianyancha.abnormal_operation import AbnormalOperationResult
from hiagent_plugin_tianyancha.change_log import ChangeLogResult
from hiagent_plugin_tianyancha.company_detail import CompanyDetailResult

current_dir = Path(os.path.dirname(os.path.abspath(__file__)))

class APIErrCode(Exception):
    def __init__(self, code: int, message: str):
        self.code = code
        self.message = message
        super().__init__(f"API error: code={code}, message={message}")

@set_meta(cn_name="天眼查", en_name="tianyancha")
class TianyanchaPlugin(BasePlugin):
    """利用天眼查官方API接口,以关键词检索企业列表实现企业搜索功能，并支持查询企业基本信息、新闻舆情、经营异常及变更记录等信息。"""

    hiagent_tools = ["news", "abnormal_operation", "change_log", "company_detail"]
    hiagent_category = BuiltinCategory.WebSearch

    def __init__(self, token: Annotated[str, SecretField(description="申请说明: https://open.tianyancha.com/console/mydata")]):
        self.token = token

    @classmethod
    def _icon_uri(cls) -> str:
        return f"file://{current_dir}/icon.png"

    async def _get(self, url: str, params: dict) -> dict:
        query: Query = {k: v for k, v in params.items() if v is not None}
        headers = {"Authorization": self.token}
        async with arequest("GET", url, params=query, headers=headers) as resp:
            resp.raise_for_status()
            ret = await resp.json()
        # print(json.dumps(ret, indent=2, ensure_ascii=False))
        return ret

    # https://open.tianyancha.com/open/943
    async def news(self,
        name: Annotated[str | None, Field(description="公司名称（精确匹配、name和id其一为必填即可）")] = None,
        id: Annotated[int | None, Field(description="公司id（name和id其一为必填即可）")] = None,
        pageSize: Annotated[int, Field(description="每页条数（默认20条，最大20条）")] = 20,
        pageNum: Annotated[int, Field(description="当前页数（默认第1页）")] = 1,
    ) -> NewsResult:
        """可以通过公司名称（需公司全称）或ID精确匹配获取新闻列表。"""
        url = "https://open.api.tianyancha.com/services/open/ps/news/2.0"
        params = {
            "name": name,
            "id": id,
            "pageSize": pageSize,
            "pageNum": pageNum,
        }
        ret_dict = await self._get(url, params)
        ret = CommonResp[NewsResult](**ret_dict)
        # 300000 经查无结果
        if ret.error_code == 300000:
            return NewsResult() # type: ignore
        if ret.error_code != 0:
            raise APIErrCode(ret.error_code, ret.reason)
        if ret.result is None:
            raise APIErrCode(-1, "result is None")
        return ret.result

    # https://open.tianyancha.com/open/848
    async def abnormal_operation(self,
        keyword: Annotated[str, Field(description="搜索关键字（公司名称、公司id、注册号或社会统一信用代码）")],
    ) -> AbnormalOperationResult:
        """可以通过公司名称（需公司全称）或ID获取企业经营异常信息，经营异常信息包括列入/移除原因、时间、做出决定机关等字段的详细信息。"""
        url = "https://open.api.tianyancha.com/services/open/mr/abnormal/2.0"
        params = {
            "keyword": keyword,
        }
        ret_dict = await self._get(url, params)
        ret = CommonResp[AbnormalOperationResult](**ret_dict)
        # 300000 经查无结果
        if ret.error_code == 300000:
            return AbnormalOperationResult() # type: ignore
        if ret.error_code!= 0:
            raise APIErrCode(ret.error_code, ret.reason)
        if ret.result is None:
            raise APIErrCode(-1, "result is None")
        return ret.result

    # https://open.tianyancha.com/open/822
    async def change_log(self,
        keyword: Annotated[str, Field(description="搜索关键字（公司名称、公司id、注册号或社会统一信用代码）")],
        pageSize: Annotated[int, Field(description="每页条数（默认20条，最大20条）")] = 20,
        pageNum: Annotated[int, Field(description="当前页数（默认第1页）")] = 1,
    ) -> ChangeLogResult:
        """可以通过公司名称（需公司全称）或ID获取企业变更记录，变更记录包括工商变更事项、变更前后信息等字段的详细信息。"""
        url = "https://open.api.tianyancha.com/services/open/ic/changeinfo/2.0"
        params = {
            "keyword": keyword,
            "pageSize": pageSize,
            "pageNum": pageNum,
        }
        ret_dict = await self._get(url, params)
        ret = CommonResp[ChangeLogResult](**ret_dict)
        # 300000 经查无结果
        if ret.error_code == 300000:
            return ChangeLogResult() # type: ignore
        if ret.error_code!= 0:
            raise APIErrCode(ret.error_code, ret.reason)
        if ret.result is None:
            raise APIErrCode(-1, "result is None")
        return ret.result

    # https://open.tianyancha.com/open/818
    async def company_detail(self,
        keyword: Annotated[str, Field(description="搜索关键字（公司名称、公司id、注册号或社会统一信用代码）")],
    ) -> CompanyDetailResult:
        """可以通过公司名称（需公司全称）或ID获取企业基本信息和企业联系方式，包括公司名称或ID、类型、成立日期、电话、邮箱、网址等字段的详细信息。"""
        url = "https://open.api.tianyancha.com/services/open/ic/baseinfoV2/2.0"
        params = {
            "keyword": keyword,
        }
        ret_dict = await self._get(url, params)
        ret = CommonResp[CompanyDetailResult](**ret_dict)
        # 300000 经查无结果
        if ret.error_code!= 0:
            raise APIErrCode(ret.error_code, ret.reason)
        if ret.result is None:
            raise APIErrCode(-1, "result is None")
        return ret.result

    # async def _validate(self) -> None:
    #     url = "http://open.api.tianyancha.com/services/open/ic/baseinfoV2/2.0"
    #     params = {
    #         "keyword": "validate",
    #     }
    #     query: Query = {k: v for k, v in params.items() if v is not None}
    #     headers = {"Authorization": self.token}
    #     async with arequest("HEAD", url, params=query, headers=headers) as resp:
    #         resp.raise_for_status()
    #     return None

from typing import Any, Optional, List, Dict, Annotated, Literal
import os
from pydantic import Field
from pathlib import Path
import json
from hiagent_plugin_sdk import BasePlugin, set_meta, SecretField, BuiltinCategory
import lark_oapi as lark # type: ignore
import lark_oapi.api.wiki.v2 as wiki_v2 # type: ignore
import hiagent_plugin_feishu_wiki.sdk_model as model

current_dir = Path(os.path.dirname(os.path.abspath(__file__)))

class LarkApiException(Exception):
    def __init__(self, code: int, msg: str):
        self.code = code
        self.msg = msg
        super().__init__(f"LarkApiError[{code}]: {msg}")

@set_meta(cn_name="飞书知识库")
class FeishuWikiPlugin(BasePlugin):
    """飞书知识库"""
    hiagent_tools = [
        "get_wiki_nodes"
    ]
    hiagent_category = BuiltinCategory.Productivity

    def __init__(self,
        app_id: Annotated[str, Field(description="申请链接: <https://open.larkoffice.com/app>")],
        app_secret: Annotated[str, SecretField()],
    ):
        self.app_id = app_id
        self.app_secret = app_secret
        # TODO: 缓存
        self.cli = lark.Client.builder().app_id(self.app_id).app_secret(self.app_secret).build()

    @classmethod
    def _icon_uri(cls) -> str:
        return f"file://{current_dir}/icon.png"

    # https://open.feishu.cn/document/server-docs/docs/wiki-v2/space-node/list
    async def get_wiki_nodes(self,
        space_id: Annotated[str, Field(description="知识空间id")],
        page_size: Annotated[int, Field(description="分页大小")] = 10,
        page_token: Annotated[str, Field(description="分页标记，第一次请求不填，表示从头开始遍历；")] = "",
        parent_node_token: Annotated[str, Field(description="父节点token")] = "",
    ) -> model.BaseRespModel[model.ListSpaceNodeResponseBodyModel]: # type: ignore
        """获取知识空间子节点列表"""
        req = wiki_v2.ListSpaceNodeRequest.builder().space_id(space_id).page_size(page_size).page_token(page_token).parent_node_token(parent_node_token).build()
        resp = await self.cli.wiki.v2.space_node.alist(req)
        if not resp.success():
            raise LarkApiException(resp.code, resp.msg)
        ret_dict = json.loads(resp.raw.content.decode("utf-8"))
        print(json.dumps(ret_dict, indent=2, ensure_ascii=False))
        ret =  model.BaseRespModel[model.ListSpaceNodeResponseBodyModel](**ret_dict) # type: ignore
        return ret

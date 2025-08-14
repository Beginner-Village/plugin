
from typing import Any, Optional, List, Dict, Annotated, Literal
import os
from pydantic import Field
from pathlib import Path
import json
from hiagent_plugin_sdk import BasePlugin, set_meta, SecretField, BuiltinCategory
import lark_oapi as lark # type: ignore
import lark_oapi.api.docx.v1 as doc_v1 # type: ignore
import hiagent_plugin_feishu_docx.sdk_model as model

current_dir = Path(os.path.dirname(os.path.abspath(__file__)))

class LarkApiException(Exception):
    def __init__(self, code: int, msg: str):
        self.code = code
        self.msg = msg
        super().__init__(f"LarkApiError[{code}]: {msg}")

@set_meta(cn_name="飞书云文档")
class FeishuDocxPlugin(BasePlugin):
    """飞书云文档"""
    hiagent_tools = [
        "create_document", "get_document", "get_document_content",
        "list_document_block", "create_document_block",
    ]
    hiagent_category = BuiltinCategory.Productivity

    def __init__(self,
        app_id: Annotated[str, Field(description="申请链接: <https://open.larkoffice.com/app>")],
        app_secret: Annotated[str, SecretField()],
    ):
        self.app_id = app_id
        self.app_secret = app_secret
        self.cli = lark.Client.builder().app_id(self.app_id).app_secret(self.app_secret).build()

    @classmethod
    def _icon_uri(cls) -> str:
        return f"file://{current_dir}/icon.png"

    # https://open.feishu.cn/document/server-docs/docs/docs/docx-v1/document/create
    async def create_document(self,
        folder_token: Annotated[str, Field(description="指定文档所在文件夹 的 Token。不传或传空表示根目录。")] = "",
        title: Annotated[str, Field(description="文档标题，只支持纯文本")] = "",
    ) -> model.BaseRespModel[model.CreateDocumentResponseBodyModel]: # type: ignore
        """创建文档"""
        req = doc_v1.CreateDocumentRequest.builder().request_body({
            "folder_token": folder_token,
            "title": title,
        }).build()
        resp = await self.cli.docx.v1.document.acreate(req)
        if not resp.success():
            raise LarkApiException(resp.code, resp.msg)
        ret_dict = json.loads(resp.raw.content.decode("utf-8"))
        print(json.dumps(ret_dict, indent=2, ensure_ascii=False))
        ret =  model.BaseRespModel[model.CreateDocumentResponseBodyModel](**ret_dict) # type: ignore
        return ret

    # https://open.feishu.cn/document/server-docs/docs/docs/docx-v1/document/get
    async def get_document(self,
        document_id: Annotated[str, Field(description="文档的唯一标识。")],
    ) -> model.BaseRespModel[model.GetDocumentResponseBodyModel]: # type: ignore
        """获取文档基本信息"""
        req = doc_v1.GetDocumentRequest.builder().document_id(document_id).build()
        resp = await self.cli.docx.v1.document.aget(req)
        if not resp.success():
            raise LarkApiException(resp.code, resp.msg)
        ret_dict = json.loads(resp.raw.content.decode("utf-8"))
        print(json.dumps(ret_dict, indent=2, ensure_ascii=False))
        ret =  model.BaseRespModel[model.GetDocumentResponseBodyModel](**ret_dict) # type: ignore
        return ret

    # https://open.feishu.cn/document/server-docs/docs/docs/docx-v1/document/raw_content
    async def get_document_content(self,
        document_id: Annotated[str, Field(description="文档的唯一标识。")],
        lang: Annotated[int, Field(description="""指定返回的 MentionUser 即 @用户 的语言
0：该用户的默认名称。如：@张敏
1：该用户的英文名称。如：@Min Zhang
2：暂不支持该枚举，使用时返回该用户的默认名称""")] = 0,
    ) -> model.BaseRespModel[model.RawContentDocumentResponseBodyModel]: # type: ignore
        """获取文档纯文本内容"""
        req = doc_v1.RawContentDocumentRequest.builder() \
            .document_id(document_id).lang(lang).build()
        resp = await self.cli.docx.v1.document.araw_content(req)
        if not resp.success():
            raise LarkApiException(resp.code, resp.msg)
        ret_dict = json.loads(resp.raw.content.decode("utf-8"))
        print(json.dumps(ret_dict, indent=2, ensure_ascii=False))
        ret =  model.BaseRespModel[model.RawContentDocumentResponseBodyModel](**ret_dict) # type: ignore
        return ret

    # https://open.feishu.cn/document/server-docs/docs/docs/docx-v1/document/list
    async def list_document_block(self,
        document_id: Annotated[str, Field(description="文档的唯一标识。")],
        document_revision_id: Annotated[int, Field(description="查询的文档版本，-1 表示文档最新版本。文档创建后，版本为 1。")] = -1,
        page_size: Annotated[int, Field(description="分页大小, <= 500")] = 500,
        page_token: Annotated[str, Field(description="分页标记，第一次请求不填，表示从头开始遍历")] = "",
    ) -> model.BaseRespModel[model.CreateDocumentBlockChildrenResponseBodyModel]: # type: ignore
        """获取文档所有块"""
        req = doc_v1.ListDocumentBlockRequest.builder() \
            .document_id(document_id) \
            .document_revision_id(document_revision_id) \
            .page_size(page_size).page_token(page_token) \
            .build()
        resp = await self.cli.docx.v1.document_block.alist(req)
        if not resp.success():
            raise LarkApiException(resp.code, resp.msg)
        ret_dict = json.loads(resp.raw.content.decode("utf-8"))
        print(json.dumps(ret_dict, indent=2, ensure_ascii=False))
        ret =  model.BaseRespModel[model.ListDocumentBlockResponseBodyModel](**ret_dict) # type: ignore
        return ret

    # https://open.feishu.cn/document/server-docs/docs/docs/docx-v1/document-block/create
    async def create_document_block(self,
        document_id: Annotated[str, Field(description="文档的唯一标识。")],
        block_id: Annotated[str, Field(description="父块的block_id，表示为其创建一批子块。如果需要对文档树根节点创建子块，可将 document_id 填入此处。")],
        content: Annotated[model.CreateDocumentBlockChildrenRequestBodyModel, Field(description="块内容")], # type: ignore
        client_token: Annotated[str, Field(description="操作的唯一标识，与接口返回值的 client_token 相对应，用于幂等的进行更新操作。此值为空表示将发起一次新的请求，此值非空表示幂等的进行更新操作")] = "",
        document_revision_id: Annotated[int, Field(description="查询的文档版本，-1 表示文档最新版本。文档创建后，版本为 1。")] = -1,
    ) -> model.BaseRespModel[model.CreateDocumentBlockChildrenResponseBodyModel]: # type: ignore
        """创建块"""
        req = doc_v1.CreateDocumentBlockChildrenRequest.builder() \
            .document_id(document_id).document_revision_id(document_revision_id) \
            .block_id(block_id) \
            .client_token(client_token) \
            .request_body(content) \
            .build()
        resp = await self.cli.docx.v1.document_block_children.acreate(req)
        if not resp.success():
            raise LarkApiException(resp.code, resp.msg)
        ret_dict = json.loads(resp.raw.content.decode("utf-8"))
        print(json.dumps(ret_dict, indent=2, ensure_ascii=False))
        ret =  model.BaseRespModel[model.CreateDocumentBlockChildrenResponseBodyModel](**ret_dict) # type: ignore
        return ret

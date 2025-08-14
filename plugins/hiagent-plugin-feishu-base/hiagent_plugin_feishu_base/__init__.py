
from typing import Any, Optional, List, Dict, Annotated, Literal
import os
from pydantic import Field
from pathlib import Path
import json
from hiagent_plugin_sdk import BasePlugin, set_meta, SecretField, BuiltinCategory
import lark_oapi as lark # type: ignore
import lark_oapi.api.bitable.v1 as base_v1 # type: ignore
import hiagent_plugin_feishu_base.sdk_model as model

current_dir = Path(os.path.dirname(os.path.abspath(__file__)))

class LarkApiException(Exception):
    def __init__(self, code: int, msg: str):
        self.code = code
        self.msg = msg
        super().__init__(f"LarkApiError[{code}]: {msg}")

@set_meta(cn_name="飞书多维表格")
class FeishuBasePlugin(BasePlugin):
    """飞书多维表格"""
    hiagent_tools = [
        "create_base", "get_base_info",
        "create_table", "list_table", "delete_table",
        "create_records", "update_records", "search_records", "delete_records",
    ]
    hiagent_category = BuiltinCategory.Productivity

    def __init__(self,
        app_id: Annotated[str, Field(description="申请链接: <https://open.feishu.cn/app>")],
        app_secret: Annotated[str, SecretField()],
    ):
        self.app_id = app_id
        self.app_secret = app_secret
        self.cli = lark.Client.builder().app_id(self.app_id).app_secret(self.app_secret).build()

    @classmethod
    def _icon_uri(cls) -> str:
        return f"file://{current_dir}/icon.png"

    # https://open.feishu.cn/document/server-docs/docs/bitable-v1/app/create
    async def create_base(self,
        name: Annotated[str, Field(description="多维表格 App 名称。最长为 255 个字符。")],
        folder_token: Annotated[str, Field(description="多维表格 App 归属文件夹。默认为空，表示多维表格将被创建在云空间根目录。")] = "",
    ) -> model.BaseRespModel[model.CreateAppResponseBodyModel]: # type: ignore
        """创建多维表格"""
        req = base_v1.CreateAppRequest.builder().request_body(
            base_v1.ReqApp.builder()
                .name(name)
                .folder_token(folder_token)
                .build()
        ).build()
        resp = await self.cli.bitable.v1.app.acreate(req)
        if not resp.success():
            raise LarkApiException(resp.code, resp.msg)
        ret_dict = json.loads(resp.raw.content.decode("utf-8"))
        print(json.dumps(ret_dict, indent=2, ensure_ascii=False))
        ret =  model.BaseRespModel[model.CreateAppResponseBodyModel](**ret_dict) # type: ignore
        return ret

    # https://open.feishu.cn/document/server-docs/docs/bitable-v1/app/get
    async def get_base_info(self,
        app_token: Annotated[str, Field(description="多维表格 App Token。")],
    ) -> model.BaseRespModel[model.GetAppResponseBodyModel]: # type: ignore
        """获取多维表格元数据"""
        req = base_v1.GetAppRequest.builder().app_token(app_token).build()
        resp = await self.cli.bitable.v1.app.aget(req)
        if not resp.success():
            raise LarkApiException(resp.code, resp.msg)
        ret_dict = json.loads(resp.raw.content.decode("utf-8"))
        print(json.dumps(ret_dict, indent=2, ensure_ascii=False))
        ret =  model.BaseRespModel[model.GetAppResponseBodyModel](**ret_dict) # type: ignore
        return ret

    # https://open.feishu.cn/document/server-docs/docs/bitable-v1/app-table/create
    async def create_table(self,
        app_token: Annotated[str, Field(description="多维表格 App Token。")],
        name: Annotated[str, Field(description="数据表名称。该字段必填。")],
        default_view_name: Annotated[str | None, Field(description="默认表格视图的名称，不填则默认为“表格视图 1”。")] = None,
        fields: Annotated[List[model.AppTableCreateHeaderModel], Field(description="数据表的初始字段。")] = [], # type: ignore
    ) -> model.BaseRespModel[model.CreateAppTableResponseBodyModel]: # type: ignore
        """创建数据表"""
        req_dict: Dict[str, Any] = {
            "table": {
                "name": name,
                "default_view_name": default_view_name,
                # "fields": fields,
            }
        }
        if len(fields) > 0:
            req_dict["table"]["fields"] = fields
        req = base_v1.CreateAppTableRequestBody(req_dict)
        resp = await self.cli.bitable.v1.app_table.acreate(
            base_v1.CreateAppTableRequest.builder()
                .app_token(app_token)
                .request_body(req)
                .build()
        )
        if not resp.success():
            raise LarkApiException(resp.code, resp.msg)
        ret_dict = json.loads(resp.raw.content.decode("utf-8"))
        print(json.dumps(ret_dict, indent=2, ensure_ascii=False))
        ret =  model.BaseRespModel[model.CreateAppTableResponseBodyModel](**ret_dict) # type: ignore
        return ret

    # https://open.feishu.cn/document/server-docs/docs/bitable-v1/app-table/list
    async def list_table(self,
        app_token: Annotated[str, Field(description="多维表格 App Token。")],
        page_size: Annotated[int, Field(description="分页大小")] = 10,
        page_token: Annotated[str, Field(description="分页标记，第一次请求不填，表示从头开始遍历；")] = "",
    ) -> model.BaseRespModel[model.ListAppTableResponseBodyModel]: # type: ignore
        """列出数据表"""
        resp = await self.cli.bitable.v1.app_table.alist(
            base_v1.ListAppTableRequest.builder()
                .app_token(app_token)
                .page_size(page_size)
                .page_token(page_token)
                .build()
        )
        if not resp.success():
            raise LarkApiException(resp.code, resp.msg)
        ret_dict = json.loads(resp.raw.content.decode("utf-8"))
        print(json.dumps(ret_dict, indent=2, ensure_ascii=False))
        ret =  model.BaseRespModel[model.ListAppTableResponseBodyModel](**ret_dict) # type: ignore
        return ret

    # https://open.feishu.cn/document/server-docs/docs/bitable-v1/app-table/delete
    async def delete_table(self,
        app_token: Annotated[str, Field(description="多维表格 App 的唯一标识。")],
        table_id: Annotated[str, Field(description="多维表格数据表的唯一标识。")],
    ) -> model.BaseRespModel[dict]: # type: ignore
        """删除一个数据表"""
        resp = await self.cli.bitable.v1.app_table.adelete(
            base_v1.DeleteAppTableRequest.builder()
                .app_token(app_token)
                .table_id(table_id)
                .build()
        )
        if not resp.success():
            raise LarkApiException(resp.code, resp.msg)
        ret_dict = json.loads(resp.raw.content.decode("utf-8"))
        print(json.dumps(ret_dict, indent=2, ensure_ascii=False))
        ret =  model.BaseRespModel[dict](**ret_dict) # type: ignore
        return ret

    # https://open.feishu.cn/document/server-docs/docs/bitable-v1/app-table-record/create
    async def create_records(self,
        app_token: Annotated[str, Field(description="多维表格 App 的唯一标识。")],
        table_id: Annotated[str, Field(description="多维表格数据表的唯一标识。")],
        fields_json: Annotated[str, Field(description='要新增的记录的数据。你需先指定数据表中的字段（即指定列），再传入正确格式的数据作为一条记录。比如 `{"col_1": 1, "col_2": "hello"}`')],
    ) -> model.BaseRespModel[model.CreateAppTableRecordResponseBodyModel]: # type: ignore
        """新增记录"""
        fields = json.loads(fields_json)
        resp = await self.cli.bitable.v1.app_table_record.acreate(
            base_v1.CreateAppTableRecordRequest.builder()
                .app_token(app_token)
                .table_id(table_id)
                .request_body(
                    base_v1.AppTableRecord.builder()
                        .fields(fields)
                        .build()
                )
                .build()
        )
        if not resp.success():
            raise LarkApiException(resp.code, resp.msg)
        ret_dict = json.loads(resp.raw.content.decode("utf-8"))
        print(json.dumps(ret_dict, indent=2, ensure_ascii=False))
        ret =  model.BaseRespModel[model.CreateAppTableRecordResponseBodyModel](**ret_dict) # type: ignore
        return ret

    # https://open.feishu.cn/document/server-docs/docs/bitable-v1/app-table-record/update
    async def update_records(self,
        app_token: Annotated[str, Field(description="多维表格 App 的唯一标识。")],
        table_id: Annotated[str, Field(description="多维表格数据表的唯一标识。")],
        record_id: Annotated[str, Field(description="数据表中一条记录的唯一标识。")],
        fields_json: Annotated[str, Field(description='要新增的记录的数据。你需先指定数据表中的字段（即指定列），再传入正确格式的数据作为一条记录。比如 `{"col_1": 1, "col_2": "hello"}`')],
    ) -> model.BaseRespModel[model.UpdateAppTableRecordResponseBodyModel]: # type: ignore
        """更新记录"""
        fields = json.loads(fields_json)
        resp = await self.cli.bitable.v1.app_table_record.aupdate(
            base_v1.UpdateAppTableRecordRequest.builder()
                .app_token(app_token)
                .table_id(table_id)
                .record_id(record_id)
                .request_body(
                    base_v1.AppTableRecord.builder()
                        .fields(fields)
                        .build()
                )
                .build()
        )
        if not resp.success():
            raise LarkApiException(resp.code, resp.msg)
        ret_dict = json.loads(resp.raw.content.decode("utf-8"))
        print(json.dumps(ret_dict, indent=2, ensure_ascii=False))
        ret =  model.BaseRespModel[model.UpdateAppTableRecordResponseBodyModel](**ret_dict) # type: ignore
        return ret

    # https://open.feishu.cn/document/uAjLw4CM/ukTMukTMukTM/reference/bitable-v1/app-table-record/search
    async def search_records(self,
        app_token: Annotated[str, Field(description="多维表格 App 的唯一标识。")],
        table_id: Annotated[str, Field(description="多维表格数据表的唯一标识。")],
        search: Annotated[model.SearchAppTableRecordRequestBodyModel, Field(description="查询条件。")], # type: ignore
        page_size: Annotated[int, Field(description="分页大小")] = 10,
        page_token: Annotated[str, Field(description="分页标记，第一次请求不填，表示从头开始遍历；")] = "",
    ) -> model.BaseRespModel[model.SearchAppTableRecordResponseBodyModel]: # type: ignore
        """查询记录"""
        resp = await self.cli.bitable.v1.app_table_record.asearch(
            base_v1.SearchAppTableRecordRequest.builder()
                .app_token(app_token)
                .table_id(table_id)
                .page_token(page_token)
                .page_size(page_size)
                .request_body(base_v1.SearchAppTableRecordRequestBody(search))
                .build()
        )
        if not resp.success():
            raise LarkApiException(resp.code, resp.msg)
        ret_dict = json.loads(resp.raw.content.decode("utf-8"))
        print(json.dumps(ret_dict, indent=2, ensure_ascii=False))
        ret =  model.BaseRespModel[model.SearchAppTableRecordResponseBodyModel](**ret_dict) # type: ignore
        return ret

    # https://open.feishu.cn/document/server-docs/docs/bitable-v1/app-table-record/delete
    async def delete_records(self,
        app_token: Annotated[str, Field(description="多维表格 App 的唯一标识。")],
        table_id: Annotated[str, Field(description="多维表格数据表的唯一标识。")],
        record_id: Annotated[str, Field(description="数据表中一条记录的唯一标识。")],
    ) -> model.BaseRespModel[model.DeleteAppTableRecordResponseModel]: # type: ignore
        """删除记录"""
        resp = await self.cli.bitable.v1.app_table_record.adelete(
            base_v1.DeleteAppTableRecordRequest.builder()
                .app_token(app_token)
                .table_id(table_id)
                .record_id(record_id)
                .build()
        )
        if not resp.success():
            raise LarkApiException(resp.code, resp.msg)
        ret_dict = json.loads(resp.raw.content.decode("utf-8"))
        print(json.dumps(ret_dict, indent=2, ensure_ascii=False))
        ret =  model.BaseRespModel[model.DeleteAppTableRecordResponseModel](**ret_dict) # type: ignore
        return ret

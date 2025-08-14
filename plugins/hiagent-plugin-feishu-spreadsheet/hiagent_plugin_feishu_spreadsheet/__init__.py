
from typing import Any, Optional, List, Dict, Annotated, Literal
import os
from pydantic import Field
from pathlib import Path
import json
from hiagent_plugin_sdk import BasePlugin, set_meta, SecretField, BuiltinCategory

import lark_oapi as lark # type: ignore
import lark_oapi.api.sheets.v3 as sheets_v3 # type: ignore
from lark_oapi.client import BaseRequest, BaseResponse, HttpMethod, AccessTokenType  # type: ignore

import hiagent_plugin_feishu_spreadsheet.sdk_model as model
from hiagent_plugin_feishu_spreadsheet.add_rows_or_columns import Dimension, AddRowsOrColumnsRespBody
from hiagent_plugin_feishu_spreadsheet.value_range import ValueRangeRespBody, ValueRangeUpdate, WriteValueRespBody, ValueRow

current_dir = Path(os.path.dirname(os.path.abspath(__file__)))

class LarkApiException(Exception):
    def __init__(self, code: int, msg: str):
        self.code = code
        self.msg = msg
        super().__init__(f"LarkApiError[{code}]: {msg}")

@set_meta(cn_name="飞书电子表格")
class FeishuSpreadSheetPlugin(BasePlugin):
    """飞书电子表格"""
    hiagent_tools = [
        "create_spreadsheet", "get_spreadsheet",
        "list_sheets", "get_sheet",
        "add_rows_or_columns", "read_range", "write_range",
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

    # https://open.feishu.cn/document/server-docs/docs/sheets-v3/spreadsheet/create
    async def create_spreadsheet(self,
        folder_token: Annotated[str, Field(description="文件夹 token")],
        title: Annotated[str, Field(description="表格标题")] = "",
    ) -> model.BaseRespModel[model.CreateSpreadsheetResponseBodyModel]: # type: ignore
        """创建电子表格"""
        req = sheets_v3.CreateSpreadsheetRequest.builder().request_body(
            sheets_v3.Spreadsheet.builder()
                .folder_token(folder_token)
                .title(title)
                .build()
        ).build()
        resp = await self.cli.sheets.v3.spreadsheet.acreate(req)
        if not resp.success():
            raise LarkApiException(resp.code, resp.msg)
        ret_dict = json.loads(resp.raw.content.decode("utf-8"))
        print(json.dumps(ret_dict, indent=2, ensure_ascii=False))
        ret =  model.BaseRespModel[model.CreateSpreadsheetResponseBodyModel](**ret_dict) # type: ignore
        return ret

    # https://open.feishu.cn/document/server-docs/docs/sheets-v3/spreadsheet/get
    async def get_spreadsheet(self,
        spreadsheet_token: Annotated[str, Field(description="电子表格的 token。")],
    ) -> model.BaseRespModel[model.GetSpreadsheetResponseBodyModel]: # type: ignore
        """获取电子表格信息"""
        req = sheets_v3.GetSpreadsheetRequest.builder().spreadsheet_token(spreadsheet_token).build()
        resp = await self.cli.sheets.v3.spreadsheet.aget(req)
        if not resp.success():
            raise LarkApiException(resp.code, resp.msg)
        ret_dict = json.loads(resp.raw.content.decode("utf-8"))
        print(json.dumps(ret_dict, indent=2, ensure_ascii=False))
        ret =  model.BaseRespModel[model.GetSpreadsheetResponseBodyModel](**ret_dict) # type: ignore
        return ret

    # https://open.feishu.cn/document/server-docs/docs/sheets-v3/spreadsheet-sheet/query
    async def list_sheets(self,
        spreadsheet_token: Annotated[str, Field(description="电子表格的 token。")],
    ) -> model.BaseRespModel[model.QuerySpreadsheetSheetResponseBodyModel]: # type: ignore
        """获取工作表"""
        req = sheets_v3.QuerySpreadsheetSheetRequest.builder().spreadsheet_token(spreadsheet_token).build()
        resp = await self.cli.sheets.v3.spreadsheet_sheet.aquery(req)
        if not resp.success():
            raise LarkApiException(resp.code, resp.msg)
        ret_dict = json.loads(resp.raw.content.decode("utf-8"))
        print(json.dumps(ret_dict, indent=2, ensure_ascii=False))
        ret =  model.BaseRespModel[model.QuerySpreadsheetSheetResponseBodyModel](**ret_dict) # type: ignore
        return ret

    # https://open.feishu.cn/document/server-docs/docs/sheets-v3/spreadsheet-sheet/get
    async def get_sheet(self,
        spreadsheet_token: Annotated[str, Field(description="电子表格的 token。")],
        sheet_id: Annotated[str, Field(description="电子表格的 token。")],
    ) -> model.BaseRespModel[model.GetSpreadsheetSheetResponseBodyModel]: # type: ignore
        """查询工作表"""
        req = sheets_v3.GetSpreadsheetSheetRequest.builder().spreadsheet_token(spreadsheet_token).sheet_id(sheet_id).build()
        resp = await self.cli.sheets.v3.spreadsheet_sheet.aget(req)
        if not resp.success():
            raise LarkApiException(resp.code, resp.msg)
        ret_dict = json.loads(resp.raw.content.decode("utf-8"))
        print(json.dumps(ret_dict, indent=2, ensure_ascii=False))
        ret =  model.BaseRespModel[model.GetSpreadsheetSheetResponseBodyModel](**ret_dict) # type: ignore
        return ret

    # https://open.feishu.cn/document/server-docs/docs/sheets-v3/sheet-rowcol/add-rows-or-columns
    async def add_rows_or_columns(self,
        spreadsheet_token: Annotated[str, Field(description="电子表格的 token。")],
        dimension: Annotated[Dimension, Field(description="需要增加行列的维度信息")],
    ) -> model.BaseRespModel[AddRowsOrColumnsRespBody]: # type: ignore
        """增加行列"""
        req = BaseRequest().builder().uri(
            "/open-apis/sheets/v2/spreadsheets/:spreadsheet_token/dimension_range"
        ).http_method(HttpMethod.POST).paths({
            "spreadsheet_token": spreadsheet_token,
        }).token_types({AccessTokenType.TENANT, AccessTokenType.USER}).body({
            "dimension": dimension,
        }).build()
        resp: BaseResponse = await self.cli.arequest(req)
        ret_dict = json.loads(resp.raw.content.decode("utf-8"))
        print(json.dumps(ret_dict, indent=2, ensure_ascii=False))
        ret =  model.BaseRespModel[AddRowsOrColumnsRespBody](**ret_dict) # type: ignore
        if not ret.code == 0:
            raise LarkApiException(ret.code, ret.msg)
        return ret

    # https://open.feishu.cn/document/server-docs/docs/sheets-v3/data-operation/reading-a-single-range
    async def read_range(self,
        spreadsheet_token: Annotated[str, Field(description="电子表格的 token。")],
        range: Annotated[str, Field(description="""查询范围。格式为 <sheetId>!<开始位置>:<结束位置>。其中：
sheetId 为工作表 ID，通过获取工作表 获取
<开始位置>:<结束位置> 为工作表中单元格的范围，数字表示行索引，字母表示列索引。如 A2:B2 表示该工作表第 2 行的 A 列到 B 列。range支持四种写法，详情参考电子表格概述""")],
    ) -> model.BaseRespModel[ValueRangeRespBody]: # type: ignore
        """读取单个范围"""
        req = BaseRequest().builder().uri(
            "/open-apis/sheets/v2/spreadsheets/:spreadsheetToken/values/:range"
        ).http_method(HttpMethod.GET).paths({
            "spreadsheetToken": spreadsheet_token,
            "range": range,
        }).token_types({AccessTokenType.TENANT, AccessTokenType.USER}).build()
        resp: BaseResponse = await self.cli.arequest(req)
        ret_dict = json.loads(resp.raw.content.decode("utf-8"))
        # patch values
        row_values = []
        for row in ret_dict["data"]["valueRange"]["values"]:
            col_values = []
            for col in row:
                col_values.append(f"{col}")
            row_values.append(dict(values=col_values))
        ret_dict["data"]["valueRange"]["rowValues"] = row_values

        print(json.dumps(ret_dict, indent=2, ensure_ascii=False))
        ret =  model.BaseRespModel[ValueRangeRespBody](**ret_dict) # type: ignore
        if not ret.code == 0:
            raise LarkApiException(ret.code, ret.msg)
        return ret

    # https://open.feishu.cn/document/server-docs/docs/sheets-v3/data-operation/write-data-to-a-single-range
    async def write_range(self,
        spreadsheet_token: Annotated[str, Field(description="电子表格的 token。")],
        values: Annotated[ValueRangeUpdate, Field(description="指定工作表的范围和写入的数据。")],
    ) -> model.BaseRespModel[WriteValueRespBody]: # type: ignore
        """向单个范围写入数据"""
        # fixed values
        fixed_values = []
        for row in values.get("rowValues", []): # type: ignore
            fixed_values.append(row.get("values", []))

        req = BaseRequest().builder().uri(
            "/open-apis/sheets/v2/spreadsheets/:spreadsheetToken/values"
        ).http_method(HttpMethod.PUT).paths({
            "spreadsheetToken": spreadsheet_token,
        }).token_types({AccessTokenType.TENANT, AccessTokenType.USER}).body({
            "valueRange": {
                "range": values.get("range", ""), # type: ignore
                "values": fixed_values,
            },
        }).build()
        resp: BaseResponse = await self.cli.arequest(req)
        ret_dict = json.loads(resp.raw.content.decode("utf-8"))
        print(json.dumps(ret_dict, indent=2, ensure_ascii=False))
        ret = model.BaseRespModel[WriteValueRespBody](**ret_dict) # type: ignore
        if not ret.code == 0:
            raise LarkApiException(ret.code, ret.msg)
        return ret

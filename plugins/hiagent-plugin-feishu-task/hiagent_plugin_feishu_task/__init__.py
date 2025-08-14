
from typing import Any, Optional, List, Dict, Annotated, Literal
import os
from pydantic import Field
from pathlib import Path
import json
from hiagent_plugin_sdk import BasePlugin, set_meta, SecretField, BuiltinCategory
import lark_oapi as lark # type: ignore
import lark_oapi.api.task.v2 as task_v2 # type: ignore
import hiagent_plugin_feishu_task.sdk_model as model

current_dir = Path(os.path.dirname(os.path.abspath(__file__)))

class LarkApiException(Exception):
    def __init__(self, code: int, msg: str):
        self.code = code
        self.msg = msg
        super().__init__(f"LarkApiError[{code}]: {msg}")

@set_meta(cn_name="飞书任务")
class FeishuTaskPlugin(BasePlugin):
    """飞书任务"""
    hiagent_tools = [
        "create_task", "update_task", "delete_task",
        "add_members",
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

    # https://open.feishu.cn/document/uAjLw4CM/ukTMukTMukTM/task-v2/task/create
    async def create_task(self,
        input_task: Annotated[model.InputTaskModel, Field(description="任务定义")], # type: ignore
    ) -> model.BaseRespModel[model.CreateTaskResponseModel]: # type: ignore
        """创建任务"""
        req = task_v2.CreateTaskRequest.builder().request_body(input_task).build()
        resp = await self.cli.task.v2.task.acreate(req)
        if not resp.success():
            raise LarkApiException(resp.code, resp.msg)
        ret_dict = json.loads(resp.raw.content.decode("utf-8"))
        print(json.dumps(ret_dict, indent=2, ensure_ascii=False))
        ret =  model.BaseRespModel[model.CreateTaskResponseModel](**ret_dict) # type: ignore
        return ret

    # https://open.feishu.cn/document/uAjLw4CM/ukTMukTMukTM/task-v2/task/patch
    async def update_task(self,
        task_guid: Annotated[str, Field(description="要更新的任务全局唯一ID")],
        update_fields: Annotated[List[str], Field(description="设置需要修改的字段")],
        input_task: Annotated[model.InputTaskModel, Field(description="任务定义")], # type: ignore
    ) -> model.BaseRespModel[model.PatchTaskResponseModel]: # type: ignore
        """更新任务"""
        req = task_v2.PatchTaskRequest.builder().task_guid(task_guid).request_body({
            "task": input_task,
            "update_fields": update_fields,
        }).build()
        resp = await self.cli.task.v2.task.apatch(req)
        if not resp.success():
            raise LarkApiException(resp.code, resp.msg)
        ret_dict = json.loads(resp.raw.content.decode("utf-8"))
        print(json.dumps(ret_dict, indent=2, ensure_ascii=False))
        ret =  model.BaseRespModel[model.PatchTaskResponseModel](**ret_dict) # type: ignore
        return ret

    # https://open.feishu.cn/document/uAjLw4CM/ukTMukTMukTM/task-v2/task/delete
    async def delete_task(self,
        task_guid: Annotated[str, Field(description="要更新的任务全局唯一ID")],
    ) -> model.BaseRespModel[dict]: # type: ignore
        """删除任务"""
        req = task_v2.DeleteTaskRequest.builder().task_guid(task_guid).build()
        resp = await self.cli.task.v2.task.adelete(req)
        if not resp.success():
            raise LarkApiException(resp.code, resp.msg)
        ret_dict = json.loads(resp.raw.content.decode("utf-8"))
        print(json.dumps(ret_dict, indent=2, ensure_ascii=False))
        ret =  model.BaseRespModel[dict](**ret_dict) # type: ignore
        return ret

    # https://open.feishu.cn/document/uAjLw4CM/ukTMukTMukTM/task-v2/task/add_members
    async def add_members(self,
        task_guid: Annotated[str, Field(description="要更新的任务全局唯一ID")],
        members: Annotated[List[model.MemberModel], Field(description="要添加的members列表，单请求支持最大50个成员（去重后)")], # type: ignore
        client_token: Annotated[str | None, Field(None, description="幂等token，如果提供则实现幂等行为")] = None,
    ) -> model.BaseRespModel[model.AddMembersTaskResponseModel]: # type: ignore
        """添加任务成员"""
        req = task_v2.AddMembersTaskRequest.builder().task_guid(task_guid).request_body({
            "members": members,
            "client_token": client_token,
        }).build()
        resp = await self.cli.task.v2.task.aadd_members(req)
        if not resp.success():
            raise LarkApiException(resp.code, resp.msg)
        ret_dict = json.loads(resp.raw.content.decode("utf-8"))
        print(json.dumps(ret_dict, indent=2, ensure_ascii=False))
        ret =  model.BaseRespModel[model.AddMembersTaskResponseModel](**ret_dict) # type: ignore
        return ret

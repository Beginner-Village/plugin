
from typing import Any, Optional, List, Dict, Annotated, Literal
import os
from pydantic import Field
from pathlib import Path
import json
from hiagent_plugin_sdk import BasePlugin, set_meta, SecretField, BuiltinCategory
import lark_oapi as lark # type: ignore
import lark_oapi.api.im.v1 as im_v1 # type: ignore
import hiagent_plugin_feishu_message.sdk_model as model

current_dir = Path(os.path.dirname(os.path.abspath(__file__)))

class LarkApiException(Exception):
    def __init__(self, code: int, msg: str):
        self.code = code
        self.msg = msg
        super().__init__(f"LarkApiError[{code}]: {msg}")

@set_meta(cn_name="飞书消息")
class FeishuMessagePlugin(BasePlugin):
    """飞书消息"""
    hiagent_tools = [
        "list_message"
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

    # https://open.feishu.cn/document/server-docs/im-v1/message/list
    async def list_message(self,
        container_id_type: Annotated[Literal["chat", "thread"], Field(description="容器类型。chat：包含单聊（p2p）和群聊（group）, thread：话题")],
        container_id: Annotated[str, Field(description="容器 ID。ID 类型与 container_id_type 取值一致")],
        start_time: Annotated[str, Field(description="待查询历史信息的起始时间，秒级时间戳。thread 容器类型暂不支持获取指定时间范围内的消息。")] = "",
        end_time: Annotated[str, Field(description="待查询历史信息的结束时间，秒级时间戳。thread 容器类型暂不支持获取指定时间范围内的消息。")] = "",
        sort_type: Annotated[str, Field(description="消息排序方式。ByCreateTimeAsc：按消息创建时间升序排列, ByCreateTimeDesc：按消息创建时间降序排列")] = "ByCreateTimeAsc",
        page_size: Annotated[int, Field(description="分页大小，即单次请求所返回的数据条目数。1 ~ 50")] = 20,
        page_token: Annotated[str, Field(description="分页标记，第一次请求不填，表示从头开始遍历；")] = "",
    ) -> model.BaseRespModel[model.ListMessageResponseBodyModel]: # type: ignore
        """获取会话历史消息: 获取指定会话（包括单聊、群组）内的历史消息（即聊天记录）"""
        b = im_v1.ListMessageRequest.builder() \
            .container_id_type(container_id_type).container_id(container_id) \
            .start_time(start_time).end_time(end_time) \
            .page_size(page_size).page_token(page_token).sort_type(sort_type)
        resp = await self.cli.im.v1.message.alist(b.build())
        if not resp.success():
            raise LarkApiException(resp.code, resp.msg)
        ret_dict = json.loads(resp.raw.content.decode("utf-8"))
        print(json.dumps(ret_dict, indent=2, ensure_ascii=False))
        ret =  model.BaseRespModel[model.ListMessageResponseBodyModel](**ret_dict) # type: ignore
        return ret


    # https://open.feishu.cn/document/server-docs/im-v1/message/create
    async def send_message(self,
        receive_id_type: Annotated[str, Field(description="""用户 ID 类型;
open_id：标识一个用户在某个应用中的身份。同一个用户在不同应用中的 Open ID 不同。
union_id：标识一个用户在某个应用开发商下的身份。同一用户在同一开发商下的应用中的 Union ID 是相同的，在不同开发商下的应用中的 Union ID 是不同的。通过 Union ID，应用开发商可以把同个用户在多个应用中的身份关联起来。
user_id：标识一个用户在某个租户内的身份。同一个用户在租户 A 和租户 B 内的 User ID 是不同的。在同一个租户内，一个用户的 User ID 在所有应用（包括商店应用）中都保持一致。User ID 主要用于在不同的应用间打通用户数据。
email：以用户的真实邮箱来标识用户。
chat_id：以群 ID 来标识群聊。""")],
        receive_id: Annotated[str, Field(description="消息接收者的 ID，ID 类型与查询参数 receive_id_type 的取值一致。")],
        msg_type: Annotated[str, Field(description="""消息类型。
text：文本
post：富文本
image：图片
file：文件
audio：语音
media：视频
sticker：表情包
interactive：卡片
share_chat：分享群名片
share_user：分享个人名片
system：系统消息""")],
        content: Annotated[str, Field(description='消息内容，JSON 结构序列化后的字符串。该参数的取值与 msg_type 对应，例如 msg_type 取值为 text，则该参数需要传入文本类型的内容。示例 "{"text":"test content"}"')],
        uuid: Annotated[str, Field(description="自定义设置的唯一字符串序列，用于在发送消息时请求去重。持有相同 uuid 的请求，在 1 小时内至多成功发送一条消息。")] = "",
    ) -> model.BaseRespModel[model.CreateMessageResponseBodyModel]: # type: ignore
        """发送消息: 调用该接口向指定用户或者群聊发送消息。支持发送的消息类型包括文本、富文本、卡片、群名片、个人名片、图片、视频、音频、文件以及表情包等。
        https://open.feishu.cn/document/server-docs/im-v1/message/create"""
        req = im_v1.CreateMessageRequest.builder() \
            .receive_id_type(receive_id_type).request_body({
                "receive_id": receive_id,
                "msg_type": msg_type,
                "content": content,
                "uuid": uuid,
            }).build()
        resp = await self.cli.im.v1.message.acreate(req)
        if not resp.success():
            raise LarkApiException(resp.code, resp.msg)
        ret_dict = json.loads(resp.raw.content.decode("utf-8"))
        print(json.dumps(ret_dict, indent=2, ensure_ascii=False))
        ret =  model.BaseRespModel[model.CreateMessageResponseBodyModel](**ret_dict) # type: ignore
        return ret

    # https://open.feishu.cn/document/server-docs/group/chat/list
    async def list_chat(self,
        user_id_type: Annotated[str, Field(description="""用户 ID 类型;
open_id：标识一个用户在某个应用中的身份。同一个用户在不同应用中的 Open ID 不同。
union_id：标识一个用户在某个应用开发商下的身份。同一用户在同一开发商下的应用中的 Union ID 是相同的，在不同开发商下的应用中的 Union ID 是不同的。通过 Union ID，应用开发商可以把同个用户在多个应用中的身份关联起来。
user_id：标识一个用户在某个租户内的身份。同一个用户在租户 A 和租户 B 内的 User ID 是不同的。在同一个租户内，一个用户的 User ID 在所有应用（包括商店应用）中都保持一致。User ID 主要用于在不同的应用间打通用户数据。""")],
        sort_type: Annotated[str, Field(description="消息排序方式。ByCreateTimeAsc：按消息创建时间升序排列, ByCreateTimeDesc：按消息创建时间降序排列")] = "ByCreateTimeAsc",
        page_size: Annotated[int, Field(description="分页大小，即单次请求所返回的数据条目数。1 ~ 50")] = 20,
        page_token: Annotated[str, Field(description="分页标记，第一次请求不填，表示从头开始遍历；")] = "",
    ) -> model.BaseRespModel[model.ListChatResponseBodyModel]: # type: ignore
        """获取用户或机器人所在的群列表: 获取 access_token 所代表的用户或者机器人所在的群列表"""
        req = im_v1.ListChatRequest.builder() \
            .user_id_type(user_id_type) \
            .sort_type(sort_type).page_size(page_size).page_token(page_token) \
            .build()
        resp = await self.cli.im.v1.chat.alist(req)
        if not resp.success():
            raise LarkApiException(resp.code, resp.msg)
        ret_dict = json.loads(resp.raw.content.decode("utf-8"))
        print(json.dumps(ret_dict, indent=2, ensure_ascii=False))
        ret =  model.BaseRespModel[model.ListChatResponseBodyModel](**ret_dict) # type: ignore
        return ret


from typing import Any, Optional, List, Dict, Annotated, Literal
import os
from pydantic import Field
from pathlib import Path
import json
from hiagent_plugin_sdk import BasePlugin, set_meta, SecretField, BuiltinCategory
import lark_oapi as lark # type: ignore
import lark_oapi.api.calendar.v4 as calendar_v4 # type: ignore
import hiagent_plugin_feishu_calendar.sdk_model as model

current_dir = Path(os.path.dirname(os.path.abspath(__file__)))

class LarkApiException(Exception):
    def __init__(self, code: int, msg: str):
        self.code = code
        self.msg = msg
        super().__init__(f"LarkApiError[{code}]: {msg}")

@set_meta(cn_name="飞书日历")
class FeishuCalendarPlugin(BasePlugin):
    """飞书日历"""
    hiagent_tools = [
        "list_calendars", "create_event", "delete_event", "update_event", "list_event", "search_event",
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

    # https://open.feishu.cn/document/server-docs/calendar-v4/calendar/list-2
    async def list_calendars(self,
        page_size: Annotated[int, Field(description="一次请求返回的最大日历数量。50 ～ 1000")] = 500,
        page_token: Annotated[str, Field(description="分页标记，第一次请求不填，表示从头开始遍历；")] = "",
        sync_token: Annotated[str, Field(description="增量同步标记，第一次请求不填。当分页查询结束（page_token 返回值为空）时，接口会返回 sync_token 字段，下次调用可使用该 sync_token 增量获取日历变更数据")] = "",
    ) -> model.BaseRespModel[model.ListCalendarResponseModel]: # type: ignore
        """查询日历列表"""
        req = calendar_v4.ListCalendarRequest.builder() \
            .page_size(page_size) \
            .page_token(page_token) \
            .sync_token(sync_token) \
            .build()
        resp = await self.cli.calendar.v4.calendar.alist(req)
        if not resp.success():
            raise LarkApiException(resp.code, resp.msg)
        ret_dict = json.loads(resp.raw.content.decode("utf-8"))
        print(json.dumps(ret_dict, indent=2, ensure_ascii=False))
        ret =  model.BaseRespModel[model.ListCalendarResponseModel](**ret_dict) # type: ignore
        return ret

    # https://open.feishu.cn/document/server-docs/calendar-v4/calendar-event/create
    async def create_event(self,
        calendar_id: Annotated[str, Field(description="日历 ID。")],
        event: Annotated[model.CalendarEventModel, Field(description="事件信息")], # type: ignore
        idempotency_key: Annotated[str, Field(description="创建日程的幂等 key，该 key 在应用和日历维度下唯一，用于避免重复创建资源。")] = "",
    ) -> model.BaseRespModel[model.CreateCalendarEventResponseModel]: # type: ignore
        """创建日程"""
        b = calendar_v4.CreateCalendarEventRequest.builder() \
            .calendar_id(calendar_id) \
            .request_body(event)
        if idempotency_key!= "":
            b = b.idempotency_key(idempotency_key)
        req = b.build()
        resp = await self.cli.calendar.v4.calendar_event.acreate(req)
        if not resp.success():
            raise LarkApiException(resp.code, resp.msg)
        ret_dict = json.loads(resp.raw.content.decode("utf-8"))
        print(json.dumps(ret_dict, indent=2, ensure_ascii=False))
        ret =  model.BaseRespModel[model.CreateCalendarEventResponseModel](**ret_dict) # type: ignore
        return ret

    # https://open.feishu.cn/document/server-docs/calendar-v4/calendar-event/delete
    async def delete_event(self,
        calendar_id: Annotated[str, Field(description="日程所在的日历 ID。")],
        event_id: Annotated[str, Field(description="日程 ID。")],
        need_notification: Annotated[str, Field(description="删除日程是否给日程参与人发送 Bot 通知。")] = "true",
    ) -> model.BaseRespModel[dict]: # type: ignore
        """删除日程"""
        req = calendar_v4.DeleteCalendarEventRequest.builder() \
            .calendar_id(calendar_id) \
            .event_id(event_id) \
            .need_notification(need_notification).build()
        resp = await self.cli.calendar.v4.calendar_event.adelete(req)
        if not resp.success():
            raise LarkApiException(resp.code, resp.msg)
        ret_dict = json.loads(resp.raw.content.decode("utf-8"))
        print(json.dumps(ret_dict, indent=2, ensure_ascii=False))
        ret =  model.BaseRespModel[dict](**ret_dict) # type: ignore
        return ret

    # https://open.feishu.cn/document/server-docs/calendar-v4/calendar-event/list
    async def list_event(self,
        calendar_id: Annotated[str, Field(description="日程所在的日历 ID。")],
        anchor_time: Annotated[str, Field(description="时间锚点，Unix 时间戳（秒）。anchor_time用于设置一个时间点，以便直接拉取该时间点之后的日程数据，从而避免拉取全量日程数据。你可以使用page_token或sync_token进行分页或增量拉取anchor_time之后的所有日程数据。比如: \"1609430400\"")],
        # start_time: Annotated[int, Field(description="日程 ID。")],
        # end_time: Annotated[str, Field(description="删除日程是否给日程参与人发送 Bot 通知。")] = "true",
        page_size: Annotated[int, Field(description="一次请求要求返回的最大日程数量。50 ～ 1000")] = 500,
        page_token: Annotated[str, Field(description="分页标记，第一次请求不填，表示从头开始遍历；")] = "",
        sync_token: Annotated[str, Field(description="增量同步标记，第一次请求不填。当分页查询结束（page_token 返回值为空）时，接口会返回 sync_token 字段，下次调用可使用该 sync_token 增量获取日历变更数据。")] = "",
    ) -> model.BaseRespModel[model.ListCalendarEventResponseBodyModel]: # type: ignore
        """查询日程列表"""
        req = calendar_v4.ListCalendarEventRequest.builder() \
            .calendar_id(calendar_id) \
            .anchor_time(anchor_time) \
            .page_size(page_size).page_token(page_token).sync_token(sync_token).build()
        resp = await self.cli.calendar.v4.calendar_event.alist(req)
        if not resp.success():
            raise LarkApiException(resp.code, resp.msg)
        ret_dict = json.loads(resp.raw.content.decode("utf-8"))
        print(json.dumps(ret_dict, indent=2, ensure_ascii=False))
        ret =  model.BaseRespModel[model.ListCalendarEventResponseBodyModel](**ret_dict) # type: ignore
        return ret

    # https://open.feishu.cn/document/server-docs/calendar-v4/calendar-event/patch
    async def update_event(self,
        calendar_id: Annotated[str, Field(description="日程所在的日历 ID。")],
        event_id: Annotated[str, Field(description="日程 ID。")],
        event: Annotated[model.CalendarEventModel, Field(description="事件信息")], # type: ignore
    ) -> model.BaseRespModel[model.PatchCalendarEventResponseBodyModel]: # type: ignore
        """更新日程"""
        req = calendar_v4.PatchCalendarEventRequest.builder() \
            .calendar_id(calendar_id) \
            .event_id(event_id) \
            .request_body(event).build()
        resp = await self.cli.calendar.v4.calendar_event.apatch(req)
        if not resp.success():
            raise LarkApiException(resp.code, resp.msg)
        ret_dict = json.loads(resp.raw.content.decode("utf-8"))
        print(json.dumps(ret_dict, indent=2, ensure_ascii=False))
        ret =  model.BaseRespModel[model.PatchCalendarEventResponseBodyModel](**ret_dict) # type: ignore
        return ret

    # https://open.feishu.cn/document/server-docs/calendar-v4/calendar-event/search
    async def search_event(self,
        calendar_id: Annotated[str, Field(description="日程所在的日历 ID。")],
        query: Annotated[str, Field(description="搜索关键字。")],
        filter: Annotated[model.EventSearchFilterModel, Field(description="搜索条件")] = {}, # type: ignore
        page_size: Annotated[int, Field(description="一次请求要求返回的最大日程数量。50 ～ 1000")] = 500,
        page_token: Annotated[str, Field(description="分页标记，第一次请求不填，表示从头开始遍历；")] = "",
    ) -> model.BaseRespModel[model.SearchCalendarEventResponseBodyModel]: # type: ignore
        """搜索日程"""
        req = calendar_v4.SearchCalendarEventRequest.builder() \
            .calendar_id(calendar_id) \
            .request_body({
                "query": query,
                "filter": filter,
            }) \
            .page_size(page_size).page_token(page_token) \
            .build()
        resp = await self.cli.calendar.v4.calendar_event.asearch(req)
        if not resp.success():
            raise LarkApiException(resp.code, resp.msg)
        ret_dict = json.loads(resp.raw.content.decode("utf-8"))
        print(json.dumps(ret_dict, indent=2, ensure_ascii=False))
        ret =  model.BaseRespModel[model.SearchCalendarEventResponseBodyModel](**ret_dict) # type: ignore
        return ret

    # https://open.feishu.cn/document/server-docs/calendar-v4/calendar-event-attendee/create
    async def create_event_attendee(self,
        calendar_id: Annotated[str, Field(description="日程所在的日历 ID。")],
        event_id: Annotated[str, Field(description="日程 ID。")],
        attendees: Annotated[List[model.CalendarEventAttendeeModel], Field(description="搜索条件")] = {}, # type: ignore
    ) -> model.BaseRespModel[model.CreateCalendarEventAttendeeResponseBodyModel]: # type: ignore
        """添加日程参与人"""
        req = calendar_v4.CreateCalendarEventAttendeeRequest.builder() \
            .calendar_id(calendar_id) \
            .event_id(event_id) \
            .request_body({
                "attendees": attendees,
            }) \
            .build()
        resp = await self.cli.calendar.v4.calendar_event_attendee.acreate(req)
        if not resp.success():
            raise LarkApiException(resp.code, resp.msg)
        ret_dict = json.loads(resp.raw.content.decode("utf-8"))
        print(json.dumps(ret_dict, indent=2, ensure_ascii=False))
        ret =  model.BaseRespModel[model.CreateCalendarEventAttendeeResponseBodyModel](**ret_dict) # type: ignore
        return ret

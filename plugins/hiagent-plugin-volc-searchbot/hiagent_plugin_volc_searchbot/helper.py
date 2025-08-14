from typing import AsyncGenerator, List, Any

from hiagent_plugin_sdk.schema import ServerSentEvent
from hiagent_plugin_volc_searchbot.common import EventData, AgentIntention
import json

# https://bytedance.larkoffice.com/docx/CXNBd3ADIotQQlxLdWDc29cPnCg
def adapter_runtime(event: ServerSentEvent) -> List[ServerSentEvent]:
    newData: dict[str, Any]
    if event.event == "close":
        return [ServerSentEvent(event="close", data="closed")]
    if event.event != "message":
        return []
    ret = []
    if not event.data:
        return []
    data_dict = json.loads(event.data)
    data_obj = EventData(**data_dict)
    if len(data_obj.choices) == 0:
        return []
    if data_obj.choices[0].delta is None:
        return []
    if not data_obj.choices[0].delta.content:
        return []
    chat_delta = data_obj.choices[0].delta.content
    if chat_delta:
        newData = {
            "content": chat_delta
        }
        ret.append(ServerSentEvent(event="message", data=json.dumps(newData, ensure_ascii=False)))
    if data_obj.references is None:
        data_obj.references = []
    if data_obj.cards is None:
        data_obj.cards = []
    if len(data_obj.references) > 0 or len(data_obj.cards) > 0:
        intention_evt = AgentIntention(
            references=data_obj.references,
            cards=data_obj.cards,
        )
        ret.append(ServerSentEvent(event="agent_intention", data=intention_evt.model_dump_json()))
    return ret

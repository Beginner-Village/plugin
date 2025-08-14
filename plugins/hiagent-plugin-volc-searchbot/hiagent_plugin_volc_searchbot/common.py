from typing import List
from pydantic import BaseModel, Field

TOOL_NAME = "SmartSearch"

class VolcAPIException(Exception):
    def __init__(self, code: str, message: str) -> None:
        self.code = code
        self.message = message
        super().__init__(f"VolcException[{code}]: {message}")

class VolcRespError(BaseModel):
    """火山引擎返回结果错误信息"""
    Code: str
    Message: str = ""

class CoverImage(BaseModel):
    """封面图"""
    url: str
    width: int
    height: int

class Result(BaseModel):
    """搜索结果"""
    id: str = ""
    source_type: str | None = None
    site_name: str | None = None
    title: str | None = None
    summary: str | None = None
    publish_time: int | None = None
    url: str = Field("")
    cover_image: CoverImage | None = None
    width: int | None = None
    height: int | None = None
    duration: int | None = None

class Card(BaseModel):
    card_type: str
    video_card: dict | None = None
    weather_card: dict | None = None
    image_card: dict | None = None
    timeline_card: dict | None = None

class AgentIntention(BaseModel):
    """智能体意图"""
    intention: str = TOOL_NAME
    references: List[Result] = []
    cards: List[Card] = []

class SearchResp(BaseModel):
    """返回结果"""
    content: str
    agent_intention: AgentIntention | None = None

class VolcRespMetadata(BaseModel):
    Error: VolcRespError | None = None

class VolcRespMessage(BaseModel):
    role: str
    content: str
    tool_calls: List[dict] | None = None

class VolcRespChoice(BaseModel):
    message: VolcRespMessage | None = None
    delta: VolcRespMessage | None = None
    finish_reason: str = ""
    index: int = 0

class Error(BaseModel):
    """火山引擎返回结果错误信息"""
    code: str
    message: str = ""
    type: str | None = None

class VolcRespResult(BaseModel):
    choices: List[VolcRespChoice] = []
    references: List[Result] = []
    cards: List[Card] = []
    error: Error | None = None


class VolcResp(BaseModel):
    """火山引擎返回结果"""
    ResponseMetadata: VolcRespMetadata
    Result: VolcRespResult | None = None


class EventData(BaseModel):
    """意图数据"""
    id: str = ""
    object: str = ""
    choices: List[VolcRespChoice] = []
    references: List[Result] | None = None
    cards: List[Card] | None = None
    created: int = 0

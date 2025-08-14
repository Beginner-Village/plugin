from pydantic import BaseModel, Field
from typing import List, Optional

from redis.commands.graph.execution_plan import Operation


class ScrapeItem(BaseModel):
    content: str = Field(default="", description="内容")
    # markdown: str = Field(default="", description="markdown")
    # rawHtml: str = Field(default="", description="html")
    # linksOnPage: str = Field(default="", description="页面链接")
    metadata: dict = Field(default_factory=dict, description="元数据")

    class Config:
        extra = "allow"

class ScrapeResult(BaseModel):
    success: bool = Field(default=False, description="是否成功")
    data: Optional[ScrapeItem] = Field(default=None, description="数据")
    returnCode: Optional[int] = Field(default=None, description="返回码")

    class Config:
        extra = "allow"

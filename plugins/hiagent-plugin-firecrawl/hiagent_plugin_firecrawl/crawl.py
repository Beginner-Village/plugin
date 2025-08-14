from pydantic import BaseModel, Field
from typing import List, Optional

from redis.commands.graph.execution_plan import Operation


class CrawlItem(BaseModel):
    content: str = Field(default="", description="内容")
    # markdown: str = Field(default="", description="markdown")
    # rawHtml: str = Field(default="", description="html")
    # linksOnPage: str = Field(default="", description="页面链接")
    metadata: dict = Field(default_factory=dict, description="元数据")

    class Config:
        extra = "allow"

class CrawlResult(BaseModel):
    status: str = Field(default="", description="状态")
    current: Optional[int] = Field(default=None, description="当前数量")
    total: Optional[int] = Field(default=None, description="总数量")
    data: Optional[List[CrawlItem]] = Field(default=None, description="数据")

    class Config:
        extra = "allow"

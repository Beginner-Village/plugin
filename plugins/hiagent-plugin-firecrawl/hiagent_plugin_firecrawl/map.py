from pydantic import BaseModel, Field
from typing import List, Optional

from redis.commands.graph.execution_plan import Operation

class MapResult(BaseModel):
    success: bool = Field(default=False, description="是否成功")
    links: Optional[list[str]] = Field(default=None, description="链接列表")

    class Config:
        extra = "allow"

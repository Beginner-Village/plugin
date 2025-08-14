from pydantic import BaseModel, Field
from typing import List
from hiagent_plugin_amap.plan_walking import Step


class Path(BaseModel):
    distance: int = Field(None, title="起点和终点的步行距离", description="单位：米")
    duration: int = Field(None, title="步行时间预计", description="单位：秒")
    steps: List[Step] = Field([], description="路线")


class Route(BaseModel):
    origin: str = Field(None, title="起点")
    destination: str = Field(None, title="终点")
    paths: List[Path] = Field([], description="方案")


class PlanBicycleResult(BaseModel):
    errmsg: str
    errcode: int  # 返回值为 0 或 1，0，表示成功
    errdetail: str  = Field(None)
    data: Route = Field(None, title="数据")

from pydantic import BaseModel, Field
from typing import List


class Step(BaseModel):
    instruction: str = Field(None, title="路段步行指示")
    road: str = Field(None, title="道路名称")
    distance: int = Field(None, title="此路段距离", description="单位：米")
    orientation: str = Field(None, title="方向")
    duration: int = Field(None, title="此路段预计步行时间")
    polyline: str = Field(None, title="此路段坐标点")
    action: str = Field(None, title="步行主要动作")
    assistant_action: str = Field(None, title="步行辅助动作")
    walk_type: int = Field(None,
        title="这段路是否存在特殊的方式", description="""0，普通道路;1，人行横道;3，地下通道;4，过街天桥;5，地铁通道;6，公园;7，广场;8，扶梯;9，直梯;10，索道;11，空中通道;12，建筑物穿越通道;13，行人通道;14，游船路线;15，观光车路线;16，滑道;18，扩路;19，道路附属连接线;20，阶梯;21，斜坡;22，桥;23，隧道;30，轮渡""")


class Path(BaseModel):
    distance: str = Field(None, title="起点和终点的步行距离", description="单位：米")
    duration: str = Field(None, title="步行时间预计", description="单位：秒")
    steps: List[Step] = Field([], description="路线")


class Route(BaseModel):
    origin: str = Field(None, title="起点")
    destination: str = Field(None, title="终点")
    paths: List[Path] = Field([], description="方案")


class PlanWalkingResult(BaseModel):
    info: str
    status: int  # 返回值为 0 或 1，0 表示请求失败；1 表示请求成功。
    count: int = Field(0, title="总数")
    route: Route = Field(None, title="路线方案")

from pydantic import BaseModel, Field
from typing import List


class Tmc(BaseModel):
    distance: str = Field(None, title="此段路的长度", description="单位：米")
    status: str = Field(None,
        title="此段路的交通情况", description="未知、畅通、缓行、拥堵、严重拥堵")
    polyline: str = Field(None, title="此段路的轨迹", description="规格：x1,y1;x2,y2")


class District(BaseModel):
    name: str = Field(None, title="途径区县名称")
    adcode: str = Field(None, title="途径区县 adcode")


class City(BaseModel):
    name: str = Field(None, title="名称")
    citycode: str = Field(None, title="途径城市编码")
    adcode: str = Field(None, title="途径区域编码")
    districts: List[District] = Field(None, title="途径区县")


class Step(BaseModel):
    instruction: str = Field(None, title="行驶指示")
    orientation: str = Field(None, title="方向")
    road: str = Field(None, title="道路名称")
    distance: str = Field(None, title="此路段距离", description="单位：米")
    tolls: str = Field(None, title="此路段收费", description="单位：元")
    toll_distance: str = Field(None, title="收费路段距离", description="单位：米")
    toll_road: str = Field(None, title="主要收费道路")
    polyline: str = Field(None, title="此路段坐标点串")
    action: str = Field(None, title="导航主要动作")
    assistant_action: str = Field(None, title="步行辅助动作")
    tmcs: List[Tmc] = Field(None, title="驾车导航详细信息")
    cities: List[City] = Field(None, title="路线途经行政区划")


class Path(BaseModel):
    distance: str = Field(None, title="起点和终点的步行距离", description="单位：米")
    duration: str = Field(None, title="步行时间预计", description="单位：秒")
    strategy: str = Field(None, title="导航策略")
    tolls: str = Field(None, title="此导航方案道路收费", description="单位：元")
    restriction: str = Field(None, title="限行结果", description="0 代表限行已规避或未限行，即该路线没有限行路段; 1 代表限行无法规避，即该线路有限行路段")
    traffic_lights: str = Field(None, title="红绿灯个数")
    toll_distance: str = Field(None, title="收费路段距离", description="单位：米")
    steps: List[Step] = Field([], description="路线")


class DrivingRoute(BaseModel):
    origin: str = Field(None, title="起点")
    destination: str = Field(None, title="终点")
    taxi_cost: str = Field(None, title="打车费用")
    paths: List[Path] = Field([], description="方案")


class PlanDrivingResult(BaseModel):
    info: str
    status: int  # 返回值为 0 或 1，0 表示请求失败；1 表示请求成功。
    count: int = Field(None, title="总数")
    route: DrivingRoute = Field(None, title="驾车换乘方案")

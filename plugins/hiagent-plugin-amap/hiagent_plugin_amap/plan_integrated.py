from pydantic import BaseModel, Field
from typing import List


class BusStop(BaseModel):
    name: str = Field(None, title="途径公交站点信息")
    id: str = Field(None, title="公交站点编号")
    location: str = Field(None, title="公交站点经纬度")


class Busline(BaseModel):
    departure_stop: BusStop = Field(None, title="起始站点")
    arrival_stop: BusStop = Field(None, title="到达站点")
    name: str = Field(None, title="公交路线名称")
    id: str = Field(None, title="线路id")
    type: str = Field(None, title="公交类型")
    distance: str = Field(None, title="公交行驶距离", description="单位：米")
    duration: str = Field(None, title="公交预计行驶时间", description="单位：秒")
    polyline: str = Field(None, title="此路段坐标集")
    start_time: str = Field(
        None, title="首班车时间", description="格式如：0600，代表06：00")
    end_time: str = Field(
        None, title="末班车时间", description="格式如：0600，代表06：00")
    via_num: int = Field(None, title="途径站数")
    via_stops: List[BusStop] = Field(None, title="途径站")


class Bus(BaseModel):
    buslines: List[Busline] = Field(None, title="线路列表")


class SubwayEntry(BaseModel):
    location: str = Field(None, title="入口经纬度")

class DepartureStop(BaseModel):
    id: str = Field(None, title="站点id")
    name: str = Field(None, title="站点名称")
    location: str = Field(None, title="站点经纬度")
    adcode: str = Field(None, title="站点所在区域编码")
    time: str = Field(None, title="站点预计到站时间")
    end: str = Field(None, title="是否为终点站", description="1表示为终点站，0表示非终点站")
    start: str = Field(None, title="是否始发站", description="1表示为始发站，0表示非始发站")

class Alter(BaseModel):
    id: str = Field(None, title="备选方案 ID")
    name: str = Field(None, title="备选线路名称")

class Space(BaseModel):
    code: str = Field(None, title="仓位编码")
    cost: str = Field(None, title="仓位费用")

class Railway(BaseModel):
    id: str = Field(None, title="线路id")
    time: str = Field(None, title="该线路车段耗时")
    name: str = Field(None, title="线路名称")
    trip: str = Field(None, title="线路车次号")
    distance: str = Field(None, title="该 item 换乘段的行车总距离")
    type: str = Field(None, title="线路车次类型")
    departure_stop: DepartureStop = Field(None, title="火车始发站信息")
    arrival_stop: DepartureStop = Field(None, title="火车到站信息")
    via_stop: List[DepartureStop] = Field(None, title="途径站点信息")
    alters: List[Alter] = Field(None, title="聚合的备选方案")
    spaces: List[Space] = Field(None, title="仓位及价格信息")


class WalkingStep(BaseModel):
    instruction: str = Field(None, title="此段路的行走介绍")
    road: str = Field(None, title="道路名称")
    distance: str = Field(None, title="此路段距离", description="单位：米")
    duration: str = Field(None, title="步行预计时间", description="单位：秒")
    polyline: str = Field(None, title="此段路的坐标")
    action: str = Field(None, title="步行主要动作")
    assistant_action: str = Field(None, title="步行辅助动作")


class Walking(BaseModel):
    origin: str = Field(None, title="起点坐标")
    destination: str = Field(None, title="终点坐标")
    distance: int = Field(None, title="每段线路步行距离", description="单位：米")
    duration: int = Field(None, title="步行预计时间", description="单位：秒")
    steps: List[WalkingStep] = Field([], title="步行路段列表")


class Segment(BaseModel):
    walking: Walking = Field(None, title="此路段步行导航信息")
    bus: Bus = Field(None, title="此路段公交导航信息")
    entrance: SubwayEntry = Field(None, title="地铁入口")
    exit: SubwayEntry = Field(None, title="地铁出口")
    railway: Railway = Field(None, title="乘坐火车的信息")


class Emergency(BaseModel):
    linetype: str = Field(
        None, title="事件类型", description="1：影响乘坐；2：不影响乘坐")
    eventTagDesc: str = Field(
        None, title="事件标签", description='值为："提示“、”甩站“、”突发“、”停运“')
    ldescription: str = Field(None, title="事件的线路上的文案")
    busid: str = Field(None, title="线路id")
    busname: str = Field(None, title="线路名")


class Transit(BaseModel):
    cost: str = Field(None, title="此换乘方案价格", description="单位：元")
    duration: str = Field(None, title="步行时间预计", description="单位：秒")
    nightflag: str = Field(
        None, title="是否是夜班车", description="0：非夜班车；1：夜班车")
    walking_distance: str = Field(
        None, title="此方案总步行距离", description="单位：米")
    emergency: Emergency = Field(None, title="紧急事件")
    segments: List[Segment] = Field(None, title="换乘路段列表")


class IntegratedRoute(BaseModel):
    origin: str = Field(None, title="起点")
    destination: str = Field(None, title="终点")
    distance: str = Field(None, title="起点和终点的步行距离", description="单位：米")
    taxi_cost: str = Field(None, title="出租车费用")
    transits: List[Transit] = Field([], title="公交换乘方案列表")


class PlanIntegratedResult(BaseModel):
    info: str
    status: int  # 返回值为 0 或 1，0 表示请求失败；1 表示请求成功。
    count: int = Field(None, title="总数")
    route: IntegratedRoute = Field(None, title="驾车换乘方案")

from typing import Generic, TypeVar
from pydantic import BaseModel, Field

T = TypeVar('T')

class RC(BaseModel):
    c: int
    p: str

class CommonResp(BaseModel, Generic[T]):
    code: int = Field(0)
    msg: str = Field("")
    data: T = Field(None)
    rc: RC = Field(None)

class Current(BaseModel):
    day: int = Field(0, description="当地时间的白天晚上标识, 0: 白天, 1: 晚上")
    dewpoint: float = Field(0, description="露点温度, 摄氏度(°C)")
    humidity: int = Field(0, description="相对湿度, %")
    icon: int = Field(0, description="天气图标")
    mslp: int = Field(0, description="气压, hPa")
    obs_time: str = Field("", description="数据更新时间")
    precip_1h: float = Field(0, description="1小时降水量, mm/h")
    real_feel: float = Field(0, description="体感温度, 摄氏度(°C)")
    sky: int = Field(0, description="云覆盖率")
    temp: float = Field(0, description="温度, 摄氏度(°C)")
    uvi: int = Field(0, description="紫外线强度")
    vis: int = Field(0, description="能见度, m")

    weather: str = Field("", description="天气现象")
    weather_id: int = Field(0, description="天气现象ID")

    wind_degrees: int = Field(0, description="风向角度")
    wind_dir: str = Field("", description="风向")
    wind_dir_id: int = Field(0, description="风向id")
    wind_level: int = Field(0, description="风力等级")
    wspd: float = Field(0, description="风速, m/s")

    comfort: int = Field(0)
    get_time: str = Field("")
    sun_down: str = Field("")
    sun_rise: str = Field("")
    tips: str = Field("")

class CurrentResp(BaseModel):
    current: Current

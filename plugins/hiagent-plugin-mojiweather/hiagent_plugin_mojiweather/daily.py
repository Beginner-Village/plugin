from typing import Generic, TypeVar, List
from pydantic import BaseModel, Field

T = TypeVar('T')

class CommonResp(BaseModel, Generic[T]):
    code: int
    msg: str
    data: T = Field(None)

class Daily(BaseModel):
    humidity: int = Field(0, description="相对湿度, %")
    icon_day: int = Field(0, description="白天天气图标ID")
    icon_night: int = Field(0, description="夜晚天气图标ID")
    moon_rise: str = Field("", description="月升时间")
    moon_down: str = Field("", description="月落时间")
    moon_phase: str = Field("", description="月相")
    mslp: int = Field(0, description="气压, hPa")
    pop: int = Field(0, description="降水概率, %")
    predict_date: str = Field("", description="预报时间")
    qpf: float = Field(0, description="预测对应天的日累计降水量, mm")
    sun_down: str = Field("", description="日落时间")
    sun_rise: str = Field("", description="日出时间")
    temp_high: float = Field(0, description="最高温度, 摄氏度(°C)")
    temp_low: float = Field(0, description="最低温度, 摄氏度(°C)")
    uvi: int = Field(0, description="紫外线强度")

    weather_day: str = Field("", description="白天天气现象")
    weather_id_day: int = Field(0, description="白天天气现象 id")
    weather_id_night: int = Field(0, description="夜晚天气现象 id")
    weather_night: str = Field("", description="夜晚天气现象")

    get_time: str = Field("")

    wind_degrees_day: int = Field(0, description="白天风向角度")
    wind_degrees_night: int = Field(0, description="夜晚风向角度")
    wind_dir_day: str = Field("", description="白天风向")
    wind_dir_id_day: int = Field(0, description="白天风向 id")
    wind_dir_night: str = Field("", description="夜晚风向")
    wind_dir_id_night: int = Field(0, description="夜晚风向 id")
    wind_level_day: str = Field("", description="白天平均风力等级")
    wind_level_night: str = Field("", description="夜晚平均风力等级")
    wspd_day: float = Field(0, description="白天风速, m/s")
    wspd_night: float = Field(0, description="夜晚风速, m/s")

    pop_day: int = Field(0)
    pop_night: int = Field(0)
    update_time: str = Field("")


class DailyResp(BaseModel):
    daily: List[Daily] = Field([])

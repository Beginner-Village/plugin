from pydantic import BaseModel, Field
from typing import List


class GeocodeItem(BaseModel):
    country: str = Field(None, description="国家")
    province: str = Field(None, description="省份")
    city: str = Field(None, description="城市")
    citycode: str = Field(None, description="城市编码")
    district: str = Field(None, description="区")
    street: str = Field(None, description="街道")
    number: str = Field(None, description="门牌")
    adcode: str = Field(None, description="区域编码")
    location: str = Field(None, description="坐标点")
    level: str = Field(None, description="匹配级别")


class GeocodeResult(BaseModel):
    info: str
    status: int  # 返回值为 0 或 1，0 表示请求失败；1 表示请求成功。
    count: int = Field(None, description="总数")
    geocodes: List[GeocodeItem] = Field([], description="列表")

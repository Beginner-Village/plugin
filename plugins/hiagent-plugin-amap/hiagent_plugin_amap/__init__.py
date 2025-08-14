
from typing import List, Annotated
import os
import logging
import json
from pathlib import Path
from pydantic import Field
from hiagent_plugin_sdk import BasePlugin, set_meta, ConfigValidateMixin, SecretField, BuiltinCategory, arequest
from hiagent_plugin_amap.geocode import GeocodeResult
from hiagent_plugin_amap.plan_walking import PlanWalkingResult
from hiagent_plugin_amap.plan_driving import PlanDrivingResult
from hiagent_plugin_amap.plan_integrated import PlanIntegratedResult
from hiagent_plugin_amap.plan_bicycle import PlanBicycleResult

logger = logging.getLogger(__name__)
current_dir = Path(os.path.dirname(os.path.abspath(__file__)))

class APIErrCode(Exception):
    def __init__(self, code: int, message: str):
        self.code = code
        self.message = message
        super().__init__(f"API error: code={code}, message={message}")

@set_meta(cn_name="高德地图", en_name="Amap")
class AmapPlugin(BasePlugin, ConfigValidateMixin):
    """高德地图插件，该插件能够帮助用户规划出最优的骑行、步行、开车及公共交通路线。"""

    hiagent_tools = ["poi_to_geocode", "plan_walking", "plan_driving", "plan_integrated", "plan_bicycle"]
    hiagent_category = BuiltinCategory.LifeAssistant

    def __init__(self, api_key: Annotated[str, SecretField(description="申请链接: <https://lbs.amap.com/api/webservice/create-project-and-key>")]):
        self.api_key = api_key

    @classmethod
    def _icon_uri(cls) -> str:
        return f"file://{current_dir}/icon.png"

    async def _get(self, url: str, params: dict) -> dict:
        query: dict[str, str | float | int] = {k: v for k, v in params.items() if v is not None}
        query["key"] = self.api_key
        async with arequest("GET", url, params=query) as resp:
            resp.raise_for_status()
            ret_dict =  await resp.json()
        delete_empty_list_or_null(ret_dict)
        print(json.dumps(ret_dict, indent=2, ensure_ascii=False))
        return ret_dict

    # https://lbs.amap.com/api/webservice/guide/api/georegeo/
    async def poi_to_geocode(self,
        address: Annotated[str, Field(description="结构化地址信息. 规则遵循：国家、省份、城市、区县、城镇、乡村、街道、门牌号码、屋邨、大厦，如：北京市朝阳区阜通东大街6号。")],
        city: Annotated[str | None, Field(description="指定查询的城市. 可选输入内容包括：指定城市的中文（如北京）、指定城市的中文全拼（beijing）、citycode（010）、adcode（110000），不支持县级市。当指定城市查询内容为空时，会进行全国范围内的地址转换检索。")] = None,
    ) -> GeocodeResult:
        """地理编码，支持将详细的结构化地址转换为高德经纬度坐标。"""
        url = "https://restapi.amap.com/v3/geocode/geo"
        params = {
            "address": address,
            "city": city,
        }
        ret_dict = await self._get(url, params)
        logging.debug(json.dumps(ret_dict, indent=2))
        ret =  GeocodeResult(**ret_dict)
        if ret.status == 0:
            raise APIErrCode(ret.status, ret.info)
        return ret

    # https://lbs.amap.com/api/webservice/guide/api/direction#s3
    async def plan_walking(self,
        # origin 在 golang scheme 解析的时候会被忽略
        start: Annotated[str, Field(title="出发点", description="规则：lon，lat（经度，纬度）， “,”分割，如117.500244, 40.417801 经纬度小数点不超过6位")],
        destination: Annotated[str, Field(title="目的地", description="规则：lon，lat（经度，纬度）， “,”分割，如117.500244, 40.417801 经纬度小数点不超过6位")],
    ) -> PlanWalkingResult:
        """步行路线规划"""
        url = "https://restapi.amap.com/v3/direction/walking"
        params = {
            "origin": start,
            "destination": destination,
        }
        ret_dict = await self._get(url, params)
        logging.debug(json.dumps(ret_dict, indent=2))
        ret = PlanWalkingResult(**ret_dict)
        if ret.status == 0:
            raise APIErrCode(ret.status, ret.info)
        return ret


    # https://lbs.amap.com/api/webservice/guide/api/direction#s11
    async def plan_driving(self,
        start: Annotated[str, Field(title="出发点", description="规则：lon，lat（经度，纬度）， “,”分割，如117.500244, 40.417801 经纬度小数点不超过6位")],
        destination: Annotated[str, Field(title="目的地", description="规则：lon，lat（经度，纬度）， “,”分割，如117.500244, 40.417801 经纬度小数点不超过6位")],
    ) -> PlanDrivingResult:
        """驾驶路线规划"""
        url = "https://restapi.amap.com/v3/direction/driving"
        params = {
            "origin": start,
            "destination": destination,
        }
        ret_dict = await self._get(url, params)
        ret = PlanDrivingResult(**ret_dict)
        if ret.status == 0:
            raise APIErrCode(ret.status, ret.info)
        return ret

    # https://lbs.amap.com/api/webservice/guide/api/direction#s7
    async def plan_integrated(self,
        start: Annotated[str, Field(title="出发点", description="规则：lon，lat（经度，纬度）， “,”分割，如117.500244, 40.417801 经纬度小数点不超过6位")],
        destination: Annotated[str, Field(title="目的地", description="规则：lon，lat（经度，纬度）， “,”分割，如117.500244, 40.417801 经纬度小数点不超过6位")],
        city: Annotated[str, Field(title="城市/跨城规划时的起点城市", description="目前支持市内公交换乘/跨城公交的起点城市。可选值：城市名称/citycode")],
    ) -> PlanIntegratedResult:
        """公共交通路线规划"""
        url = "https://restapi.amap.com/v3/direction/transit/integrated"
        params = {
            "origin": start,
            "destination": destination,
            "city": city,
        }
        ret_dict = await self._get(url, params)
        ret = PlanIntegratedResult(**ret_dict)
        if ret.status == 0:
            raise APIErrCode(ret.status, ret.info)
        return ret

    # https://lbs.amap.com/api/webservice/guide/api/direction#s7
    async def plan_bicycle(self,
        start: Annotated[str, Field(title="出发点", description="规则：lon，lat（经度，纬度）， “,”分割，如117.500244, 40.417801 经纬度小数点不超过6位")],
        destination: Annotated[str, Field(title="目的地", description="规则：lon，lat（经度，纬度）， “,”分割，如117.500244, 40.417801 经纬度小数点不超过6位")],
    ) -> PlanBicycleResult:
        """骑行路线规划"""
        url = "https://restapi.amap.com/v4/direction/bicycling"
        params = {
            "origin": start,
            "destination": destination,
        }
        ret_dict = await self._get(url, params)
        ret = PlanBicycleResult(**ret_dict)
        if ret.errcode != 0:
            raise APIErrCode(ret.errcode, ret.errmsg)
        return ret

    async def _validate(self):
        url = "https://restapi.amap.com/v3/config/district"
        params = {}
        ret_dict = await self._get(url, params)
        if ret_dict.get("status")!="1":
            raise APIErrCode(ret_dict.get("status"), ret_dict.get("info"))

def delete_empty_list_or_null(d: dict):
    """递归将 dict 中的 [] 转换成 None"""
    if not isinstance(d, dict):
        return
    remove_key = []
    for k, v in d.items():
        if v is None:
            remove_key.append(k)
            continue
        if isinstance(v, list):
            if len(v) == 0:
                remove_key.append(k)
                continue
            for item in v:
                delete_empty_list_or_null(item)
        delete_empty_list_or_null(v)
    for k in remove_key:
        d.pop(k)

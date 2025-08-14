
from typing import List, Annotated, Any
import os
import logging
from functools import cache
import time
import sqlite3
import json
from pathlib import Path

from pydantic import Field
from hiagent_plugin_sdk import BasePlugin, set_meta, SecretField, BuiltinCategory, arequest
from hiagent_plugin_mojiweather.current import CurrentResp, CommonResp
from hiagent_plugin_mojiweather.daily import DailyResp

logger = logging.getLogger(__name__)
current_dir = Path(os.path.dirname(os.path.abspath(__file__)))

class APIErrCode(Exception):
    def __init__(self, code: int, message: str):
        self.code = code
        self.message = message
        super().__init__(f"API error: code={code}, message={message}")

@set_meta(cn_name="墨迹天气")
class MojiWeatherPlugin(BasePlugin):
    """搜索提供的国家, 省, 市, 区县的天气信息"""

    hiagent_tools = ["CurrentWeather", "Latest40DayWeather"]
    hiagent_category = BuiltinCategory.LifeAssistant

    API_ADDR = "http://coapi.moji.com/whapi/v2/weather"
    CITY_ID_DB = f"{current_dir}/city_id.db"

    @cache
    def _connect_db(self) -> sqlite3.Connection:
        return sqlite3.connect(self.CITY_ID_DB)

    def __init__(self,
        current_weather_token: Annotated[str, Field(title="实时天气Token", description="该插件包含两个工具，请分别填写对应的授权信息, 申请说明: <https://www.mojicb.com/apis>")] = "",
        current_weather_password: Annotated[str, SecretField(title="实时天气密码", description="")] = "",
        latest_40days_weather_token: Annotated[str, Field(title="40天天气Token", description="该插件包含两个工具，请分别填写对应的授权信息, 申请说明: <https://www.mojicb.com/apis>")] = "",
        latest_40days_weather_password: Annotated[str, SecretField(title="40天天气密码", description="")] = "",
    ):
        self.current_weather_token = current_weather_token
        self.current_weather_password = current_weather_password
        self.latest_40days_weather_token = latest_40days_weather_token
        self.latest_40days_weather_password = latest_40days_weather_password

    @classmethod
    def _icon_uri(cls) -> str:
        return f"file://{current_dir}/icon.png"

    async def CurrentWeather(self,
        name: Annotated[str, Field(description="查询的城市或者区县名, 中文, 比如: 北京市, 浦东区, 西湖区, 杭州市, 洛杉矶, 纽约")],
        parent: Annotated[str, Field(description="查询的上一级行政区, 中文选填, 比如, 北京市, 上海市, 杭州市, 浙江省, 加利福尼亚州")] = "",
    ) -> CommonResp[CurrentResp]:
        '''搜索提供的省、市、区县的当前天气'''
        t = int(time.time()*1000)
        city_id = self.get_city_id(name, parent)
        key = self.sign(self.current_weather_password, t, city_id)
        params: dict[str, str|int] = {
            "cityId": city_id,
            "timestamp": t,
            "token": self.current_weather_token,
            "key": key,
        }
        async with arequest("GET", self.API_ADDR, params=params) as resp:
            resp.raise_for_status()
            data =  await resp.text()
        ret_dict = json.loads(data)
        ret = CommonResp[CurrentResp](**ret_dict)
        if ret.code!= 0:
            raise APIErrCode(ret.code, ret.msg)
        if ret.rc != None and ret.rc.c!= 0:
            raise APIErrCode(ret.rc.c, ret.rc.p)
        return ret


    async def Latest40DayWeather(self,
        name: Annotated[str, Field(description="查询的城市或者区县名, 中文, 比如: 北京市, 浦东区, 西湖区, 杭州市, 洛杉矶, 纽约")],
        parent: Annotated[str, Field(description="查询的上一级行政区, 中文选填, 比如, 北京市, 上海市, 杭州市, 浙江省, 加利福尼亚州")] = "",
    ) -> CommonResp[DailyResp]:
        '''搜索提供的省、市、区县未来40天的天气情况，包括温度、湿度、日夜风向等。'''
        t = int(time.time()*1000)
        city_id = self.get_city_id(name, parent)
        key = self.sign(self.latest_40days_weather_password, t, city_id)
        params: dict[str, str|int] = {
            "cityId": city_id,
            "timestamp": t,
            "token": self.latest_40days_weather_token,
            "key": key,
        }
        async with arequest("GET", self.API_ADDR, params=params) as resp:
            resp.raise_for_status()
            data =  await resp.text()
        ret_dict = json.loads(data)
        ret = CommonResp[DailyResp](**ret_dict)
        if ret.code!= 0:
            raise APIErrCode(ret.code, ret.msg)
        if ret.rc != None and ret.rc.c!= 0:
            raise APIErrCode(ret.rc.c, ret.rc.p)
        return ret

    def sign(self, password: str, timestamp: int, city_id: int) -> str:
        # key = MD5(password+timestamp+cityId)
        import hashlib
        m = hashlib.md5()
        m.update((password + str(timestamp) + str(city_id)).encode('utf-8'))
        return m.hexdigest()

    def get_city_id(self, name: str, parent: str) -> int:
        con = self._connect_db()
        cur = con.cursor()
        query = "name=?"
        param = [name, ]
        if parent != "":
            query += " AND (parent_name=? OR province=? OR country_name=?)"
            param.extend([parent, parent, parent])
        cur.execute("SELECT city_id FROM city WHERE " + query, param)
        result = cur.fetchone()
        if result is None or len(result) == 0:
            raise ValueError(f"name {parent}/{name} not found")
        return result[0]

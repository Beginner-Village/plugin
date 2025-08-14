
from typing import List, Annotated
import os
import json
import hashlib
import base64
from urllib.parse import quote
from pathlib import Path
from pydantic import Field
from hiagent_plugin_sdk import BasePlugin, set_meta, SecretField, BuiltinCategory, arequest
from hiagent_plugin_kuaidiniao.express_query import ExpressQueryResult

current_dir = Path(os.path.dirname(os.path.abspath(__file__)))

class APIErrCode(Exception):
    def __init__(self, reason: str):
        super().__init__(f"API error: message={reason}")

@set_meta(cn_name="快递鸟")
class KuaidiniaoPlugin(BasePlugin):
    """国内快递查询，根据快递单号查询快递状态。"""

    hiagent_tools = ["ExpressDelivery"]
    hiagent_category = BuiltinCategory.Logistics

    def __init__(self,
        app_id: Annotated[str, Field(description="申请说明: https://www.yuque.com/kdnjishuzhichi/tcyzry/rseipuo10h6dktqv")],
        app_key: Annotated[str, SecretField(description="申请说明: https://www.yuque.com/kdnjishuzhichi/tcyzry/rseipuo10h6dktqv")],
    ) -> None:
        self.app_id = app_id
        self.app_key = app_key

    @classmethod
    def _icon_uri(cls) -> str:
        return f"file://{current_dir}/icon.png"

    # doc https://www.yuque.com/kdnjishuzhichi/dfcrg1/tb8nyy
    async def ExpressDelivery(self,
        LogisticCode: Annotated[str, Field(title="快递单号", description="快递单号")],
        CustomerName: Annotated[str, Field("", description="寄件人或收件人手机号后四位，查询顺丰快递必填")] = "",
    ) -> ExpressQueryResult:
        """根据快递单号查询快递状态，返回值为空代表未查到快递信息，请检查快递单号是否正确"""
        url = "https://api.kdniao.com/Ebusiness/EbusinessOrderHandle.aspx"
        biz_params = {
            "LogisticCode": LogisticCode,
        }
        if CustomerName != "":
            biz_params["CustomerName"] = CustomerName

        form_data = {
            "RequestData": json.dumps(biz_params),
            "RequestType": 8002,
            "DataType": 2,
            "DataSign": sign_data(biz_params, self.app_key),
            "EBusinessID": self.app_id,
        }
        async with arequest("POST", url, data=form_data) as resp:
            ret_raw =  await resp.text()
        # print(ret_raw)
        ret_dict = json.loads(ret_raw)
        ret =  ExpressQueryResult(**ret_dict)
        return ret



def sign_data(data: dict, api_key: str) -> str:
    sign_data = f"{json.dumps(data)}{api_key}"
    s2 = hashlib.md5(sign_data.encode()).hexdigest()
    s3 = base64.b64encode(s2.encode()).decode()
    s4 = quote(s3)
    return s4

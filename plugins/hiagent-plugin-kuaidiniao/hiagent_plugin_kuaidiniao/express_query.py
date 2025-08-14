from typing import List
from pydantic import BaseModel, Field

StateExDesc = """0-暂无轨迹信息
1-已揽收
2-在途中
 201-到达派件城市
 204-到达转运中心
 205-到达派件网点
 206-寄件网点发件
 202-派件中
 211-已放入快递柜或驿站
3-已签收
 301-正常签收
 302-轨迹异常后最终签收
 304-代收签收
 311-快递柜或驿站签收
4-问题件
 401-发货无信息
 402-超时未签收
 403-超时未更新
 404-拒收(退件)
 405-派件异常
 406-退货签收
 407-退货未签收
 412-快递柜或驿站超时未取
 413-单号已拦截
 414-破损
 415-客户取消发货
 416-无法联系
 417-配送延迟
 418-快件取出
 419-重新派送
 420-收货地址不详细
 421-收件人电话错误
 422-错分件
 423-超区件
5-转寄
6-清关
 601-待清关
 602-清关中
 603-已清关
 604-清关异常
10-待揽件"""

class TraceInfo(BaseModel):
    """物流轨迹信息"""
    AcceptTime: str = Field("", title="轨迹发生时间")
    AcceptStation: str = Field("", title="轨迹描述")
    Location: str = Field("", title="历史节点所在城市")
    Action: str = Field("", title="物流状态编码", description=StateExDesc)
    Remark: str = Field("", title="物流备注")

class ExpressQueryResult(BaseModel):
    """快递查询结果"""
    EBusinessID: str = Field("", title="用户ID")
    ShipperCode: str = Field("", title="快递公司编码")
    LogisticCode: str = Field("", title="快递单号")
    Success: bool = Field(False, title="成功与否(true/false)")
    Reason: str | None = Field("", title="失败原因")
    State: str = Field("", title="普通物流状态", description="0-暂无轨迹信息 1-已揽收 2-在途中 3-签收 4-问题件 5-转寄 6-清关")
    StateEx: str = Field("", title="物流状态编码", description=StateExDesc)
    Location: str = Field("", title="当前所在城市")
    Traces: List[TraceInfo] = Field([], title="物流轨迹信息")

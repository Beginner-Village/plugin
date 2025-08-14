from pydantic import BaseModel, Field
from typing import List
from hiagent_plugin_tianyancha.common import timestamp_to_str

class AbnormalOperationItem(BaseModel):
    """
    返回值字段	字段类型	字段说明	备注
    removeDate	String	日期	移出日期
    putReason	String	varchar(4091)	列入异常名录原因
    putDepartment	String	varchar(200)	决定列入异常名录部门(作出决定机关)
    removeDepartment	String	varchar(200)	移出部门
    removeReason	String	varchar(4091)	移除异常名录原因
    putDate	String	日期	列入日期
    """
    removeDate: str | None = Field(None, description="移出日期")
    putReason: str | None = Field(None, description="列入异常名录原因")
    putDepartment: str | None = Field(None, description="决定列入异常名录部门(作出决定机关)")
    removeDepartment: str | None = Field(None, description="移出部门")
    removeReason: str | None = Field(None, description="移除异常名录原因")
    putDate: str | None = Field(None, description="列入日期")

    def __init__(self, **data):
        # for key in ["removeDate", "putDate"]:
        #     data[key] = timestamp_to_str(data.get(key))
        super().__init__(**data)

class AbnormalOperationResult(BaseModel):
    """
    返回值字段	字段类型	字段说明	备注
    total	Number	int(11)	总数
    items	Array		新闻列表
    """
    total: int = Field(0, description="总数")
    items: List[AbnormalOperationItem] = Field([], description="列表")

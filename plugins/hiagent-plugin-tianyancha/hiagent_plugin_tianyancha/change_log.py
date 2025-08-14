from pydantic import BaseModel, Field
from typing import List
from hiagent_plugin_tianyancha.common import timestamp_to_str

class ChangeLogItem(BaseModel):
    """
    返回值字段	字段类型	字段说明	备注
    changeItem	String	varchar（4091）	变更事项
    createTime	String	日期	创建时间
    contentBefore	String	mediumtext	变更前
    contentAfter	String	mediumtext	变更后
    changeTime	String	日期	变更时间
    """
    changeItem: str | None = Field(None, description="变更事项")
    createTime: str | None = Field(None, description="创建时间")
    contentBefore: str | None = Field(None, description="变更前")
    contentAfter: str | None = Field(None, description="变更后")
    changeTime: str | None = Field(None, description="变更时间")

    def __init__(self, **data):
        # 处理时间字段
        # for key in ["createTime", "changeTime"]:
        #     data[key] = timestamp_to_str(data.get(key))
        super().__init__(**data)

class ChangeLogResult(BaseModel):
    """
    返回值字段	字段类型	字段说明	备注
    total	Number	int(11)	总数
    items	Array		新闻列表
    """
    total: int = Field(0, description="总数")
    items: List[ChangeLogItem] = Field([], description="列表")

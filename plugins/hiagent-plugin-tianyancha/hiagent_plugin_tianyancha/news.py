from pydantic import BaseModel, Field
from typing import List
from hiagent_plugin_tianyancha.common import timestamp_to_str


class NewsItem(BaseModel):
    """
    返回值字段	字段类型	字段说明	备注
    website	String	varchar(20)	数据来源
    abstracts	String	varchar(2048)	简介
    docid	String	varchar(255)	新闻唯一标识符
    rtm	Number	时间戳	发布时间
    title	String	varchar(200)	标题
    uri	String	varchar(300)	新闻url
    tags	Array	text	标签
      _child	String	varchar(50)	标签
    emotion	Number	int(11)	情感分类（1-正面，0-中性，-1-负面）
    """
    website: str | None = Field(None, description="数据来源")
    abstracts: str | None = Field(None, description="简介")
    docid: str | None = Field(None, description="新闻唯一标识符")
    # rtm: int | None = Field(None, description="发布时间戳", exclude=True)
    rtm: str = Field("", description="发布时间")
    title: str | None = Field(None, description="标题")
    uri: str | None = Field(None, description="新闻url")
    tags: List[str] | None = Field(None, description="标签")
    emotion: int | None = Field(None, description="情感分类（1-正面，0-中性，-1-负面）")

    def __init__(self, **data):
        # 处理rtm字段
        data["rtm"] = timestamp_to_str(data.get("rtm"))
        super().__init__(**data)


class NewsResult(BaseModel):
    """
    返回值字段	字段类型	字段说明	备注
    total	Number	int(11)	总数
    items	Array		新闻列表
    """
    total: int = Field(0, description="总数")
    items: List[NewsItem] = Field([], description="新闻列表")

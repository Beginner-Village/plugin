from pydantic import BaseModel, Field

class TrailerList(BaseModel):
    string: list[str] = Field([])
    type: str = Field(None)

class ShowVersion(BaseModel):
    string: list[str]

class Show(BaseModel):
    background: str = Field(None, description="背景图片")
    company: str = Field(None, description="厂商")
    country: str = Field(None, description="国家")
    description: str = Field(None, description="详情")
    director: str = Field(None, description="出品")
    duration: int = Field(None, description="时长")
    highlight: str = Field(None, description="重点信息")
    language: str = Field(None, description="语言")
    leader: str = Field(None, description="导演")
    name: str = Field(None, description="片名")
    name_en: str = Field(None, description="片名")
    open_day: str = Field(None, description="上映日期")
    poster: str = Field(None, description="海报")
    remark: str = Field(None, description="评分")

    show_code: str = Field(None, description="影片CODE")
    show_id: str = Field(None, description="影片ID")
    show_mark: str = Field(None, description="影片标记")
    type: str = Field(None, description="影片类型")
    show_versions: ShowVersion = Field(None, description="影片版本")
    trailer_list: TrailerList = Field(None, description="海报")
    status: str = Field(None, description="状态， 1为正常")

class ReturnValue(BaseModel):
    show: list[Show] = Field([])

class FilmOpenShowNowAndSoonGetResponse(BaseModel):
    count: int = Field(0)
    return_value: ReturnValue = Field(None)
    request_id: str = Field("")
    return_code: str = Field("")
    error_response: str = Field(None)

class RespWrapper(BaseModel):
    film_open_show_nowandsoon_get_response: FilmOpenShowNowAndSoonGetResponse = Field(None)
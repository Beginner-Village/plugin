from typing import List
from pydantic import BaseModel, Field

class ImageResult(BaseModel):
    """插件返回内容"""
    image_url: str
    rephraser_result: str = ""
    pe_result: str = ""

class VolcRespData(BaseModel):
    binary_data_base64: List[str]
    rephraser_result: str = ""
    pe_result: str = ""
    request_id: str = ""

class VolcResp(BaseModel):
    message: str
    code: int
    data: VolcRespData = Field(None)

class VolcAPIException(Exception):
    def __init__(self, code: int, message: str, ):
        self.message = message
        self.code = code
        super().__init__(f"VolcAPI error[{code}]: {message}")

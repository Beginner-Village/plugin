from typing import Literal
from pydantic import BaseModel, Field

class Dimension(BaseModel):
    sheetId: str = Field(description="电子表格工作表的 ID")
    majorDimension: Literal["ROWS", "COLUMNS"] = Field(description="维度。取值范围：ROWS、COLUMNS")
    length: int = Field(description="要增加的行数或列数。")

class AddRowsOrColumnsRespBody(BaseModel):
    addCount: int = Field(description="增加的行数或列数")
    majorDimension: Literal["ROWS", "COLUMNS"] = Field(description="维度。取值范围：ROWS、COLUMNS")
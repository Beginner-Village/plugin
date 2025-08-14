from typing import Literal, List
from pydantic import BaseModel, Field

class ValueRow(BaseModel):
    values: List[str] = Field(description="行数据")
class ValueRangeUpdate(BaseModel):
    range: str = Field(description="数据的范围。格式为 <sheetId>!<开始位置>:<结束位置>。")
    # 平台不支持这种数据类型
    # values: List[List[str|int|float]] = Field(None, description="指定范围中的数据")
    # 补充字段, 用于平台不支持类型的改写
    rowValues: List[ValueRow] = Field(None, description="指定范围中的数据")


class ValueRange(ValueRangeUpdate):
    majorDimension: Literal["ROWS", "COLUMNS"] = Field(description="维度。取值范围：ROWS、COLUMNS")
    revision: int = Field(description="工作表的版本号。从 0 开始计数，更新一次版本号加一")

class ValueRangeRespBody(BaseModel):
    revision: int = Field(description="工作表的版本号。从 0 开始计数，更新一次版本号加一")
    spreadsheetToken: str = Field(description="表格的 token")
    valueRange: ValueRange = Field(description="读取的值与范围")

class WriteValueRespBody(BaseModel):
    revision: int = Field(description="工作表的版本号。从 0 开始计数，更新一次版本号加一")
    spreadsheetToken: str = Field(description="表格的 token")
    updatedCells: int = Field(description="写入的单元格总数")
    updatedColumns: int = Field(description="写入的列数")
    updatedRows: int = Field(description="写入的行数")
    updatedRange: str = Field(description="数据的范围。格式为 <sheetId>!<开始位置>:<结束位置>。")

from typing import Any, Generic, TypeVar
from pydantic import BaseModel, Field
from dataclasses import dataclass
import logging
import traceback

logger = logging.getLogger(__name__)

class HttpError(BaseModel):
    code: str
    message: str
    data: dict[str, Any] | None = None
    http_code: int = 500

    def __repr__(self):
        return f"{self.code}: {self.message}"

    @classmethod
    def from_exception(cls, e: Exception) -> "HttpError":
        traceback.print_exc()
        logger.info(f"from_exception: {e}, is HttpException: {isinstance(e, HttpException)}")
        if isinstance(e, HttpException):
            return HttpError(
                code=e.code,
                message=e.message,
                data=e.data,
                http_code=e.http_code,
            )
        from pydantic import ValidationError
        if isinstance(e, ValidationError):
            data = {}
            for error in e.errors():
                field = error["loc"][0]
                data[f"{field}"] = error["msg"]
            return HttpError(
                code=e.__class__.__name__,
                message=str(e),
                data=data,
                http_code=422,
            )
        from fastapi.exceptions import RequestValidationError
        if isinstance(e, RequestValidationError):
            data = {}
            for error in e.errors():
                field = error["loc"][0]
                data[f"{field}"] = error["msg"]
            return HttpError(
                code=e.__class__.__name__,
                message=str(e),
                data=data,
                http_code=422,
            )
        ret = HttpError(
            code=e.__class__.__name__,
            message=str(e),
            data={},
            http_code=500,
        )
        return ret


class HttpException(Exception):
    def __init__(self, code: str, message: str, data: dict[str, Any] | None = None, http_code: int = 500):
        self.code = code
        self.message = message
        self.data = data
        self.http_code = http_code
        super().__init__(f"{code}: {message}")


    @classmethod
    def from_exception(cls, e: Exception) -> "HttpException":
        traceback.print_exc()
        logger.info(f"from_exception: {e}, is HttpError: {isinstance(e, HttpException)}")
        if isinstance(e, HttpException):
            return e
        ret = HttpException(
            code=e.__class__.__name__,
            message=str(e),
            data={},
            http_code=500,
        )
        return ret

T = TypeVar('T')

class CommonResponse(BaseModel, Generic[T]):
    data: T | None = None
    error: HttpError | None = None

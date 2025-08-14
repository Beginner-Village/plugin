import time
import logging
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, Response
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError
from app.schema.common import HttpException, HttpError

from app.api.v1 import api_v1, root

def handle_exception(request: Request, e: Exception):
    err = HttpError.from_exception(e)
    return JSONResponse(
        status_code=err.http_code,
        content={
            "error": {
                "code": err.code,
                "message": err.message,
                "data": err.data,
                "http_code": err.http_code,
            }
        },
    )

def init_exception_handler(app: FastAPI):
    @app.exception_handler(HttpException)
    def http_error_handler(request: Request, e: HttpException):
        return handle_exception(request, e)

    @app.exception_handler(ValidationError)
    def validation_error_handler(request: Request, e: ValidationError):
        return handle_exception(request, e)

    @app.exception_handler(RequestValidationError)
    def request_validation_error_handler(request: Request, e: RequestValidationError):
        return handle_exception(request, e)

    @app.exception_handler(Exception)
    def common_handler(request: Request, e: Exception):
        return handle_exception(request, e)

app = FastAPI()
init_exception_handler(app)

app.include_router(root)
app.include_router(api_v1, prefix="/v1")

trace_logger = logging.getLogger("trace")

@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    req_id = request.headers.get("X-Request-ID", "")
    trace_logger.debug(f"start [{req_id}] {request.method}:{request.url.path}")
    start_time = time.perf_counter()
    response: Response = await call_next(request)
    process_time = time.perf_counter() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    trace_logger.info(f"finish [{req_id}] {request.method}:{request.url.path} status_code={response.status_code}, cost={process_time:.3f}")
    return response

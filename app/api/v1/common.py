from typing import Annotated, AsyncGenerator, Any
import logging

from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse

api_v1 = APIRouter()

root = APIRouter()

@root.get("/ping")
async def ping():
    # import logging
    # from hiagent_plugin_sdk import secretLogger

    # logging.info("hello")
    # logging.warning("hello")
    # logging.error("hello")
    # logging.critical("hello")

    # secretLogger.info("secret")
    # secretLogger.warning("secret")
    # secretLogger.error("secret")
    # secretLogger.critical("secret")
    return JSONResponse(content={"message": "pong"})

@root.get("/loggingLevel")
async def set_logging_level(
    level: Annotated[str, Query(embed=True)],
    logger: Annotated[str|None, Query(embed=True)] = None,
):
    logging.getLogger(logger).setLevel(level)
    logging.debug("debug log")
    logging.info("info log")
    logging.warning("warning log")
    logging.error("error log")
    logging.critical("critical log")
    return JSONResponse(content={"message": "ok"})

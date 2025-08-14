
from typing import Annotated

from fastapi import Body

from app.api.v1.common import api_v1
from app.schema.common import CommonResponse
from app.package_mgr import delete_pkg
from app.runtime.sock_client import default_manager


@api_v1.post("/DeletePackage")
def delete_package(
    pkg: Annotated[str, Body(embed=True)],
    version: Annotated[str, Body(embed=True)]
) -> CommonResponse[None]:
    """删除插件"""
    default_manager.stop_process(pkg, version)
    delete_pkg(pkg, version)
    return CommonResponse(data=None)

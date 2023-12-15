import json
import logging
import os
import sys
import uuid
from typing import Optional, Union
from pydantic import BaseModel, field_validator, ValidationError
from starlette.responses import Response
from utils import responses_serializer as res
from fastapi import APIRouter
from starlette.requests import Request
from models import exec_base_sql_order
from utils import crypto
from utils.crypto import encrypt_password

router = APIRouter()

logging.getLogger().setLevel(logging.INFO)
logging.debug("debug")


class UsernamePasswordVerify(object):
    def __init__(self, username: str, password: str):
        self.username = username
        self.password = password

    def verify(self):
        logging.info(f"username: {self.username}, password: {self.password}")
        sql = f"SELECT * from user where username = '{self.username}'"
        obj = exec_base_sql_order(sql).exec_sql()
        try:
           obj = obj[3]
        except:
            raise ValueError("Invalid username")
        if obj:
            logging.info(obj)
            if crypto.verify_password(self.password, bytes(obj, encoding="utf-8")):
                return True
        else:
            raise ValueError("Invalid username or password")


class GetUserRequestModel(BaseModel):
    user_id: str

    @field_validator("user_id")
    def check_user_id(cls, v):
        # pattern = r"^[0-9a-f]{32}$"
        try:
            if uuid.UUID(str(v)).version == 4:
                return v
            else:
                raise ValueError("Invalid user_id")
        except ValueError:
            raise ValueError("Invalid user_id")

    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "f6d8e8e8-7f1a-4b6e-8f1a-6f8f8f8f8f8f"
            }
        }


@router.post(path="/user/info", tags=["users"], summary="获取用户信息", description="获取用户信息",
             response_model=res.BaseResponse)
async def get_user_info(param: GetUserRequestModel, request: Request = None) -> Union[Response, Response]:
    """
    获取用户信息 只允许API调用且只有Post方法
    :param 请求体
    - :param user_id: 用户的独立ID
    :rtype: Union[Response, Response]
    :raises: 404 / 500
    :returns: Error Message / User Info
    :return: Response
    """
    sql = f"SELECT * from user where id = '{param.user_id}'"
    obj = exec_base_sql_order(sql, 'user_model_serializers').exec_sql()
    if obj:
        result = obj
        response = res.BaseResponse(request_id=request.state.request_id, status="ok", result=result)
        return Response(
            status_code=200,
            content=response.model_dump_json(exclude_none=True, by_alias=True, exclude_unset=True)
        )
    else:
        response = res.ErrorHandler(request_id=request.state.request_id, code=10320, status="error", msg="Result Not Found")
        return Response(
            status_code=404,
            content=response.model_dump_json(exclude_none=True, by_alias=True, exclude_unset=True)
        )


class VerifyUserInfo(BaseModel):
    username: str
    password: str

    class Config:
        json_schema_extra = {
            "example": {
                "username": "foo",
                "password": "bar"
            }
        }


@router.post(path="/user/verify", tags=["users"], summary="验证用户信息", description="验证用户信息",
             response_model=res.BaseResponse)
async def verify_user_info(param: VerifyUserInfo, request: Request = None) -> Union[Response, Response]:
    """
    验证用户信息 只允许API调用且只有Post方法
    :param 请求体
    - :param username: 用户名
    - :param password: 密码
    :rtype: Union[Response, Response]
    :raises: 404 / 500
    :returns: Error Message / User Info
    :return: Response
    """
    try:
        setattr(UsernamePasswordVerify, "username", param.username)
        setattr(UsernamePasswordVerify, "password", param.password)
    except:
        raise ValueError("Invalid username or password")
    verify = UsernamePasswordVerify(param.username, param.password)
    try:
        f = verify.verify()
    except ValueError:
        response = res.ErrorHandler(request_id=request.state.request_id, code=10320, status="error",
                                    msg="Invalid username or password")
        return Response(
            status_code=404,
            content=response.model_dump_json(exclude_none=True, by_alias=True, exclude_unset=True)
        )
    if f:
        response = res.BaseResponse(request_id=request.state.request_id, status="ok", result="success")
        return Response(
            status_code=200,
            content=response.model_dump_json(exclude_none=True, by_alias=True, exclude_unset=True)
        )
    else:
        response = res.ErrorHandler(request_id=request.state.request_id, code=10320, status="error",
                                    msg="Invalid Password")
        return Response(
            status_code=404,
            content=response.model_dump_json(exclude_none=True, by_alias=True, exclude_unset=True)
        )

import logging
import uuid
from datetime import datetime, timedelta
from typing import Union
from jose import jwt
from pydantic import BaseModel, field_validator
from starlette.responses import Response
from utils import responses_serializer as res
from fastapi import APIRouter
from starlette.requests import Request
from models.UserModel import exec_base_sql_order
from utils import crypto

router = APIRouter()

logging.getLogger().setLevel(logging.INFO)
logging.debug("debug")


class UsernamePasswordVerify(object):
    def __init__(self, username: str, password: str):
        self.username = username
        self.password = password

    def verify(self):
        sql = f"SELECT * from user where username = '{self.username}'"
        obj = exec_base_sql_order(sql).exec_sql()
        try:
            obj = obj[3]
        except:
            raise ValueError("Invalid username")
        if obj:
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
        response = res.ErrorHandler(request_id=request.state.request_id, code=10320, status="error",
                                    msg="Result Not Found")
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


@router.post(path="/user/login", tags=["users"], summary="用户登录", description="用户登录",
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
        sql = f"SELECT * from user where username = '{param.username}'"
        obj = exec_base_sql_order(sql, 'user_model_serializers').exec_sql()
        result = obj
        response = res.BaseResponse(request_id=request.state.request_id, status="ok", msg="success", result=result)
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


class Token(BaseModel):
    user_id: str
    access_token: str
    token_type: str


class GenerateTokenData(BaseModel):
    username: str
    password: str
    expires_delta: int


@router.post("/token/generate", response_model=Token)
def create_access_token(data: GenerateTokenData, request: Request):
    Algorithm = "HS256"
    SECRET_KEY = "kxs7qyv=@&scg$k75@(ri+mn8%57_@$nl==kcz_gagqs7j5r1y"
    verify_user_info(data.username, data.password)
    to_encode = data.model_copy()
    if data.expires_delta:
        expire = datetime.utcnow() + timedelta(data.expires_delta)
    else:
        if type(data.expires_delta) is int:
            expire = datetime.utcnow() + timedelta(seconds=data.expires_delta)
        elif type(data.expires_delta) is float:
            expire = datetime.utcnow() + timedelta(seconds=int(data.expires_delta))
        else:
            expire = datetime.utcnow() + timedelta(seconds=300)
        expire = datetime.utcnow() + timedelta(expire)
    # to_encode.update({"exp": expire}) # 过期时间
    encoded_jwt = jwt.encode(claims={"time_claim": str(datetime.now())}, key=SECRET_KEY, algorithm=Algorithm)
    response = res.BaseResponse(request_id=request.state.request_id, status="ok", msg=f"expires: {expire}",
                                result=encoded_jwt)
    # 设置cookie
    return Response(
        status_code=200,
        content=response.model_dump_json(exclude_none=True, by_alias=True, exclude_unset=True),
        headers={"Set-Cookie": f"token={encoded_jwt}; Path=/; Expires={expire}; HttpOnly"}
    )

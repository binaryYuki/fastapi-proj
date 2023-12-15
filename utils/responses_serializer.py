import json
import logging
from typing import Any, Optional, Union

from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()


class ErrorHandler(BaseModel):
    """
    错误返回json
    :param request_id: 请求id
    :param code: 错误码
    :param status: 错误状态
    :param msg: 错误信息
    :param data: 错误数据 / 可选
    :return: json
    """
    request_id: str
    code: int
    status: str
    msg: Optional[str]  # 这个Optional是pydantic的一个特性，表示这个字段可以为空
    data: Optional[Any]

    def __init__(self, request_id: str, code: int, status: str, msg: str, data: Any = None):
        super().__init__(request_id=request_id, code=code, status=status, msg=msg, data=data)
        self.request_id = request_id
        self.code = code
        self.status = status
        self.msg = msg
        self.data = data

    def __str__(self):
        return json.dumps(self.model_dump_json())

    class Config:
        json_schema_extra = {
            "example": {
                "request_id": "aa7fa607edaa44f6",
                "code": 10320,
                "status": "error",
                "msg": "Invalid username or password"
            }
        }


class BaseResponse(BaseModel):
    request_id: str
    code: int
    status: str
    msg: Optional[str]
    data: Optional[Any]

    @staticmethod
    def define_data(result: Any) -> Any:
        """
        定义data字段
        :param result: 返回结果
        :return: data
        """
        if result is None:
            return None
        else:
            return result

    def __init__(self, request_id: str, status: str, result: Union[str, dict], code: int = 200,
                 msg: Optional[str] = None):
        super().__init__(request_id=request_id, code=code, status=status, msg=msg, data=result)

    def __str__(self):
        return self.model_dump_json(indent=4)

    class Config:
        json_schema_extra = {
            "example": {
                "request_id": "b7b26c54448e430f",
                "code": 200,
                "status": "ok",
                "data": {
                    "id": "036c75a8-fe43-4ae1-9cf2-f36db8d83289",
                    "avatar": "https://avatars.githubusercontent.com/u/60097976?s=400&u"
                              "=46206cff80830b3e6e2d04154b9c75a0a156c056&v=4",
                    "username": "root",
                    "email": "root@localhost",
                    "role": "admin",
                    "is_active": 1,
                    "APP_NAME": "",
                    "APP_ID": "",
                    "APP_SECRET": "",
                    "APP_URL": "",
                    "APP_ENABLED": 0,
                    "APIKEY": "",
                    "APIKEY_ENABLED": 0,
                    "APIKEY_EXPIRATION": ""
                }
            }

        }


class ServerHealthResponseSerializer(BaseModel):
    """
    服务器健康检查返回json
    :param request_id: 请求id
    :param code: 错误码
    :param status: 错误状态
    :param msg: 错误信息
    :param data: 错误数据 / 可选
    :return: json
    """
    request_id: str
    code: int
    status: str
    msg: Optional[str]  # 这个Optional是pydantic的一个特性，表示这个字段可以为空
    data: Optional[Any]

    def __init__(self, request_id: str, code: int, status: str, msg: str, data: Any = None):
        super().__init__(request_id=request_id, code=code, status=status, msg=msg, data=data)
        self.request_id = request_id
        self.code = code
        self.status = status
        self.msg = msg
        self.data = data

    def __str__(self):
        return json.dumps(self.model_dump_json())

    class Config:
        json_schema_extra = {
            "example": {
                "request_id": "aa7fa607edaa44f6",
                "code": 10320,
                "status": "error",
                "msg": "Invalid username or password"
            }
        }

import json
import os
import sys
from os import environ
import redis.asyncio as redis
import uvicorn
from fastapi import Depends
from fastapi_limiter import FastAPILimiter
from fastapi_limiter.depends import RateLimiter
from pydantic import ValidationError
from utils.middleware import LogRequestsMiddleware
from routers import users
from starlette.requests import Request
from tzlocal import get_localzone_name
from datetime import datetime
import utils.responses_serializer as res
from starlette.responses import JSONResponse, Response
from dotenv import load_dotenv
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware  # 强制转换为https
import logger
from models import create_root_user
from logging import getLogger
from fastapi import FastAPI
from starlette.exceptions import HTTPException as StarletteHTTPException
from fastapi.exceptions import RequestValidationError

load_dotenv()

logging = getLogger(__name__)

app = FastAPI()

app.include_router(users.router, prefix="/api/v1")


async def init_while_startup():
    try:
        await create_root_user()
    except Exception as e:
        logging.critical("failed when initializing root user")
        logging.error('error traceback: %s' % e)
        sys.exit("The server failed to start, please check your database connection")
        # todo: redis流控
    try:
        redis1 = redis.from_url(os.environ.get("REDIS_URL"), encoding="utf-8", decode_responses=True)
        await FastAPILimiter.init(redis1)
    except Exception as e:
        print(e)


@app.on_event("startup")
async def startup_event():
    await init_while_startup()


# todo: 转换为生产环境时，需要将下面的注释去掉
# app.add_middleware(HTTPSRedirectMiddleware)  # 强制转换为https
app.add_middleware(LogRequestsMiddleware)


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = exc.errors()
    info = None
    for error in errors:
        error_type = error["type"]
        # error_type有两种，value_error和type_error还有一种是missing
        if error_type == "value_error":
            info = res.ErrorHandler(request_id=request.state.request_id, code=10012, status="error",
                                    msg="Invalid Parameters",
                                    data=error["msg"])
        elif error_type == "type_error":
            info = res.ErrorHandler(request_id=request.state.request_id, code=10012, status="error",
                                    msg="Invalid Parameters",
                                    data=error["msg"])
        else:
            info = res.ErrorHandler(request_id=request.state.request_id, code=10012, status="error",
                                    msg=f"Invalid Parameters",
                                    data=error["msg"])
    return Response(
        status_code=400,
        content=info.model_dump_json(exclude_none=True, by_alias=True, exclude_unset=True)
    )


app.add_exception_handler(RequestValidationError, validation_exception_handler)


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc):
    """
    :param exc:
    :type request: object
    """
    request_id = request.state.request_id
    logging.error(f"request_id={request_id} error={exc}")
    response = res.ErrorHandler(request_id=request_id, code=exc.status_code, status="error", msg=exc.detail)
    return Response(
        status_code=400,
        content=response.model_dump_json(exclude_none=True, by_alias=True, exclude_unset=True)
    )


@app.exception_handler(ValidationError)
async def validation_exception_handler(request: Request, exc: ValidationError):
    """
    :param exc: pydantic返回的错误
    :type request: object
    """
    request_id = request.state.request_id
    logging.error(f"request_id={request_id} error={exc}")
    response = res.ErrorHandler(request_id=request_id, code=10012, status="error", msg="Invalid Parameters",
                                data=exc.errors())
    return Response(
        status_code=400,
        content=response.model_dump_json(exclude_none=True, by_alias=True, exclude_unset=True)
    )


@app.get("/health", dependencies=[Depends(RateLimiter(times=2, seconds=5))])
async def health(request: Request):
    content = {
        "server_status": "ok",
        "server_timezone": get_localzone_name(),
        "server_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "version": environ.get("VERSION")
    }
    response = res.BaseResponse(request_id=request.state.request_id, status="ok", result=content)
    return Response(
        status_code=200,
        content=response.model_dump_json(exclude_none=True, by_alias=True, exclude_unset=True)
    )


@app.get("/")
async def root(request: Request):
    response = res.ErrorHandler(request_id=request.state.request_id, code=404, status="error", msg="")
    return Response(
        status_code=405,
        content=response.model_dump_json(exclude_none=True, by_alias=True, exclude_unset=True)
    )


if __name__ == '__main__':
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info", lifespan="on", loop="asyncio", use_colors=True)

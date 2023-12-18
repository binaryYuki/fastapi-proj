from starlette.requests import Request
from utils.responses_serializer import BaseResponse as res
import models.GptacUserModel as ac
from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()


@router.post("/gptac/user/list")
async def gptac_user_list():
    f = ac.get_all()
    return f


class CreateUserModel(BaseModel):
    username: str
    password: str
    email: str


@router.post("/gptac/user/create")
async def gptac_user_create(data: CreateUserModel, request: Request, response_model=res):
    data = ac.create_user(data.username, data.password, data.email)
    response_model.request_id = request.state.request_id
    response_model.code = 200
    response_model.message = "success"
    response_model.data = data
    return response_model

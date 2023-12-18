import os
import uuid
from os import environ
from typing import Any, Dict, Optional, Union

from sqlmodel.main import IncEx
from typing_extensions import Literal

from dotenv import find_dotenv, load_dotenv
from sqlmodel import Field, Session, SQLModel, create_engine, select
import logging

load_dotenv(find_dotenv())


# 需要一个username和password的储存表 并且该表要支持list_all(列出所有用户和密码）和get_user_info(获取用户信息）

# 以下是SQLModel的模型
class GPTUser(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str
    password: str
    email: str


default_root_user = GPTUser(
    username="root",
    password=environ.get("ROOT_PASSWORD"),
    email="admin@example.com"
)
# create the database
if environ.get("SQLALCHEMY_ECHO") == "True":
    engine = create_engine(environ.get("DATABASE_URL"), echo=True)
else:
    engine = create_engine(environ.get("DATABASE_URL"))


# 以下是SQLModel的模型
async def init_gpatc():
    """
    创建root用户 只对User模型有效
    :return: Traceback
    """
    try:
        # 创建数据库
        SQLModel.metadata.create_all(engine)
        # 尝试从数据库中找用户名为root的用户
        with Session(engine) as session:
            root_exists = select(GPTUser).where(GPTUser.username == "admin")
            root_exists = session.exec(root_exists).first()
            if root_exists is None:
                print("root user not detected, creating one")
                session.add(default_root_user)
                session.commit()
                print("GPTUSER: root user created")
            else:
                print("GPTUSER: root user detected, skipping")
    except Exception as e:
        logging.critical("failed when initializing root user")
        logging.critical("please check your database connection")
        logging.critical('error traceback: %s' % e)


def create_user(username: str, password: str, email: str):
    # 创建用户
    with Session(engine) as session:
        user = GPTUser(username=username, password=password, email=email)
        session.add(user)
        session.commit()


def get_all():
    # 导出所有数据
    with Session(engine) as session:
        statement = select(GPTUser)
        users = session.exec(statement).all()  # 这个代码的意思是从数据库中导出所有数据
    return users


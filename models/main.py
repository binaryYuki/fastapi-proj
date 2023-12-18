import sys
from os import environ

from sqlalchemy import create_engine
from sqlmodel import SQLModel

import models.GptacUserModel as ac
import models.UserModel as user

# create the database
if environ.get("SQLALCHEMY_ECHO") == "True":
    engine = create_engine(environ.get("DATABASE_URL"), echo=True)
else:
    engine = create_engine(environ.get("DATABASE_URL"))
SQLModel.metadata.create_all(bind=engine, checkfirst=True, tables=[user.User.__table__, ac.GPTUser.__table__])


async def main():
    try:  # 初始化数据库
        await ac.init_gpatc()
        await user.create_root_user()
        print("initial db success")
    except Exception as e:
        sys.exit(f"initial db failed, error: {e}"), -1


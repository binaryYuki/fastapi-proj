import uuid
from os import environ
from typing import Optional
from dotenv import load_dotenv, find_dotenv
from sqlmodel import Field, Session, SQLModel, create_engine, select
import logging
from sqlalchemy import text
from utils import crypto

env = load_dotenv(find_dotenv())

logging.info("connecting to database")


def user_id_generator():
    return str(uuid.uuid4())


class User(SQLModel, table=True):
    id: Optional[str] = Field(nullable=False, primary_key=True, index=True, unique=True, default=user_id_generator)
    avatar: Optional[str] = None
    username: str
    password: str
    email: str
    full_name: Optional[str] = None
    role: str
    is_active: bool = True
    APP_NAME: Optional[str] = None
    APP_ID: Optional[str] = None
    APP_SECRET: Optional[str] = None
    APP_URL: Optional[str] = None
    APP_ENABLED: Optional[bool] = None
    APIKEY: Optional[str] = None
    APIKEY_ENABLED: Optional[bool] = None
    APIKEY_EXPIRATION: Optional[str] = None


default_root_user = User(
    id=user_id_generator(),
    avatar="https://avatars.githubusercontent.com/u/60097976?s=400&u=46206cff80830b3e6e2d04154b9c75a0a156c056&v=4",
    username="root",
    password=crypto.encrypt_password(environ.get("ROOT_PASSWORD")),
    email="root@localhost",
    role="admin",
    is_active=True,
    APP_NAME="",
    APP_ID="",
    APP_SECRET="",
    APP_URL="",
    APP_ENABLED=False,
    APIKEY="",
    APIKEY_ENABLED=False,
    APIKEY_EXPIRATION="",
)

# create the database
if environ.get("SQLALCHEMY_ECHO") == "True":
    engine = create_engine(environ.get("DATABASE_URL"), echo=True)
else:
    engine = create_engine(environ.get("DATABASE_URL"))

SQLModel.metadata.create_all(engine)


async def create_root_user():
    """
    创建root用户 只对User模型有效
    :return: Traceback
    """
    try:
        # 尝试从数据库中找用户名为root的用户
        with Session(engine) as session:
            root_exists = select(User).where(User.username == "root")
            root_exists = session.exec(root_exists).first()
            if root_exists is None:
                print("root user not detected, creating one")
                session.add(default_root_user)
                session.commit()
                print(session.refresh(default_root_user))
            else:
                print("root user detected, skipping creation")
                print("You can find your root password in the .env file")
                print("Your server is ready to go!")
    except Exception as e:
        logging.critical("failed when initializing root user")
        logging.critical("please check your database connection")
        logging.critical('error traceback: %s' % e)


class exec_base_sql_order(object):
    """
    执行sql语句的类 用于执行sql语句
    """

    def __init__(self, sql, serializer=None, model=None):
        """
        init 函数 传入sql语句
        :param sql: sql语句
        :param serializer: 序列化器名
        :param model: 模型名 可以为空 保留api
        """
        self.sql = sql
        self.serializer = serializer
        self.model = model
        self.result = None
        self.passwd = None

    def __enter__(self):
        """
        当执行with语句时，会执行这个函数 只执行 没有返回值
        :return:
        """
        self.session = Session(engine)
        self.query = text(self.sql)
        try:
            self.session.exec(self.query)
            self.session.commit()
            return self
        except Exception as e:
            logging.critical("failed when executing sql %s" % self.sql)
            logging.critical("please check your sql syntax")
            logging.critical('error traceback: %s' % e)
            self.session.rollback()
            return self

    def user_model_serializers(self):
        """
        根据model的字段名，将查询结果转换为dict 便于JsonResponse
        :arg: sql语句
        :return:
        """
        result = self.result
        if self.result is None:
            return None
        else:
            return {
                "id": result[0],
                "avatar": result[1],
                "username": result[2],
                # "password": result[3],
                "email": result[4],
                # "full_name": result[5],
                "role": result[6],
                "is_active": result[7],
                "APP_NAME": result[8],
                "APP_ID": result[9],
                "APP_SECRET": result[10],
                "APP_URL": result[11],
                "APP_ENABLED": result[12],
                "APIKEY": result[13],
                "APIKEY_ENABLED": result[14],
                "APIKEY_EXPIRATION": result[15],
            }

    def exec_sql(self):
        with Session(engine) as session:
            query = text(self.sql)
            result = session.exec(query).first()
            logging.info("exec sql %s" % self.sql)
            self.result = result
            if self.serializer is not None:
                return getattr(self, self.serializer)()
            elif self.model is User:
                return self.user_model_serializers()
            else:
                return result


# 自定义区分颜色的logger
# 用法：logger.info('info message')
from logging import getLogger, StreamHandler, Formatter


def info(msg):
    # 绿色的INFO 正常的输出
    handler = StreamHandler()
    handler.setLevel(40)
    handler.setFormatter(Formatter("\033[32m%(asctime)s - %(name)s - %(levelname)s - %(message)s\033[0m"))
    logging = getLogger(__name__)
    logging.addHandler(handler)
    logging.setLevel(10)
    logging.info(msg)
    print("\033[1;36m{}\033[0m".format(msg))


if __name__ == '__main__':
    info("error! runtime error!")


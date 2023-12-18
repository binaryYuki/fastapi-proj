FROM python:3.11-slim

# Update and install required packages
RUN apt-get update -y && apt-get install -y \
    apt-transport-https \
    python3 \
    python3-pip \
    default-libmysqlclient-dev


RUN apt-get install pkg-config -y

RUN pip3 install --upgrade pip
RUN pip3 install mysqlclient

COPY . /app
WORKDIR /app

RUN pip3 install -r requirements.txt

# Copy the current directory contents into the container at /app
# open port 8000
EXPOSE 80

# 安装 Nginx
RUN apt-get update && apt-get install -y nginx

CMD ["bash", "-c", "service nginx start"]

RUN apt-get install -y libnginx-mod-http-headers-more-filter

RUN ln -s /usr/share/nginx/modules-available/mod-http-headers-more-filter.load /etc/nginx/modules-enabled/

RUN systemctl restart nginx

# 设置 Nginx 配置
COPY nginx.conf /etc/nginx/nginx.conf

# 暴露 Nginx 端口
EXPOSE 80

# 启动 FastAPI 应用和 Nginx
CMD ["bash", "-c", "service nginx start && uvicorn main:app --host 0.0.0.0 --port 8080"]

#CMD ["gunicorn", "main:app", "--workers", "4", "--worker-class", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:80"]

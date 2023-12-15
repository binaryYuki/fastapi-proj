FROM python:3.11-slim

# Update and install required packages
RUN apt-get update -y && apt-get install -y \
    apt-transport-https \
    python3 \
    python3-pip \
    default-libmysqlclient-dev \


RUN apt-get install python3-dev default-libmysqlclient-dev build-essential -y

RUN pip3 install --upgrade pip
RUN pip3 install mysqlclient

COPY . /app
WORKDIR /app

# 找不到requirements.txt怎么办  > [6/6] RUN pip3 install -r requirements.txt:
                         #0.294 ERROR: Could not open requirements file: [Errno 2] No such file or directory: 'requirements.txt'
# 解决：在Dockerfile文件中添加COPY . /app 还是没用
# 解决：在Dockerfile文件中添加WORKDIR /app
RUN pip3 install -r requirements.txt

# Copy the current directory contents into the container at /app
# open port 8000
EXPOSE 8000

CMD ["uvicorn", "main:app"]

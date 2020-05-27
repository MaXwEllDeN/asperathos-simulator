FROM python:3

RUN apt update && apt install -y python-pip redis-tools

RUN pip install requests redis

RUN mkdir -p /output/

COPY wrapper.sh /wrapper.sh
COPY src /app

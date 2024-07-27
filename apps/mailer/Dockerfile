FROM python:3.11-alpine

# make sure all messages always reach console
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/opt/deploy

RUN mkdir -p /opt/deploy/app
RUN mkdir -p /opt/deploy/scripts

WORKDIR /opt/deploy

RUN apk add --update curl && \
    rm -rf /var/cache/apk/*

# install requirements
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

COPY ./src/app ./app


FROM python:3.11-alpine

# make sure all messages always reach console
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/opt/deploy

RUN mkdir -p /opt/deploy/app
RUN mkdir -p /opt/deploy/scripts

WORKDIR /opt/deploy

COPY ./scripts/ ./scripts/

RUN chmod -R +x ./scripts/tests.sh
RUN chmod -R +x ./scripts/entrypoint.sh

RUN apk add --update curl && \
    rm -rf /var/cache/apk/*

COPY alembic.ini .

# install requirements
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

COPY ./src/app ./app

CMD ["scripts/entrypoint.sh"]

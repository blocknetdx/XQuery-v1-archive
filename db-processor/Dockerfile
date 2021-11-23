FROM python:3.7-alpine3.9

COPY . /app/manager
WORKDIR /app/manager

RUN apk add --no-cache build-base musl-dev gcc g++ libffi-dev openssl-dev python-dev curl krb5-dev linux-headers zeromq-dev postgresql-dev \
    && pip install cython \
    && pip install psycopg2-binary \
    && pip3 install -r /app/manager/requirements.txt \
    && apk del build-base musl-dev gcc g++ openssl-dev \
    && rm -rf /var/cache/apk/* \
    && rm -rf /usr/share/man \
    && rm -rf /tmp/*

CMD sleep 10 && python3 /app/manager/schema.py && python3 /app/manager/main.py
FROM python:3.9-buster

COPY . /app/manager
WORKDIR /app/manager

RUN apt-get update
RUN apt-get install -y build-essential musl-dev gcc g++ libffi-dev libssl-dev python3-dev curl libkrb5-dev python3-zmq libpq-dev \
    && pip install cython \
    && pip install psycopg2-binary \
    && pip3 install -r /app/manager/requirements.txt \
    && rm -rf /var/cache/apk/* \
    && rm -rf /usr/share/man \
    && rm -rf /tmp/*

#CMD sleep 20 && python3 /app/manager/index_topics.py && python3 -m scalene --profile-interval 10.0 --cli --html --outfile /app/manager/profile/$NAME.html /app/manager/main.py
CMD sleep 20 && python3 /app/manager/index_topics.py && python3 /app/manager/main.py
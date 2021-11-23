#FROM nginx:1.15-alpine
FROM openresty/openresty:alpine-fat
RUN mkdir -p /run/nginx
RUN apk add --no-cache nginx-mod-http-lua coreutils
RUN apk add python3 python3-dev py3-pip
RUN pip3 install jinja2 jinja2schema pyyaml flask
RUN apk update && apk add bash
WORKDIR /app/manager
COPY . .
CMD python3 template.py && nginx
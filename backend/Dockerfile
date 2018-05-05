FROM python:3.6-alpine

RUN apk add --update --no-cache libmemcached-dev zlib-dev cyrus-sasl-dev

RUN apk add --update --no-cache build-base make gcc musl-dev linux-headers

RUN pip install pipenv

COPY . /usr/src/app

WORKDIR /usr/src/app

RUN pipenv install --system

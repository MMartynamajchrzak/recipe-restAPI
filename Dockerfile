FROM python:3.10-alpine

# tell pyhton to run in unbuffered mode - it prints outputs directly
ENV PYTHONUNBUFFERED 1

#    copy from           copy to
COPY ./requirements.txt /requirements.txt

# user package manager (apk), add package, update registry before we add it,
# no-cache: dont store registry id on dockerflie -->
# minimize number of packages included in our docker container
RUN apk add --update --no-cache postgresql-client

# tp easily remove dependecies later
RUN apk add --update --no-cache --virtual .tmp-build-deps \
                gcc libc-dev linux-headers postgresql-dev

RUN pip install -r /requirements.txt

RUN apk del .tmp-build-deps

RUN mkdir /app

WORKDIR /app

COPY ./app /app

# create user used for running applications only --> -D
RUN adduser -D user

# switches user for this user
USER user
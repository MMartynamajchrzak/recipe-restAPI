FROM python:3.10-alpine

# tell pyhton to run in unbuffered mode - it prints outputs directly
ENV PYTHONUNBUFFERED 1

#    copy from           copy to
COPY ./requirements.txt /requirements.txt

RUN pip install -r /requirements.txt

RUN mkdir /app

WORKDIR /app

COPY ./app /app

# create user used for running applications only --> -D
RUN adduser -D user

# switches user for this user
USER user
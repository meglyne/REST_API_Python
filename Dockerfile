# pull base image
FROM python:3.8-alpine

# adding unpriviledged user and group
RUN addgroup -S messaging_api -g 433 && \
    adduser -u 431 -s /bin/sh -G messaging_api -D messaging_api

# Giving ownership of logs to messaging_api user
RUN mkdir /var/log/messaging_api
RUN chown messaging_api:messaging_api /var/log/messaging_api


#set working directory
WORKDIR /usr/src/app

# add and install requirements
COPY ./requirements.txt /usr/src/app/requirements.txt
RUN pip install -r requirements.txt

# add source code
COPY app /usr/src/app/

# set environment variables
# prevents Python from writing .pyc files to disk
ENV PYTHONDONTWRITEBYTECODE 1
# prevents Python from buffering stdout and stderr
ENV PYTHONUNBUFFERED 1

#Adding unpriviledged user
USER messaging_api

# configure Flask environment variables
ENV FLASK_APP /usr/src/app/app/messaging_api.py
ENV FLASK_ENV production

# running flask server
CMD flask run --host=0.0.0.0
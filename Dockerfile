# pull base image
FROM python:3.8-alpine

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

# configure Flask environment variables
ENV FLASK_APP /usr/src/app/app/messaging_api.py
ENV FLASK_ENV production

# running flask server
CMD flask run --host=0.0.0.0
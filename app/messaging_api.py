# app/messaging_api.py

from flask import Flask
from flask import request, make_response

from redis import Redis, RedisError

from multiprocessing import Value
from os import environ
import uuid

import redis

def create_app():
    #Creating a variable shared across Flask processes
    app = Flask(__name__)
    hostname = ""
    FLASK_ENV=environ.get('FLASK_ENV')
    if FLASK_ENV == "production":
        hostname = "redis-server"
    elif FLASK_ENV == "development":
        hostname = "localhost"
    redis_connection = Redis(host=hostname, port=6379, db=0, socket_connect_timeout=2, socket_timeout=2)

    @app.route("/", methods=['GET', 'POST'])
    def post_message():
        response = None
        if request.method == 'POST':
            if request.is_json:
                payload = request.json
                if 'message' in payload:
                    if redis_connection.ping():
                        # get a random uuid as message_id
                        new_message_id = str(uuid.uuid4())
                        try:    
                            redis_set_value(redis=redis_connection, name=new_message_id, value=payload['message'])
                        
                            response = make_response({'status': 200, 'message_id': new_message_id}, 200)
                        except RedisError:
                            response = make_response({'status': 500, 'message': 'Database error. Please try again later.'})
                    else:
                        response = make_response({'status': 500, 'message': 'Database unavailable. Please try again later.'}, 500)
                else:
                    response = make_response({'status': 400, 'message': 'Bad request - The JSON payload is missing a "message" key.'}, 400)
            else:
                response = make_response({'status': 400, 'message': 'Bad request - Your request is missing a JSON payload.'}, 400)
        elif request.method == 'GET':
            response = make_response('', 200)
        
        return response
    
    @app.route("/msg/<uuid:message_id>")
    def get_message(message_id):
        response = None
        # checking if redis is up
        if redis_connection.ping():
            try:
                message = redis_get_value(redis=redis_connection, name=str(message_id))
                #sending back message
                response = make_response({'status': 200, 'message': '{message}'.format(message=message)}, 200)
            except RedisError:
                response = make_response({'status': 400, 'message': 'Bad request - There is no message for this id'}, 400)    
        else:
            response = make_response({'status': 500, 'message': 'Database unavailable - Please try again later.'}, 500)
        return response

    return app

def redis_set_value(redis, name, value, ttl=None):
    if ttl is None or ttl > 604800:
        # set ttl by default to 7 days (=604,800 seconds)
        ttl = 604800
    success = redis.set(name=name, value=value,ex=ttl)
    if not success:
        raise RedisError

def redis_get_value(redis, name):
    value = redis.get(name=name)
    if value is None:
        raise RedisError
    else:
        # decoding bytes from redis as string
        return value.decode("utf-8")

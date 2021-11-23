# app/messaging_api.py

from flask import Flask
from flask import request, make_response

from redis import Redis, RedisError

from multiprocessing import Value
from os import environ

import redis

def create_app():
    #Creating a variable shared across Flask processes
    new_message_id = Value('i', 0)
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
                        try:
                            redis_set_value(redis=redis_connection, name=new_message_id.value, value=payload['message'])
                            with new_message_id.get_lock():
                                response = make_response({'status': 200, 'message_id': new_message_id.value}, 200)
                                new_message_id.value +=1
                        except RedisError:
                            pass
                    else:
                        response = make_response({'status': 500, 'message': 'Database unavailable. Please try again later.'}, 500)
                else:
                    response = make_response({'status': 400, 'message': 'Bad request - The JSON payload is missing a "message" key.'}, 400)
            else:
                response = make_response({'status': 400, 'message': 'Bad request - Your request is missing a JSON payload.'}, 400)
        elif request.method == 'GET':
            response = make_response('', 200)
        
        return response
    
    @app.route("/msg/<int:message_id>")
    def get_message(message_id):
        response = None
        response = make_response('', 200)
        return response

    return app

def redis_set_value(redis, name, value):
    success = redis.set(name=name, value=value)
    if not success:
        raise RedisError
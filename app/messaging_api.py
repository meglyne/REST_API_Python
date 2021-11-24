# app/messaging_api.py

from flask import Flask
from flask import request, make_response

from redis import Redis, RedisError

from os import environ, makedirs, remove
import uuid

from app.custom_logger import init_logger

def create_app():
    #Creating a variable shared across Flask processes
    app = Flask(__name__)
    redis_hostname = ""

    FLASK_ENV=environ.get('FLASK_ENV')
    if FLASK_ENV == "production":
        redis_hostname = "redis-server"
    elif FLASK_ENV == "development":
        redis_hostname = "redis-server-dev"
    elif FLASK_ENV == "debug":
        redis_hostname = "localhost"
    else:
        redis_hostname = "localhost"
    
    # setting up logger
    logger = init_logger(logname='messaging_api', env=FLASK_ENV)

    # setting up redis connection
    logger.info('Attempting connection to redis')
    redis_connection = Redis(host=redis_hostname, port=6379, db=0, socket_connect_timeout=2, socket_timeout=2)
    if redis_connection.ping():
        logger.info("Connection to redis successful at {}".format(redis_hostname))
    else:
        logger.warning("Redis server is unavailable at {}".format(redis_hostname))
    

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
                            logger.info("Successfully created a redis entry at {redis_addr} for {remote_addr} request".format(redis_addr=redis_hostname, remote_addr=request.remote_addr))
                            response = make_response({'status': 200, 'message_id': new_message_id}, 200)
                        except RedisError:
                            if redis_connection.ping():
                                logger.error("Redis server is unavailable at {redis_addr} - Dropped message from {remote_addr}".format(redis_addr=redis_hostname, remote_addr=request.remote_addr))
                                response = make_response({'status': 500, 'message': 'Database error. Please try again later.'})
                            else:
                                logger.error("Redis server encountered an error at {redis_addr} - Dropped message from {remote_addr}".format(redis_addr=redis_hostname, remote_addr=request.remote_addr))
                                response = make_response({'status': 500, 'message': 'Database error. Please try again later.'})
                    else:
                        logger.error("Redis server encountered an error at {redis_addr} - Dropped message from {remote_addr}".format(redis_addr=redis_hostname, remote_addr=request.remote_addr))
                        response = make_response({'status': 500, 'message': 'Database unavailable. Please try again later.'}, 500)
                else:
                    logger.error("Request from {remote_addr} is missing a 'message' key in the JSON payload - Dropping message".format(remote_addr=request.remote_addr))
                    response = make_response({'status': 400, 'message': 'Bad request - The JSON payload is missing a "message" key.'}, 400)
            else:
                logger.error("Request from {remote_addr} is missing a JSON payload - Dropping message".format(remote_addr=request.remote_addr))
                response = make_response({'status': 400, 'message': 'Bad request - Your request is missing a JSON payload.'}, 400)
        elif request.method == 'GET':
            response = make_response('', 200)
        
        return response
    
    @app.route("/msg/<uuid:message_id>", methods=['GET'])
    def get_message(message_id):
        response = None
        # checking if redis is up
        if redis_connection.ping():
            try:
                message = redis_get_value(redis=redis_connection, name=str(message_id))
                logger.info("Successfully found key {message_id} - Serving response 200 to {remote_addr}".format(message_id=message_id, remote_addr=request.remote_addr))
                #sending back message
                response = make_response({'status': 200, 'message': '{message}'.format(message=message)}, 200)
            except RedisError:
                logger.error("No entry for key {message_id} in redis at {redis_addr} - Serving response 400 to {remote_addr}".format(message_id=message_id, redis_addr=redis_hostname, remote_addr=request.remote_addr))
                response = make_response({'status': 400, 'message': 'Bad request - There is no message for this id'}, 400)    
        else:
            logger.error("Redis server is unavailable at {redis_addr} - Serving response 500 to {remote_addr}".format(redis_addr=redis_hostname, remote_addr=request.remote_addr))
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

# tests/test_pytest.py

from logging import log
from redis import Redis, RedisError
import requests
import json
from os import environ

from app.custom_logger import init_logger

import pytest
from requests.api import get

class TestAPIService:

    def test_service_is_available(self):
        r = requests.get('http://localhost:5000')
        assert r.status_code == 200

    def test_post_request_with_json_returns_code_200(self):
        payload = {'message': 'test'}
        r = requests.post('http://localhost:5000', json=payload)
        assert r.status_code == 200

    def test_post_request_without_json_returns_code_400(self):
        message = 'This is a test string !'
        r = requests.post('http://localhost:5000', data=message)
        assert r.status_code == 400


    def test_post_request_returns_json_response(self):
        payload = {'message':'This is another test message !'}
        r = requests.post('http://localhost:5000', json=payload)
        # testing for json formating by loading response text
        data = json.loads(r.text)
        assert data["status"] == 200

    def test_api_returns_400_if_payload_does_not_contain_message_key(self):
        payload = {'whatever': 'test'}
        r = requests.post('http://localhost:5000', json=payload)
        assert r.status_code == 400

    def test_post_request_returns_message_id(self):
        # Tests that a POST request returns a JSON response with "message_id" as one
        # of its keys
        payload = {'message':'Yet another test message !'}
        r = requests.post('http://localhost:5000', json=payload)
        data = json.loads(r.text)
        # asserting for message_id key in data
        assert "message_id" in data

    def test_message_id_is_not_an_integer(self):
        payload = {'message': 'test'}
        r = requests.post('http://localhost:5000', json=payload)
        data = json.loads(r.text)
        assert not isinstance(data['message_id'], int)

    def test_message_id_is_not_parsable_as_integer(self):
        payload = {'message': 'test'}
        r = requests.post('http://localhost:5000', json=payload)
        data = json.loads(r.text)
        message_id = data["message_id"]
        assert isinstance(message_id, str) and not message_id.isnumeric()

    def test_post_returns_different_message_id(self):
        payload1 = {'message':'test1'}
        payload2 = {'message':'test2'}
        r1 = requests.post('http://localhost:5000', json=payload1)
        r2 = requests.post('http://localhost:5000', json=payload2)
        data1 = json.loads(r1.text)
        data2 = json.loads(r2.text)
        assert data1["message_id"] != data2["message_id"]

    def test_api_returns_500_for_post_request_while_redis_unavailable(self):
        payload = {'message':'test'}
        redis_hostname = get_redis_hostname()
        try:
            redis_client = Redis(host=redis_hostname, port=6379, db=0, socket_connect_timeout=2, socket_timeout=2)
            redis_client.ping()
            r = requests.post('http://localhost:5000', json=payload)
            assert r.status_code == 200
        except RedisError:
            r = requests.post('http://localhost:5000', json=payload)
            assert r.status_code == 500

    def test_page_for_message_posted_is_accessible(self):
        payload = {'message':'test'}
        base_url = 'http://localhost:5000'
        post_r = requests.post(base_url, json=payload)
        data = json.loads(post_r.text)
        message_link = '{base_url}/msg/{message_id}'.format(base_url=base_url, message_id=data["message_id"])
        get_message_r = requests.get(message_link)
        assert get_message_r.status_code == 200

    def test_page_for_message_posted_has_payload(self):
        payload = {'message':'test'}
        base_url = 'http://localhost:5000'
        post_r = requests.post(base_url, json=payload)
        data = json.loads(post_r.text)
        message_link = '{base_url}/msg/{message_id}'.format(base_url=base_url, message_id=data["message_id"])
        get_message_r = requests.get(message_link)
        assert get_message_r.text != ''

    def test_original_message_posted_is_accessible(self):
        payload = {'message':'test'}
        base_url = 'http://localhost:5000'
        post_r = requests.post(base_url, json=payload)
        data = json.loads(post_r.text)
        message_link = '{base_url}/msg/{message_id}'.format(base_url=base_url, message_id=data["message_id"])
        get_message_r = requests.get(message_link)
        assert payload['message'] == json.loads(get_message_r.text)['message']

class TestDatabaseService:

    @pytest.fixture(scope="module")
    def redis_connection(self):
        hostname = get_redis_hostname()

        #using hostname as host to ease connection since ip might be unknown
        r = Redis(host=hostname, port=6379, db=0, socket_connect_timeout=2, socket_timeout=2)
        return r

    def test_service_is_available(self, redis_connection):
        print(redis_connection)
        assert redis_connection.ping() == True

class TestLoggerService:
    def test_logger_level_for_debug_is_debug(self):
        logger = init_logger(logpath='.', logname='test', env='development')
        assert logger.level == 10

    def test_logger_level_for_prod_is_info(self):
        logger = init_logger(logpath='.', logname='test', env='production')
        assert logger.level == 20
    
    def test_logger_with_no_filename_inits(self):
        logger = init_logger(logpath='.', env='development')
        assert logger.handlers[-1].baseFilename != ''

def get_redis_hostname():
    redis_hostname = None
    FLASK_ENV=environ.get('FLASK_ENV')
    if FLASK_ENV == "production":
        redis_hostname = "redis-server"
    elif FLASK_ENV == "development":
        redis_hostname = "redis-server-dev"
    elif FLASK_ENV == "debug":
        redis_hostname = "localhost"
    else:
        redis_hostname = "localhost"
    return redis_hostname

        
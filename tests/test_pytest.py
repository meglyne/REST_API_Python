# tests/test_pytest.py

from redis import Redis
import requests
import json
from os import environ

import pytest

class TestAPIService:

    def test_service_is_available(self):
        r = requests.get('http://localhost:5000')
        assert r.status_code == 200

    def test_post_request_returns_code_200(self):
        message = 'This is a test message !'
        r = requests.post('http://localhost:5000', data=message)
        assert r.status_code == 200

    def test_post_request_returns_json_response(self):
        message = 'This is another test message !'
        r = requests.post('http://localhost:5000', data=message)
        # testing for json formating by loading response text
        data = json.loads(r.text)
        assert data["status"] == 200

    def test_post_request_returns_message_id(self):
        message = 'Yet another test message !'
        r = requests.post('http://localhost:5000', data=message)
        data = json.loads(r.text)
        # asserting for message_id key in data
        assert "message_id" in data

    def test_post_returns_different_message_id(self):
        message1 = 'test1'
        message2 = 'test2'
        r1 = requests.post('http://localhost:5000', data=message1)
        r2 = requests.post('http://localhost:5000', data=message2)
        data1 = json.loads(r1.text)
        data2 = json.loads(r2.text)
        assert data1["message_id"] != data2["message_id"]
    
    def test_message_posted_is_accessible(self):
        message = 'test'
        base_url = 'http://localhost:5000'
        post_r = requests.post(base_url, data=message)
        data = json.loads(post_r.text)
        message_link = '{base_url}/msg/{message_id}'.format(base_url=base_url, message_id=data["message_id"])
        get_message_r = requests.get(message_link)
        assert get_message_r.status_code == 200

class TestDatabaseService:

    @pytest.fixture(scope="module")
    def redis_connection(self):
        r = None
        FLASK_ENV=environ.get('FLASK_ENV')
        if FLASK_ENV == "production":
            #using hostname as host to ease connection since ip might be unknown
            r = Redis(host="redis-server", port=6379, db=0, socket_connect_timeout=2, socket_timeout=2)
        else:
            r = Redis(host="redis-server-dev", port=6379, db=0, socket_connect_timeout=2, socket_timeout=2)
        return r

    def test_service_is_available(self, redis_connection):
        print(redis_connection)
        assert redis_connection.ping() == True

        
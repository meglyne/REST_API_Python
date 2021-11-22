import requests
import json

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
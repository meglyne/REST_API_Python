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
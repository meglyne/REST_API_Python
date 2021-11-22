import requests

class TestAPIService:

    def test_service_is_available(self):
        r = requests.get('http://localhost:5000')
        assert r.status_code == 200

    def test_post_request_code_200(self):
        message = 'This is a test message !'
        r = requests.post('http://localhost:5000', data=message)
        assert r.status_code == 200

class TestIncDec:
    def test_increments(self):
        assert inc_dec.increment(3) == 4

    def test_decrement(self):
        assert inc_dec.decrement(3) == 2
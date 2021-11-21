from inc_dec import inc_dec
from app import messaging_api
import requests
import pytest

class TestAPIService:
    @pytest.fixture
    def start_service(self):
        app = messaging_api.create_app()
        with app.test_client() as client:
            yield client

    def test_service_is_available(self, start_service):
        r = requests.get('http://localhost:5000')
        assert r.status_code == 200

class TestIncDec:
    def test_increments(self):
        assert inc_dec.increment(3) == 4

    def test_decrement(self):
        assert inc_dec.decrement(3) == 2
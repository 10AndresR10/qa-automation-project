import requests
import pytest
BASE_URL = "https://restful-booker.herokuapp.com"


@pytest.fixture
def base_url():
    return BASE_URL

@pytest.fixture
def token(base_url):
    auth_response = requests.post(f"{base_url}/auth", json={"username": "admin", "password": "password123"})
    assert auth_response.status_code == 200
    assert "token" in auth_response.json(), auth_response.text
    token = auth_response.json()["token"]
    return token
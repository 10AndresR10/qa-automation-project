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

@pytest.fixture
def existing_booking_id(base_url):
    payload = {
        "firstname": "John",
        "lastname": "Smith",
        "totalprice": 150,
        "depositpaid": True,
        "bookingdates": {
            "checkin": "2026-01-01",
            "checkout": "2026-01-05"
        },
        "additionalneeds": "Breakfast"
    }

    response = requests.post(f"{base_url}/booking", json=payload)
    assert response.status_code == 200
    body = response.json()
    return {"id": body["bookingid"], "payload": payload, "body": body}

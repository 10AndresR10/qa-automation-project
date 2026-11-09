import requests
import pytest
from helpers import delete_booking
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
    print(token)
    return token

@pytest.fixture
def existing_booking_id(base_url, token):
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
    id_body = body["bookingid"]
    yield {"id": id_body, "payload": payload, "body": body}
    delete_booking(base_url, token, id_body)

@pytest.fixture
def non_existent_booking_id(base_url):
    response = requests.get(f"{base_url}/booking")
    assert response.status_code == 200
    highest_id = max(booking["bookingid"] for booking in response.json())
    return highest_id + 1000

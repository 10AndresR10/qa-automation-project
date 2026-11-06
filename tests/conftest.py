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
    yield {"id": body["bookingid"], "payload": payload, "body": body}
    delete_request = requests.delete(f"{base_url}/booking/{body['bookingid']}", headers={"Cookie": f"token={token}"})
    assert delete_request.status_code in [201, 405], f"Cleanup of booking {body['bookingid']}: expected 201 or 405, but got {delete_request.status_code}, {delete_request.text} with these headers {delete_request.headers}"

@pytest.fixture
def non_existent_booking_id(base_url):
    response = requests.get(f"{base_url}/booking")
    assert response.status_code == 200
    highest_id = max(booking["bookingid"] for booking in response.json())
    return highest_id + 1000

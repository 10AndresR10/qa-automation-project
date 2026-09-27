import copy

import pytest
import requests


BASE_URL = "https://restful-booker.herokuapp.com"

DEFAULT_BOOKING = {
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


@pytest.fixture(scope="session")
def base_url():
    return BASE_URL


@pytest.fixture(scope="session")
def auth_token(base_url):
    # One token for the whole test run instead of one per test.
    response = requests.post(f"{base_url}/auth", json={"username": "admin", "password": "password123"})
    assert response.status_code == 200
    return response.json()["token"]


@pytest.fixture(scope="session")
def auth_headers(auth_token):
    return {"Cookie": f"token={auth_token}"}


@pytest.fixture
def booking_payload():
    # Deep copy so a test can change nested fields (bookingdates) without
    # affecting other tests.
    return copy.deepcopy(DEFAULT_BOOKING)


@pytest.fixture
def created_booking(base_url, auth_headers, booking_payload):
    # Creates a booking before the test and deletes it afterwards.
    response = requests.post(f"{base_url}/booking", json=booking_payload)
    assert response.status_code == 200
    booking_id = response.json()["bookingid"]

    yield booking_id

    # Teardown: if the test already deleted the booking, this returns 405,
    # which is fine to ignore.
    requests.delete(f"{base_url}/booking/{booking_id}", headers=auth_headers)

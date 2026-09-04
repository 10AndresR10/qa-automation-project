import pytest
import requests

class TestBookingDelete:

    base_url = "https://restful-booker.herokuapp.com"

    def test_delete_method(self):

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
        
        response = requests.post(f"{self.base_url}/booking", json=payload)

        id = response.json()["bookingid"]

        auth_response = requests.post(f"{self.base_url}/auth", json={"username": "admin", "password": "password123"})
        token = auth_response.json()["token"]

        new_response = requests.delete(f"{self.base_url}/booking/{id}", headers={"Cookie": f"token={token}"})

        assert new_response.status_code == 201
        assert new_response.text == "Created"

        new_get = requests.get(f"{self.base_url}/booking/{id}")
        
        assert new_get.status_code == 404
        assert new_get.text == "Not Found"
        

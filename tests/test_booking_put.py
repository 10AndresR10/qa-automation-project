import requests
import pytest


class TestBookingPut:

    base_url = "https://restful-booker.herokuapp.com"

    def test_put_method(self):

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

        auth_response = requests.post(f"{self.base_url}/auth",json={"username": "admin", "password": "password123"})
        token = auth_response.json()["token"]

        payload = {
            "firstname": "Andres",
            "lastname": "Reyes",
            "totalprice": 100,
            "depositpaid": True,
            "bookingdates": {
                "checkin": "2026-01-01",
                "checkout": "2026-01-05"
            },
            "additionalneeds": "Breakfast"
            }

        update_response = requests.put(f"{self.base_url}/booking/{id}", json=payload, headers={"Cookie": f"token={token}"})

        body = update_response.json()
            
        assert update_response.status_code == 200
        assert body ["firstname"] == "Andres"
        assert body ["lastname"] == "Reyes"
        assert body ["totalprice"] == 100
        assert body ["depositpaid"] == True
        assert body ["bookingdates"]["checkin"] == "2026-01-01"
        assert body ["bookingdates"]["checkout"] == "2026-01-05"
        assert body ["additionalneeds"] == "Breakfast"
            
            
    def test_put_wrong_data(self):

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

        auth_response = requests.post(f"{self.base_url}/auth",json={"username": "admin", "password": "password123"})
        token = auth_response.json()["token"]
        payload = {
            "firstname": 0000,
            "lastname": True,
            "totalprice": "One",
            "depositpaid": 0,
            "bookingdates": {
                "checkin": 0,
                "checkout": " "
            },
            "additionalneeds": False
            }

        new_response = requests.put(f"{self.base_url}/booking/{id}", json= payload, headers={"Cookie": f"token={token}"})
        assert new_response.status_code == 500
        assert new_response.text == "Internal Server Error"

    def test_non_existent_booking_ID(self):

        none_id = 99999999999

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

        auth_response = requests.post(f"{self.base_url}/auth",json={"username": "admin", "password": "password123"})
        token = auth_response.json()["token"]
        response = requests.put(f"{self.base_url}/booking/{none_id}", json= payload, headers= {"Cookie": f"token={token}"})
        
        assert response.status_code in [405, 403]
        assert response.text == "Method Not Allowed"

    def test_missing_required_field(self):

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

        response = requests.post(f"{self.base_url}/booking", json= payload)

        id = response.json()["bookingid"]

        auth_response = requests.post(f"{self.base_url}/auth", json={"username": "admin", "password": "password123"})
        token = auth_response.json()["token"]

        wrong_payload = payload.copy()

        del wrong_payload["firstname"]

        new_response = requests.put(f"{self.base_url}/booking/{id}", json= wrong_payload, headers={"Cookie":f"token={token}"})

        assert new_response.status_code == 400 
        assert new_response.text == "Bad Request"
        


        
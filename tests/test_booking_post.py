import requests
import pytest

class TestBookingPost:

    base_url = "https://restful-booker.herokuapp.com"

    def test_post_method(self):
        payload = {
            "firstname": "Andres",
            "lastname": "Reyes",
            "totalprice": 10,
            "depositpaid": True,
            "bookingdates": {
                "checkin": "2026-01-01",
                "checkout": "2027-01-01"
            },
            "additionalneeds": "Breakfast"
        }
        response = requests.post(f"{self.base_url}/booking", json=payload)

        body = response.json()

        assert response.status_code == 200
        assert body ["booking"]["firstname"] == "Andres"
        assert body ["booking"]["lastname"] == "Reyes"
        assert body ["booking"]["totalprice"] == 10
        assert body ["booking"]["depositpaid"] == True
        assert body ["booking"]["bookingdates"]["checkin"] == "2026-01-01"
        assert body ["booking"]["bookingdates"]["checkout"] == "2027-01-01"
        assert body ["booking"]["additionalneeds"] == "Breakfast"
        assert "bookingid" in body


    def test_wrong_data_type(self):

        payload = {
            "firstname": 4783274,
            "lastname": 273482,
            "totalprice": "10",
            "depositpaid": "True",
            "bookingdates": {
                "checkin": 2026,
                "checkout": 2025
            },
            "additionalneeds": 0
        }

        response = requests.post(f"{self.base_url}/booking", json=payload)

        print(response.status_code)
        print(response.text)
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

    def assert_bad_request_returns_500(self, payload):
        response = requests.post(f"{self.base_url}/booking", json=payload)
        assert response.status_code == 500
        assert response.text == "Internal Server Error"

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

        for key, value in payload.items():
            if key == "firstname" or key == "lastname" or key == "additionalneeds":
                if type(value) != str:
                    self.assert_bad_request_returns_500(payload)

            elif key == "totalprice":
                if type(value)!= int:
                    self.assert_bad_request_returns_500(payload)
            
            elif key == "depositpaid":
                if type(value) != bool:
                    self.assert_bad_request_returns_500(payload)

            elif key == "bookingdates":
                if type(value["checkin"]) != str:
                    self.assert_bad_request_returns_500(payload)
                
                if type(value["checkout"]) != str:
                    self.assert_bad_request_returns_500(payload)


    def test_missing_required_field(self):

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

        for key in list(payload.keys()):
            if key == "firstname":
                modified_payload = payload.copy()
                del modified_payload[key]
                response = requests.post(f"{self.base_url}/booking", json=modified_payload)
                assert response.status_code == 500
                assert response.text == "Internal Server Error"
            
            elif key == "lastname":
                modified_payload = payload.copy()
                del modified_payload[key]
                response = requests.post(f"{self.base_url}/booking", json=modified_payload)
                assert response.status_code == 500
                assert response.text == "Internal Server Error"
            
            elif key == "totalprice":
                modified_payload = payload.copy()
                del modified_payload[key]
                response = requests.post(f"{self.base_url}/booking", json=modified_payload)
                assert response.status_code == 500
                assert response.text == "Internal Server Error"

            elif key == "depositpaid":
                modified_payload = payload.copy()
                del modified_payload[key]
                response = requests.post(f"{self.base_url}/booking", json=modified_payload)
                assert response.status_code == 500
                assert response.text == "Internal Server Error"
            
            elif key == "bookingdates":
                modified_payload = payload.copy()
                del modified_payload[key]
                response = requests.post(f"{self.base_url}/booking", json=modified_payload)
                assert response.status_code == 500
                assert response.text == "Internal Server Error"
            
            elif key == "additionalneeds":
                modified_payload = payload.copy()
                del modified_payload[key]
                response = requests.post(f"{self.base_url}/booking", json=modified_payload)
                assert response.status_code == 200
            
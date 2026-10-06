import requests
import pytest

class TestBookingGet:
    def test_get_method(self, base_url, existing_booking_id):
        response = requests.get(f"{base_url}/booking/{existing_booking_id}")

        assert response.status_code == 200

        body = response.json()
        assert "firstname" in body
        assert "lastname" in body
        assert "totalprice" in body
        assert isinstance(body["totalprice"], (int, float))
        assert "depositpaid" in body
        assert "bookingdates" in body
        assert "checkin" in body["bookingdates"]
        assert "checkout" in body["bookingdates"]

    def test_get_malformed_id(self, base_url):
        response = requests.get(f"{base_url}/booking/abc")
        assert response.status_code == 404
        assert "Not Found" in response.text

    def test_get_non_existent_id(self, base_url):
        response = requests.get(f"{base_url}/booking/9999")
        assert response.status_code == 404
        assert "Not Found" in response.text

    def test_an_id_of_whitespace(self, base_url):
        response = requests.get(f"{base_url}/booking/    ")
        assert response.status_code == 404
        assert "Not Found" in response.text

    def test_an_extremely_large_id(self, base_url):
        response = requests.get(f"{base_url}/booking/99999909029349309423049230940249032492304")
        assert response.status_code == 404
        assert "Not Found" in response.text


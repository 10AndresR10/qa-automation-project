import requests
import pytest


class TestBookingPost:

    def test_post_method(self, existing_booking_id):

        payload = existing_booking_id["payload"]
        body = existing_booking_id["body"]
        assert body["booking"]["firstname"] == payload["firstname"]
        assert body["booking"]["lastname"] == payload["lastname"]
        assert body["booking"]["totalprice"] == payload["totalprice"]
        assert body["booking"]["depositpaid"] is True
        assert body["booking"]["bookingdates"]["checkin"] == payload["bookingdates"]["checkin"]
        assert body["booking"]["bookingdates"]["checkout"] == payload["bookingdates"]["checkout"]
        assert body["booking"]["additionalneeds"] == payload["additionalneeds"]
        assert "bookingid" in body

    @pytest.mark.parametrize("key, expected_status_code, wrong_value, expected_value",[
        # expected_value is not checked for 500 responses
        # Known API bug: a wrong data type should be rejected with 400, but the number crashes the server
        ("firstname", 500, 12345, None),
        # Known API bug: a wrong data type should be rejected with 400, but True crashes the server
        ("firstname", 500, True, None),
        # Known API bug: a wrong data type should be rejected, but firstname stores the boolean as sent
        ("firstname", 200, False, False),
        # Known API bug: a wrong data type should be rejected with 400, but the float crashes the server
        ("firstname", 500, 3.14, None),
        # Known API bug: a wrong data type should be rejected with 400, but the number crashes the server
        ("lastname", 500, 12345, None),
        # Known API bug: a wrong data type should be rejected with 400, but True crashes the server
        ("lastname", 500, True, None),
        # Known API bug: a wrong data type should be rejected, but lastname stores the boolean as sent
        ("lastname", 200, False, False),
        # Known API bug: a wrong data type should be rejected with 400, but the float crashes the server
        ("lastname", 500, 3.14, None),
        # Known API bug: a wrong data type should be rejected, but totalprice is corrupted to null
        ("totalprice", 200, "One", None),
        # A numeric string is coerced to a number (Number("12345")), not a bug
        ("totalprice", 200, "12345", 12345),
        # Known API bug: a wrong data type should be rejected, but True corrupts totalprice to null
        ("totalprice", 200, True, None),
        # Known API bug: a wrong data type should be rejected, but False corrupts totalprice to null
        ("totalprice", 200, False, None),
        # Known API bug: a negative price should be rejected, but totalprice stores it as sent
        ("totalprice", 200, -1000, -1000),
        # A non-empty string is coerced to true (bool("True")), not a bug
        ("depositpaid", 200, "True", True),
        # Known API bug: a wrong data type should be rejected, but "False" is coerced to true and inverts the meaning
        ("depositpaid", 200, "False", True),
        # A non-empty string is coerced to true (bool("Andres")), not a bug
        ("depositpaid", 200, "Andres", True),
        # A non-zero number is coerced to true (bool(123456)), not a bug
        ("depositpaid", 200, 123456, True),
        # A non-zero number is coerced to true (bool(3.1233)), not a bug
        ("depositpaid", 200, 3.1233, True),
        # 0 is coerced to false (bool(0)), not a bug
        ("depositpaid", 200, 0, False),
        # A non-zero number is coerced to true (bool(-99)), not a bug
        ("depositpaid", 200, -99, True),
        # Known API bug: a wrong data type should be rejected with 400, but True crashes the server
        ("bookingdates", 500, True, None),
        # Known API bug: a wrong data type should be rejected with 400, but False crashes the server
        ("bookingdates", 500, False, None),
        # Known API bug: a wrong data type should be rejected with 400, but the number crashes the server
        ("bookingdates", 500, 0, None),
        # Known API bug: a wrong data type should be rejected with 400, but the number crashes the server
        ("bookingdates", 500, 12345, None),
        # Known API bug: a wrong data type should be rejected with 400, but the negative number crashes the server
        ("bookingdates", 500, -12345, None),
        # Known API bug: a wrong data type should be rejected with 400, but the string crashes the server
        ("bookingdates", 500, "Andres", None),
        # Known API bug: a wrong data type should be rejected with 400, but the float crashes the server
        ("bookingdates", 500, 3.14, None),
        # Known API bug: a wrong data type should be rejected, but additionalneeds stores the number as sent
        ("additionalneeds", 200, 0, 0),
        # Known API bug: a wrong data type should be rejected, but additionalneeds stores the number as sent
        ("additionalneeds", 200, 12345, 12345),
        # Known API bug: a wrong data type should be rejected, but additionalneeds stores the negative number as sent
        ("additionalneeds", 200, -12345, -12345),
        # Known API bug: a wrong data type should be rejected, but additionalneeds stores the boolean as sent
        ("additionalneeds", 200, True, True),
        # Known API bug: a wrong data type should be rejected, but additionalneeds stores the boolean as sent
        ("additionalneeds", 200, False, False),
        # Known API bug: a wrong data type should be rejected, but additionalneeds stores the float as sent
        ("additionalneeds", 200, 3.14, 3.14),
    ])
    def test_wrong_data_type(self, base_url, key, expected_status_code, wrong_value, expected_value):

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

        new_payload = payload.copy()
        new_payload[key] = wrong_value
        response = requests.post(f"{base_url}/booking", json=new_payload)
        assert response.status_code == expected_status_code, f"Expected {expected_status_code} with {key}, but got {response.status_code}"
        if expected_status_code == 500:
            assert response.text == "Internal Server Error"
        else:
            body = response.json()
            assert body["booking"][key] == expected_value, f"{key}: expected {expected_value!r}, got {body['booking'][key]!r}"
               
    @pytest.mark.parametrize("key, expected_status_code", [
        ("firstname", 500),
        ("lastname", 500),
        ("totalprice", 500),
        ("depositpaid", 500),
        ("bookingdates", 500),
        ("additionalneeds", 200),
    ])
    def test_missing_required_field(self, base_url, key, expected_status_code):

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

        del payload[key]
        response = requests.post(f"{base_url}/booking", json=payload)
        assert response.status_code == expected_status_code, f"Expected {expected_status_code} with {key} missing, but got {response.status_code}"

        if expected_status_code == 500:
            assert response.text == "Internal Server Error"

            
    def test_empty_string_field(self, base_url):

        payload = {
            "firstname": "",
            "lastname": "",
            "totalprice": "",
            "depositpaid": "",
            "bookingdates": {
                "checkin": "",
                "checkout": ""
            },
            "additionalneeds": ""
        }

        response = requests.post(f"{base_url}/booking", json=payload)
        assert response.status_code == 200
        body = response.json()

        assert body["booking"]["firstname"] == ""
        assert body["booking"]["lastname"] == ""
        assert body["booking"]["totalprice"] is None
        assert body["booking"]["depositpaid"] is False
        assert body["booking"]["bookingdates"]["checkin"] == "0NaN-aN-aN"
        assert body["booking"]["bookingdates"]["checkout"] == "0NaN-aN-aN"
        assert body["booking"]["additionalneeds"] == ""

    def test_extremely_long_string(self, base_url):

        payload = {
            "firstname": "Andres Andres Andres Andres Andres Andres Andres Andres Andres Andres Andres AndresAndres Andres Andres Andres Andres AndresAndres Andres Andres Andres Andres AndresAndres Andres Andres Andres Andres AndresAndres Andres Andres Andres Andres AndresAndres Andres Andres Andres Andres Andres",
            "lastname": "Reyes Reyes Reyes Reyes Reyes Reyes Reyes Reyes Reyes Reyes Reyes Reyes Reyes Reyes Reyes Reyes Reyes Reyes Reyes Reyes Reyes Reyes Reyes Reyes Reyes Reyes Reyes Reyes Reyes Reyes Reyes Reyes Reyes Reyes Reyes Reyes Reyes Reyes Reyes Reyes Reyes Reyes Reyes Reyes Reyes Reyes Reyes Reyes Reyes Reyes",
            "totalprice": 10,
            "depositpaid": False,
            "bookingdates": {
                "checkin": "2026-01-01",
                "checkout": "2026-01-01"
            },
            "additionalneeds": "Breakfast Breakfast Breakfast Breakfast Breakfast Breakfast Breakfast Breakfast Breakfast Breakfast Breakfast Breakfast Breakfast Breakfast Breakfast Breakfast Breakfast Breakfast Breakfast Breakfast Breakfast Breakfast Breakfast Breakfast Breakfast Breakfast Breakfast Breakfast Breakfast Breakfast Breakfast Breakfast Breakfast Breakfast Breakfast Breakfast "
        }

        response = requests.post(f"{base_url}/booking", json= payload)
        assert response.status_code == 200
        body = response.json()

        assert body["booking"]["firstname"] == payload["firstname"]
        assert body["booking"]["lastname"] == payload["lastname"]
        assert body["booking"]["additionalneeds"] == payload["additionalneeds"]

    def test_equivalence_partitioning_checkvariables(self, base_url):
        
        payload = {
            "firstname": "Andres",
            "lastname": "Reyes",
            "totalprice": 10,
            "depositpaid": True,
            "bookingdates": {
                "checkin": "2099-13-01",
                "checkout": "1999-01-32"
            },
            "additionalneeds": "Breakfast"
        }

        response = requests.post(f"{base_url}/booking", json= payload)
        assert response.status_code == 200
        body = response.json()

        assert body["booking"]["bookingdates"]["checkin"] == "0NaN-aN-aN"
        assert body["booking"]["bookingdates"]["checkout"] == "0NaN-aN-aN"

    def test_equivalence_partitioning_valid_dates(self, base_url):

        payload = {
            "firstname": "Andres",
            "lastname": "Reyes",
            "totalprice": 10,
            "depositpaid": True,
            "bookingdates": {
                "checkin": "2026-12-01",
                "checkout": "2026-12-10"
            },
            "additionalneeds": "Breakfast"
        }

        response = requests.post(f"{base_url}/booking", json=payload)
        assert response.status_code == 200
        body = response.json()

        assert body["booking"]["bookingdates"]["checkin"] == "2026-12-01"
        assert body["booking"]["bookingdates"]["checkout"] == "2026-12-10"

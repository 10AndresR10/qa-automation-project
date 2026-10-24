import requests
import pytest

LONG_STRING = "Andres12324" * 50

class TestBookingPut:

    def test_put_method(self, base_url, token, existing_booking_id):

        payload = {
            "firstname": "Andres",
            "lastname": "Reyes",
            "totalprice": 100,
            "depositpaid": False,
            "bookingdates": {
                "checkin": "2026-02-01",
                "checkout": "2026-02-05"
            },
            "additionalneeds": "Soccer"
            }

        update_response = requests.put(f"{base_url}/booking/{existing_booking_id['id']}", json=payload, headers={"Cookie": f"token={token}"})
        assert update_response.status_code == 200, update_response.text
        body = update_response.json()

        assert body["firstname"] == "Andres"
        assert body["lastname"] == "Reyes"
        assert body["totalprice"] == 100
        assert body["depositpaid"] is False
        assert body["bookingdates"]["checkin"] == "2026-02-01"
        assert body["bookingdates"]["checkout"] == "2026-02-05"
        assert body["additionalneeds"] == "Soccer"
    
    @pytest.mark.parametrize("key, expected_status_code, wrong_value, expected_value", [
        ("firstname", 200, 0, 0),
        ("lastname", 200, 0, 0),
        ("totalprice", 200, "One", None),
        ("depositpaid", 200, 0, False),        
    ])
    def test_put_wrong_data(self, base_url, token, existing_booking_id, key, expected_status_code, wrong_value, expected_value):

        put_payload = existing_booking_id["payload"].copy()
        put_payload[key] = wrong_value
        new_response = requests.put(f"{base_url}/booking/{existing_booking_id['id']}", json=put_payload, headers={"Cookie": f"token={token}"})
        assert new_response.status_code == expected_status_code, f"Expected {expected_status_code} with {key}, but got {new_response.status_code}"
        body = new_response.json()
        assert body[key] == expected_value           
   
    def test_non_existent_booking_ID(self, base_url, token, existing_booking_id):

        booking_id = existing_booking_id["id"]
        new_response = requests.delete(f"{base_url}/booking/{booking_id}", headers={"Cookie": f"token={token}"})
        assert new_response.status_code == 201
        response = requests.put(f"{base_url}/booking/{booking_id}", json= existing_booking_id["payload"], headers= {"Cookie": f"token={token}"})
        # Known API bug: a missing booking should return 404 Not Found, but the API returns 405
        assert response.status_code == 405
        assert response.text == "Method Not Allowed"

    @pytest.mark.parametrize("key, expected_status_code", [
        ("firstname", 400),
        ("lastname", 400),
        ("totalprice", 400),
        ("depositpaid", 400),
        ("bookingdates", 400),
        ("additionalneeds", 200),
    ])
    def test_missing_required_field(self, base_url, token, existing_booking_id, key, expected_status_code):

        wrong_payload = existing_booking_id["payload"].copy()

        del wrong_payload[key]
        response = requests.put(f"{base_url}/booking/{existing_booking_id['id']}", json=wrong_payload, headers= {"Cookie": f"token={token}"})
        assert response.status_code == expected_status_code, f"Expected {expected_status_code} with {key} missing, but got {response.status_code}"

        if expected_status_code == 400:
            assert response.text == "Bad Request"

    @pytest.mark.parametrize("key, expected_status_code, expected_value", [
        ("firstname", 200, LONG_STRING),
        ("lastname", 200, LONG_STRING),
        # Known API bug: an extremely long string should be rejected or stored as sent, but totalprice is corrupted to null
        ("totalprice", 200, None),
        # Known API bug: an extremely long string should be rejected or stored as sent, but depositpaid is corrupted to true
        ("depositpaid", 200, True),
        # Known API bug: an extremely long string should be rejected or stored as sent, but checkin and checkout are corrupted to 0NaN-aN-aN
        ("bookingdates", 200, "0NaN-aN-aN"),
        ("additionalneeds", 200, LONG_STRING)
    ])
    def test_extremely_long_string_field(self, base_url, token, existing_booking_id, key, expected_status_code, expected_value):

        long_string_payload = existing_booking_id["payload"].copy()
        if key == "bookingdates":
            long_string_payload["bookingdates"] = {
                "checkin": LONG_STRING,
                "checkout": LONG_STRING,
            }
        else:
            long_string_payload[key] = LONG_STRING

        new_response = requests.put(f"{base_url}/booking/{existing_booking_id['id']}", json=long_string_payload, headers={"Cookie": f"token={token}"})
        assert new_response.status_code == expected_status_code
        actual = new_response.json()[key]

        if key == "bookingdates":
            assert actual["checkin"] == expected_value, f"checkin: expected {expected_value!r}, got {actual['checkin']!r}"
            assert actual["checkout"] == expected_value, f"checkout: expected {expected_value!r}, got {actual['checkout']!r}"
        else:
            assert actual == expected_value, f"{key}: expected {expected_value!r}, got {actual!r}"

    @pytest.mark.parametrize("key, expected_status_code, expected_value", [
        ("firstname", 200, ""),
        ("lastname", 200, ""),
        # Known API bug: an empty string should be rejected or stored as sent, but totalprice is corrupted to null
        ("totalprice", 200, None),
        # Known API bug: an empty string should be rejected or stored as sent, but depositpaid is corrupted to false
        ("depositpaid", 200, False),
        # expected_value is not checked for 400 responses
        ("bookingdates", 400, None),
        ("additionalneeds", 200, "")
    ])
    def test_empty_string_field(self, base_url, token, existing_booking_id, key, expected_status_code, expected_value):

        empty_request = existing_booking_id["payload"].copy()
        empty_request[key] = ""
        new_response = requests.put(f"{base_url}/booking/{existing_booking_id['id']}", json=empty_request, headers={"Cookie": f"token={token}"})
        assert new_response.status_code == expected_status_code

        if expected_status_code == 400:
            assert new_response.text == "Bad Request"
        else:
            actual = new_response.json()[key]
            assert actual == expected_value, f"{key}: expected {expected_value!r}, got {actual!r}"


    def test_empty_string_nested_bookingdates_field(self, base_url, token, existing_booking_id):

        for date_key in ["checkin", "checkout"]:

            update_payload = existing_booking_id["payload"].copy()
            update_payload["bookingdates"] = existing_booking_id["payload"]["bookingdates"].copy()
            update_payload["bookingdates"][date_key] = ""

            new_response = requests.put(f"{base_url}/booking/{existing_booking_id['id']}", json=update_payload, headers={"Cookie": f"token={token}"})

            assert new_response.status_code == 200
            assert new_response.json()["bookingdates"][date_key] == "0NaN-aN-aN"


    def test_no_cookie_auth(self, base_url, existing_booking_id):

        update_payload = existing_booking_id["payload"].copy()
        update_payload["firstname"] = "Andres"

        put_response = requests.put(f"{base_url}/booking/{existing_booking_id['id']}", json=update_payload)
        assert put_response.status_code == 403
        assert put_response.text == "Forbidden"

    def test_an_invalid_expired_token(self, base_url, existing_booking_id):

        update_payload = existing_booking_id["payload"].copy()

        update_payload["firstname"] = "Andres"

        new_response = requests.put(f"{base_url}/booking/{existing_booking_id['id']}", json=update_payload, headers={"Cookie": "token=invalidtoken123"})

        assert new_response.status_code == 403
        assert new_response.text == "Forbidden"

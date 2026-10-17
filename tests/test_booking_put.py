import requests
import pytest

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
            
            
    def test_put_wrong_data(self, base_url, token, existing_booking_id):

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

        new_response = requests.put(f"{base_url}/booking/{existing_booking_id['id']}", json= payload, headers={"Cookie": f"token={token}"})
        assert new_response.status_code == 500
        assert new_response.text == "Internal Server Error"

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

    def test_extremely_long_string_field(self, base_url, token, existing_booking_id):

        long_string_payload = existing_booking_id["payload"].copy()
        long_string = "Andres Andres Andres Andres Andres Andres Andres Andres Andres Andres Andres Andres Andres "

        for key in list(long_string_payload):

            long_string_payload = existing_booking_id["payload"].copy()
            if key == "bookingdates":
                long_string_payload["bookingdates"] = {
                    "checkin": long_string,
                    "checkout": long_string,
                }

            else:
                long_string_payload[key] = long_string

            new_response = requests.put(f"{base_url}/booking/{existing_booking_id['id']}", json= long_string_payload, headers={"Cookie": f"token={token}"})

            assert new_response.status_code == 200

            if key == "bookingdates":
                body = new_response.json()
                assert body["bookingdates"]["checkin"] == "0NaN-aN-aN"
                assert body["bookingdates"]["checkout"] == "0NaN-aN-aN"


    def test_empty_string_field(self, base_url, token, existing_booking_id):
        empty_response= existing_booking_id["payload"].copy()

        for key in empty_response:
            empty_response = existing_booking_id["payload"].copy()
            empty_response[key] = ""
            new_response = requests.put(f"{base_url}/booking/{existing_booking_id['id']}", json=empty_response, headers={"Cookie": f"token={token}"})

            if key == "bookingdates":
                assert new_response.status_code == 400
                assert new_response.text == "Bad Request"
                
            else:
                known_bugs = {
                "totalprice": None,
                "depositpaid": False,
                }
                assert new_response.status_code == 200
                actual = new_response.json()[key]

                if key in known_bugs:
                    assert actual == known_bugs[key], f"{key}: expected known bug value {known_bugs[key]!r}, got {actual!r}"

                else:
                    assert actual == ""


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

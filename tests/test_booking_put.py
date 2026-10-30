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
        # Known API bug: a wrong data type should be rejected, but firstname stores the number as sent
        ("firstname", 200, 0, 0),
        # Known API bug: a wrong data type should be rejected with 400, but True crashes the server
        ("firstname", 500, True, None),
        # Known API bug: a wrong data type should be rejected, but firstname stores the boolean as sent
        ("firstname", 200, False, False),
        # Known API bug: a wrong data type should be rejected, but lastname stores the number as sent
        ("lastname", 200, 0, 0),
        # Known API bug: a wrong data type should be rejected with 400, but True crashes the server
        ("lastname", 500, True, None),
        # Known API bug: a wrong data type should be rejected, but lastname stores the boolean as sent
        ("lastname", 200, False, False),
        # Known API bug: a wrong data type should be rejected, but totalprice is corrupted to null
        ("totalprice", 200, "One", None),
        # Known API bug: a wrong data type should be rejected, but True corrupts totalprice to null
        ("totalprice", 200, True, None),
        # Known API bug: a wrong data type should be rejected, but False corrupts totalprice to null
        ("totalprice", 200, False, None),
        # 0 is coerced to false (bool(0)), not a bug
        ("depositpaid", 200, 0, False),
        # A non-empty string is coerced to true (bool("True")), not a bug
        ("depositpaid", 200, "True", True),
        # Known API bug: a wrong data type should be rejected, but "False" is coerced to true and inverts the meaning
        ("depositpaid", 200, "False", True),
        # A non-zero number is coerced to true (bool(888.0)), not a bug
        ("depositpaid", 200, 888.000, True),
        # expected_value is not checked for 400 or 500 responses
        # A number is correctly rejected for bookingdates
        ("bookingdates", 400, 0, None),
        # A boolean is correctly rejected for bookingdates
        ("bookingdates", 400, False, None),
        # A string is correctly rejected for bookingdates
        ("bookingdates", 400, "One", None),
        # Known API bug: a wrong data type should be rejected, but additionalneeds stores the boolean as sent
        ("additionalneeds", 200, False, False),
        # Known API bug: a wrong data type should be rejected, but additionalneeds stores the number as sent
        ("additionalneeds", 200, 0, 0),
        # Known API bug: a wrong data type should be rejected, but additionalneeds stores the boolean as sent
        ("additionalneeds", 200, True, True),
        # Known API bug: a wrong data type should be rejected, but additionalneeds stores the float as sent
        ("additionalneeds", 200, 8.9999, 8.9999),
    ])
    def test_put_wrong_data(self, base_url, token, existing_booking_id, key, expected_status_code, wrong_value, expected_value):

        put_payload = existing_booking_id["payload"].copy()
        put_payload[key] = wrong_value
        new_response = requests.put(f"{base_url}/booking/{existing_booking_id['id']}", json=put_payload, headers={"Cookie": f"token={token}"})
        assert new_response.status_code == expected_status_code, f"Expected {expected_status_code} with {key}, but got {new_response.status_code}"
        if expected_status_code == 400:
            assert new_response.text == "Bad Request"
        elif expected_status_code == 500:
            assert new_response.text == "Internal Server Error"
        else:
            body = new_response.json()
            assert body[key] == expected_value, f"{key}: expected {expected_value!r}, got {body[key]!r}"

    @pytest.mark.parametrize("date_key", ["checkin", "checkout"])
    @pytest.mark.parametrize("wrong_value, expected_status_code, expected_value", [
        # Known API bug: a wrong data type should be rejected, but the number is read as milliseconds since 1970-01-01
        (275759, 200, "1970-01-01"),
        # Known API bug: a wrong data type should be rejected, but the number is read as milliseconds since 1970-01-01
        (275760, 200, "1970-01-01"),
        # Known API bug: a wrong data type should be rejected, but the number is read as milliseconds since 1970-01-01
        (275761, 200, "1970-01-01"),
        # Known API bug: an invalid date should be rejected, but the string is read as year 275759 and stored cut to 4 digits
        ("275759", 200, "5759-01-01"),
        # Known API bug: an invalid date should be rejected, but the string is read as the max year 275760 and stored cut to 4 digits
        ("275760", 200, "5760-01-01"),
        # Known API bug: an invalid date should be rejected with 400, but a year past the max 275760 is stored as an Invalid Date
        ("275761", 200, "0NaN-aN-aN"),
    ])
    def test_put_wrong_data_nested_dict(self, base_url, token, existing_booking_id, date_key, wrong_value, expected_status_code, expected_value):

        put_payload = existing_booking_id["payload"]
        put_payload["bookingdates"][date_key] = wrong_value
        new_response = requests.put(f"{base_url}/booking/{existing_booking_id['id']}", json=put_payload, headers={"Cookie": f"token={token}"})
        assert new_response.status_code == expected_status_code, f"Expected {expected_status_code} with {date_key}, but got {new_response.status_code}"
        body = new_response.json()
        assert body["bookingdates"][date_key] == expected_value, f"{date_key}: expected {expected_value!r}, got {body['bookingdates'][date_key]!r}"

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

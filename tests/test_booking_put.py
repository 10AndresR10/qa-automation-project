import requests


class TestBookingPut:

    def test_put_method(self, base_url, auth_headers, created_booking):

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

        update_response = requests.put(f"{base_url}/booking/{created_booking}", json=payload, headers=auth_headers)

        body = update_response.json()

        assert update_response.status_code == 200
        assert body ["firstname"] == "Andres"
        assert body ["lastname"] == "Reyes"
        assert body ["totalprice"] == 100
        assert body ["depositpaid"] == True
        assert body ["bookingdates"]["checkin"] == "2026-01-01"
        assert body ["bookingdates"]["checkout"] == "2026-01-05"
        assert body ["additionalneeds"] == "Breakfast"


    def test_put_wrong_data(self, base_url, auth_headers, created_booking):

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

        new_response = requests.put(f"{base_url}/booking/{created_booking}", json= payload, headers=auth_headers)
        assert new_response.status_code == 500
        assert new_response.text == "Internal Server Error"

    def test_non_existent_booking_ID(self, base_url, auth_headers, booking_payload):

        none_id = 99999999999

        response = requests.put(f"{base_url}/booking/{none_id}", json= booking_payload, headers=auth_headers)

        assert response.status_code in [405, 403]
        if response.status_code == 405:
            assert response.text == "Method Not Allowed"

    def test_missing_required_field(self, base_url, auth_headers, booking_payload, created_booking):

        payload = booking_payload

        for key in list(payload):

            if key == "firstname":
                wrong_payload = payload.copy()
                del wrong_payload[key]
                new_response = requests.put(f"{base_url}/booking/{created_booking}", json= wrong_payload, headers=auth_headers)
                assert new_response.status_code == 400
                assert new_response.text == "Bad Request"

            if key == "lastname":
                wrong_payload = payload.copy()
                del wrong_payload[key]
                new_response = requests.put(f"{base_url}/booking/{created_booking}", json= wrong_payload, headers=auth_headers)
                assert new_response.status_code == 400
                assert new_response.text == "Bad Request"

            if key == "depositpaid":
                wrong_payload = payload.copy()
                del wrong_payload[key]
                new_response = requests.put(f"{base_url}/booking/{created_booking}", json= wrong_payload, headers=auth_headers)
                assert new_response.status_code == 400
                assert new_response.text == "Bad Request"

            if key == "totalprice":
                wrong_payload = payload.copy()
                del wrong_payload[key]
                new_response = requests.put(f"{base_url}/booking/{created_booking}", json= wrong_payload, headers=auth_headers)
                assert new_response.status_code == 400
                assert new_response.text == "Bad Request"

            if key == "bookingdates":
                wrong_payload = payload.copy()
                del wrong_payload[key]
                new_response = requests.put(f"{base_url}/booking/{created_booking}", json= wrong_payload, headers=auth_headers)
                assert new_response.status_code == 400
                assert new_response.text == "Bad Request"

            if key == "additionalneeds":
                wrong_payload = payload.copy()
                del wrong_payload[key]
                new_response = requests.put(f"{base_url}/booking/{created_booking}", json= wrong_payload, headers=auth_headers)
                assert new_response.status_code == 200


    def test_extremely_long_string_field(self, base_url, auth_headers, booking_payload, created_booking):

        payload = booking_payload

        long_string = "Andres Andres Andres Andres Andres Andres Andres Andres Andres Andres Andres Andres Andres "

        for key in list(payload):

            long_string_payload = payload.copy()
            if key == "bookingdates":
                long_string_payload["bookingdates"] = {
                    "checkin": long_string,
                    "checkout": long_string,
                }

            else:
                long_string_payload[key] = long_string

            new_response = requests.put(f"{base_url}/booking/{created_booking}", json= long_string_payload, headers=auth_headers)

            assert new_response.status_code == 200

            if key == "bookingdates":
                body = new_response.json()
                assert body["bookingdates"]["checkin"] == "0NaN-aN-aN"
                assert body["bookingdates"]["checkout"] == "0NaN-aN-aN"


    def test_empty_string_field(self, base_url, auth_headers, booking_payload, created_booking):

        payload = booking_payload

        for key in list(payload):
            empty_response = payload.copy()
            empty_response[key] = ""
            new_response = requests.put(f"{base_url}/booking/{created_booking}", json=empty_response, headers=auth_headers)

            if new_response.status_code != 200:
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


    def test_empty_string_nested_bookingdates_field(self, base_url, auth_headers, booking_payload, created_booking):

        payload = booking_payload

        for date_key in ["checkin", "checkout"]:

            update_payload = payload.copy()
            update_payload["bookingdates"] = payload["bookingdates"].copy()
            update_payload["bookingdates"][date_key] = ""

            new_response = requests.put(f"{base_url}/booking/{created_booking}", json=update_payload, headers=auth_headers)

            assert new_response.status_code == 200
            assert new_response.json()["bookingdates"][date_key] == "0NaN-aN-aN"


    def test_no_cookie_auth(self, base_url, booking_payload, created_booking):

        update_payload = booking_payload.copy()
        update_payload["firstname"] = "Andres"

        put_response = requests.put(f"{base_url}/booking/{created_booking}", json=update_payload)
        assert put_response.status_code == 403
        assert put_response.text == "Forbidden"

    def test_an_invalid_expired_token(self, base_url, booking_payload, created_booking):

        update_payload = booking_payload.copy()

        update_payload["firstname"] = "Andres"

        new_response = requests.put(f"{base_url}/booking/{created_booking}", json=update_payload, headers={"Cookie": "token=invalidtoken123"})

        assert new_response.status_code == 403
        assert new_response.text == "Forbidden"

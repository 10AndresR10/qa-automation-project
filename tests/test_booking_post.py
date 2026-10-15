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

    def test_wrong_data_type(self, base_url):

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

        new_value = 123456
        new_digit = str(new_value)
        new_payload = payload.copy()

        for key in new_payload:
            if key == "firstname" or key == "lastname":
                new_payload = payload.copy()
                new_payload[key] = new_value
                response = requests.post(f"{base_url}/booking", json=new_payload)
                assert response.status_code == 500
                assert response.text == "Internal Server Error"
                expected_results = {True: 500, False: 200}
                for i, expected_status in expected_results.items():
                    new_payload = payload.copy()
                    new_payload[key] = i
                    new_response = requests.post(f"{base_url}/booking", json=new_payload)
                    assert new_response.status_code == expected_status, f"Expected {expected_status} for {key}={i}, but got {new_response.status_code}"

                    if i:
                        assert new_response.text == "Internal Server Error"
                    else:
                        body = new_response.json()
                        stored_value = body["booking"][key]
                        assert stored_value is False, f"Expected {key} to be stored as False for input {i}, but got {stored_value}"
            
            elif key == "totalprice":
                new_payload = payload.copy()
                new_payload[key] = new_digit
                response = requests.post(f"{base_url}/booking", json= new_payload)
                assert response.status_code == 200

                for boolean in [True, False]:
                    new_payload = payload.copy()
                    new_payload[key] = boolean
                    new_response = requests.post(f"{base_url}/booking", json=new_payload)
                    assert new_response.status_code == 200
                    body = new_response.json()
                    stored_value = body["booking"]["totalprice"]
                    assert stored_value is None, f"Expected totalprice to be corrupted to null for input {boolean}, but got {stored_value}"
        
            elif key == "depositpaid":
                new_payload = payload.copy()
                new_payload[key] = new_digit
                response = requests.post(f"{base_url}/booking", json=new_payload)
                assert response.status_code == 200
                body = response.json()
                stored_value = body["booking"]["depositpaid"]
                assert stored_value is True, f"Expected depositpaid to coerce truthy string '{new_digit}' to True, but got {stored_value}"

                new_payload = payload.copy()
                new_payload[key] = new_value
                response = requests.post(f"{base_url}/booking", json=new_payload)
                assert response.status_code == 200

                for number in range(0, 2):
                    new_payload = payload.copy()
                    new_payload[key] = number
                    new_response = requests.post(f"{base_url}/booking", json=new_payload)
                    assert new_response.status_code == 200
                    body = new_response.json()
                    stored_value = body["booking"]["depositpaid"]
                    assert stored_value == bool(number), f"Expected depositpaid to coerce {number} to {bool(number)}, but got {stored_value}"

            elif key == "bookingdates":
                year_numbers = [275759, 275760, 275761]
                for item in payload[key]:
                    for year in year_numbers:
                        new_payload = payload.copy()
                        new_payload[key] = payload[key].copy()
                        new_payload[key][item] = str(year)
                        response = requests.post(f"{base_url}/booking", json=new_payload)
                        assert response.status_code == 200
                        body = response.json()
                        stored_value = body["booking"]["bookingdates"][item]
                        if year > 275760: 
                            assert "0NaN-aN-aN" in stored_value, f"Expected {item} to be corrupted to a NaN-containing string for input '{year}', but got {stored_value}"
                        elif year <= 275760:
                            expected_year = str(year)[-4:]
                            assert stored_value.startswith(expected_year), f"Expected {item} to be truncated to year '{expected_year}' from input '{year}', but got '{stored_value}'"

            elif key == "additionalneeds":
                new_payload = payload.copy()
                new_payload[key] = new_value
                response = requests.post(f"{base_url}/booking", json=new_payload)
                assert response.status_code == 200
                
                for bool_item in [True, False]:
                    new_payload = payload.copy()
                    new_payload[key] = bool_item
                    new_response = requests.post(f"{base_url}/booking", json=new_payload)
                    assert new_response.status_code == 200
                    body = new_response.json()
                    stored_value = body["booking"][key]
                    assert stored_value == bool_item, f"Expected {key} to coerce {bool_item} to {bool_item}, but got {stored_value}"


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

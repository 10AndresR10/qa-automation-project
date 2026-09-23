import requests
import random


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

        new_digit = ""
        for i in range(6):
            digit = str(random.randint(1,9))
            new_digit += digit
        new_value = int(new_digit)

        new_payload = payload.copy()

        for key in new_payload:
            if key == "firstname" or key == "lastname":
                new_payload = payload.copy()
                new_payload[key] = new_value
                response = requests.post(f"{self.base_url}/booking", json=new_payload)
                assert response.status_code == 500
                if response.text == "Internal Server Error":
                    for i in [True, False]: 
                        new_payload = payload.copy()
                        new_payload[key] = i
                        new_response = requests.post(f"{self.base_url}/booking", json=new_payload)

                        if new_response.status_code == 500:
                            assert new_response.text == "Internal Server Error"

                        else:
                            assert new_response.status_code == 200
            
            elif key == "totalprice":
                new_payload = payload.copy()
                new_payload[key] = new_digit
                response = requests.post(f"{self.base_url}/booking", json= new_payload)
                assert response.status_code == 200

                for i in [True, False]:
                    new_payload = payload.copy()
                    new_payload[key] = i
                    new_response = requests.post(f"{self.base_url}/booking", json=new_payload)
                    body = new_response.json()
                    assert new_response.status_code == 200
                    stored_value = body["booking"]["totalprice"]
                    assert stored_value is None, f"Expected totalprice to be corrupted to null for input {i}, but got {stored_value}"
           
            elif key == "depositpaid":
                new_payload = payload.copy()
                new_payload[key] = new_digit
                response = requests.post(f"{self.base_url}/booking", json=new_payload)
                body = response.json()
                stored_value = body["booking"]["depositpaid"]
                assert response.status_code == 200
                assert stored_value is True, f"Expected depositpaid to coerce truthy string '{new_digit}' to True, but got {stored_value}"

                new_payload = payload.copy()
                new_payload[key] = new_value
                response = requests.post(f"{self.base_url}/booking", json=new_payload)
                assert response.status_code == 200

                for i in range(0, 2):
                    new_payload = payload.copy()
                    new_payload[key] = i
                    new_response = requests.post(f"{self.base_url}/booking", json=new_payload)
                    body = new_response.json()
                    stored_value = body["booking"]["depositpaid"]
                    assert new_response.status_code == 200
                    assert stored_value == bool(i), f"Expected depositpaid to coerce {i} to {bool((i))}, but got {stored_value}"

            elif key == "bookingdates":
                new_payload = payload.copy()
                new_payload[key]["checkin"] = new_digit
                response = requests.post(f"{self.base_url}/booking", json=new_payload)
                assert response.status_code == 200
                body = response.json()
                stored_value = body["booking"]["bookingdates"]["checkin"]    
                assert "0NaN-aN-aN" in stored_value, f"Expected checkin to be corrupted to a NaN-containig string for inout '{new_digit}', but got {stored_value}"        


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
            
    def test_empty_string_field(self):

        payload = {
            "firstname": "",
            "lastname": "",
            "totalprice": False,
            "depositpaid": False,
            "bookingdates": {
                "checkin": "0NaN-aN-aN",
                "checkout": "0NaN-aN-aN"
            },
            "additionalneeds": ""
        }

    
        response = requests.post(f"{self.base_url}/booking", json=payload)
        
        body = response.json()
        assert response.status_code == 200
        assert body["booking"]["firstname"] == ""
        assert body["booking"]["lastname"] == ""
        assert body["booking"]["totalprice"] is None
        assert body["booking"]["bookingdates"]["checkin"] == "0NaN-aN-aN"
        assert body["booking"]["bookingdates"]["checkout"] == "0NaN-aN-aN"
        assert body["booking"]["additionalneeds"] == ""
        

    def test_extremely_long_string(self):

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

        response = requests.post(f"{self.base_url}/booking", json= payload)

        body = response.json()

        assert body["booking"]["firstname"] == payload["firstname"]
        assert body["booking"]["lastname"] == payload["lastname"]
        assert body["booking"]["additionalneeds"] == payload["additionalneeds"]

    def test_equivalence_partitioning_checkvariables(self):
        
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

        response = requests.post(f"{self.base_url}/booking", json= payload)
        
        body = response.json()

        assert body["booking"]["bookingdates"]["checkin"] == "0NaN-aN-aN"
        assert body["booking"]["bookingdates"]["checkout"] == "0NaN-aN-aN"

    def test_equivalence_partitioning_valid_dates(self):

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

        response = requests.post(f"{self.base_url}/booking", json=payload)
        assert response.status_code == 200
        body = response.json()

        assert body["booking"]["bookingdates"]["checkin"] == "2026-12-01"
        assert body["booking"]["bookingdates"]["checkout"] == "2026-12-10"

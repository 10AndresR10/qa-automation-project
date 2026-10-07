import requests
import random
import string


class TestBookingDelete:

    def test_delete_method(self, base_url, token, existing_booking_id):

        new_response = requests.delete(f"{base_url}/booking/{existing_booking_id["id"]}", headers={"Cookie": f"token={token}"})

        assert new_response.status_code == 201
        assert new_response.text == "Created"

        new_get = requests.get(f"{base_url}/booking/{existing_booking_id["id"]}")
        
        assert new_get.status_code == 404
        assert new_get.text == "Not Found"
        
    
    def test_non_existent_booking_ID(self, base_url, token):

        non_id = 9999

        response = requests.delete(f"{base_url}/booking/{non_id}", headers={"Cookie": f"token={token}"})
        assert response.status_code in [405, 403]
        if response.status_code == 405:
            assert response.text == "Method Not Allowed"

    
    def test_already_deleted_booking_ID(self, base_url, token, existing_booking_id):

        for i in range(2):
            new_response = requests.delete(f"{base_url}/booking/{existing_booking_id["id"]}", headers={"Cookie": f"token={token}"})
            if i == 0:
                assert new_response.status_code == 201
                assert new_response.text == "Created"
            else:
                assert new_response.status_code == 405
                assert new_response.text == "Method Not Allowed"

    
    def test_malformed_id(self, base_url, token):

        lower_case = random.sample(list(string.ascii_lowercase), k=2)
        upper_case = random.sample(list(string.ascii_uppercase), k=3)
        digits = random.sample(list(string.digits), k=3)

        new_id = "" 
        for i in lower_case:       
            new_id += i
        for j in upper_case:
            new_id += j
        for k in digits:
            new_id += k

        new_response = requests.delete(f"{base_url}/booking/{new_id}", headers= {"Cookie": f"token={token}"})

        assert new_response.status_code in [403, 405]
        if new_response.status_code == 405:
            assert new_response.text == "Method Not Allowed"

    def test_invalid_auth_token(self, base_url, existing_booking_id):

        new_response = requests.delete(f"{base_url}/booking/{existing_booking_id["id"]}", headers= {"Cookie": f"token=invalidtoken123"})

        assert new_response.status_code == 403
        assert new_response.text == "Forbidden"


    def test_no_cookie_auth_token(self, base_url, existing_booking_id):

        new_response = requests.delete(f"{base_url}/booking/{existing_booking_id["id"]}")
        assert new_response.status_code == 403
        assert new_response.text == "Forbidden"

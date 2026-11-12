import requests
import random
import string


class TestBookingDelete:

    def test_delete_method(self, base_url, token, existing_booking_id):

        new_response = requests.delete(f"{base_url}/booking/{existing_booking_id['id']}", headers={"Cookie": f"token={token}"})

        assert new_response.status_code == 201, f"Expected 201, but got {new_response.status_code}, {new_response.text} with these headers {new_response.headers}"
        assert new_response.text == "Created"

        new_get = requests.get(f"{base_url}/booking/{existing_booking_id['id']}")
        
        assert new_get.status_code == 404, f"Follow-up GET of deleted booking {existing_booking_id['id']}: expected 404, but got {new_get.status_code}, {new_get.text} with these headers {new_get.headers}"
        assert new_get.text == "Not Found"
        
    
    def test_non_existent_booking_ID(self, base_url, token, non_existent_booking_id):

        response = requests.delete(f"{base_url}/booking/{non_existent_booking_id}", headers={"Cookie": f"token={token}"})
        # Known API bug: a missing booking should return 404 Not Found, but the API returns 405
        assert response.status_code == 405, f"DELETE of non-existent booking {non_existent_booking_id}: expected 405, but got {response.status_code}, {response.text} with these headers {response.headers}"
        assert response.text == "Method Not Allowed"

    
    def test_already_deleted_booking_ID(self, base_url, token, existing_booking_id):

        for i in range(2):
            new_response = requests.delete(f"{base_url}/booking/{existing_booking_id['id']}", headers={"Cookie": f"token={token}"})
            if i == 0:
                assert new_response.status_code == 201, f"First DELETE of booking {existing_booking_id['id']}: expected 201, but got {new_response.status_code}, {new_response.text} with these headers {new_response.headers}"
                assert new_response.text == "Created"
            else:
                # Known API bug: a missing booking should return 404 Not Found, but the API returns 405
                assert new_response.status_code == 405, f"Second DELETE of booking {existing_booking_id['id']}: expected 405, but got {new_response.status_code}, {new_response.text} with these headers {new_response.headers}"
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

        # Known API bug: a missing booking should return 404 Not Found, but the API returns 405
        assert new_response.status_code == 405, f"DELETE with malformed ID {new_id!r}: expected 405, but got {new_response.status_code}, {new_response.text} with these headers {new_response.headers}"
        assert new_response.text == "Method Not Allowed"

    def test_invalid_auth_token(self, base_url, existing_booking_id):

        new_response = requests.delete(f"{base_url}/booking/{existing_booking_id['id']}", headers= {"Cookie": "token=invalidtoken123"})
        assert new_response.status_code == 403, f"DELETE with an invalid token: expected 403, but got {new_response.status_code}, {new_response.text} with these headers {new_response.headers}"
        assert new_response.text == "Forbidden"

        get_response = requests.get(f"{base_url}/booking/{existing_booking_id['id']}")
        assert get_response.status_code == 200, f"Follow-up GET of booking {existing_booking_id['id']}: expected 200, but got {get_response.status_code}, {get_response.text} with these headers {get_response.headers}"

    def test_no_cookie_auth_token(self, base_url, existing_booking_id):

        new_response = requests.delete(f"{base_url}/booking/{existing_booking_id['id']}")
        assert new_response.status_code == 403, f"DELETE without a token: expected 403, but got {new_response.status_code}, {new_response.text} with these headers {new_response.headers}"
        assert new_response.text == "Forbidden"

        get_response = requests.get(f"{base_url}/booking/{existing_booking_id['id']}")
        assert get_response.status_code == 200, f"Follow-up GET of booking {existing_booking_id['id']}: expected 200, but got {get_response.status_code}, {get_response.text} with these headers {get_response.headers}"

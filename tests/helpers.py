import requests


def delete_booking(base_url, token, booking_id):
    delete_request = requests.delete(f"{base_url}/booking/{booking_id}", headers={"Cookie": f"token={token}"})
    if delete_request.status_code == 403:
        new_token = get_token(base_url)
        retry_request = requests.delete(f"{base_url}/booking/{booking_id}", headers={"Cookie": f"token={new_token}"})
        get_response = requests.get(f"{base_url}/booking/{booking_id}")
        assert get_response.status_code == 404, f"Cleanup of booking {booking_id}: DELETE got {delete_request.status_code}, retry with a fresh token got {retry_request.status_code}, {retry_request.text} with these headers {retry_request.headers}, but the booking still exists: GET returned {get_response.status_code}"
    else:
        assert delete_request.status_code in [201, 405], f"Cleanup of booking {booking_id}: expected 201 or 405, but got {delete_request.status_code}, {delete_request.text} with these headers {delete_request.headers}"

def get_token(base_url):
    auth_response = requests.post(f"{base_url}/auth", json={"username": "admin", "password": "password123"})
    assert auth_response.status_code == 200, f"Auth: expected 200, but got {auth_response.status_code}, {auth_response.text} with these headers {auth_response.headers}"
    assert "token" in auth_response.json(), auth_response.text
    token = auth_response.json()["token"]
    return token

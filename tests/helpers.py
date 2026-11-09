import requests


def delete_booking(base_url, token, booking_id):
    delete_request = requests.delete(f"{base_url}/booking/{booking_id}", headers={"Cookie": f"token={token}"})
    if delete_request.status_code == 403:
        get_response = requests.get(f"{base_url}/booking/{booking_id}")
        assert get_response.status_code == 404, f"Cleanup of booking {booking_id}: DELETE got {delete_request.status_code}, {delete_request.text} with these headers {delete_request.headers}, but the booking still exists: GET returned {get_response.status_code}"
    else:
        assert delete_request.status_code in [201, 405], f"Cleanup of booking {booking_id}: expected 201 or 405, but got {delete_request.status_code}, {delete_request.text} with these headers {delete_request.headers}"

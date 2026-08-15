

from multiprocessing import Value


def is_valid_status_code(num):

    if num == 200 or num == 201 or num == 204:
        return True 
    else:
        return False

print(is_valid_status_code(200))
print(is_valid_status_code(201))
print(is_valid_status_code(204))

print(is_valid_status_code(500))
print(is_valid_status_code(400))
print(is_valid_status_code(404))


def check_code():
    results = [200, 404, 200, 500, 200, 400]

    check_number = 0
    for i in results:
        if i == 200:
            check_number += 1

    print(f"200 appeared {check_number} times")

check_code()


booking = {
    "firstname": "John",
    "lastname": "Smith",
    "totalprice": 150,
    "depositpaid": True
    }

def check_key(data):
    for key in data:
        if key == "firstname":
            print(data[key])
    

check_key(booking)




def exists_key(data):
    for key in data:
        if key == "totalprice":
            print(f"{key} is a key")

exists_key(booking)


def check_response(status_code):
    if status_code == 200:
        print("Success")
    elif status_code in range(400, 500, 1):
        print("Client error")
    elif status_code in range(500, 600, 1):
        print("Server error")
    else:
        print("Unexpected")


check_response(200)
check_response(202)
check_response(400)
check_response(404)
check_response(499)
check_response(500)
check_response(599)
check_response(600)
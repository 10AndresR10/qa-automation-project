Test Cases GET Method
Test 1: GET request (happy path) - retrieves booking details for a valid, existing ID and returns a 200 status code.
Test 2: GET request with a malformed ID (e.g. non-numeric, like "abc") - returns a 400 status code (Bad Request).
Test 3: GET request with a non-existent ID (valid format, but no matching record) - returns a 404 status code (Not Found).
Test 4: GET request with an empty ID - returns a 400 status code (Bad Request).
Test 5: GET request with an extremely large ID value - returns a 400 status code (Bad Request), per API documentation.

Test Cases POST Method
Test 1: POST request (happy path) - creates a new booking with valid data and returns a 200 status code.
Test 2: POST request with a wrong data type (e.g. "price" sent as a string instead of a number) - returns a 400 status code (Bad Request).
Test 3: POST request with a missing required field (e.g. "firstname" omitted entirely) - returns a 400 status code (Bad Request).
Test 4: POST request with empty string field(s) (e.g. "firstname": "") - returns a 400 status code (Bad Request).
Test 5: POST request with an extremely long string in a field (e.g. "firstname") - returns a 400 status code (Bad Request), per API documentation.
Test 6: POST request - equivalence partitioning on checkin/checkout dates: a valid range (checkout after checkin) returns 200; an invalid range (checkout before or equal to checkin) returns 400.

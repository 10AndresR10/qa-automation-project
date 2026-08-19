# Test Cases — GET Method

**Test 1: GET request (happy path)**
Retrieves booking details for a valid, existing ID.
Expected: 200
Actual: 200 ✅

**Test 2: GET request with a malformed ID (e.g. non-numeric, like "abc")**
Expected (assumed): 400 Bad Request
Actual: **404 Not Found**

**Test 3: GET request with a non-existent ID (valid format, but no matching record)**
Expected: 404 Not Found
Actual: 404 Not Found ✅

**Test 4: GET request with a whitespace-only ID**
(Note: a truly empty ID collapses onto the `/booking` collection route and isn't a distinct case; tested with `/booking/    ` instead.)
Expected (assumed): 400 Bad Request
Actual: **404 Not Found**

**Test 5: GET request with an extremely large ID value**
(Tested with a 41-digit numeric ID.)
Expected (assumed): 400 Bad Request, per API documentation
Actual: **404 Not Found**

---

# Test Cases — POST Method

**Test 1: POST request (happy path)**
Creates a new booking with valid data.
Expected: 200
Actual: 200 ✅

**Test 2: POST request with a wrong data type per field**
(e.g. numeric strings for `firstname`/`lastname`, `totalprice` as a string, `depositpaid` as a string, `checkin`/`checkout` as ints, `additionalneeds` as an int.)
Expected (assumed): 400 Bad Request
Actual: **500 Internal Server Error** ("Internal Server Error" body) for every mistyped field.

**Test 3: POST request with a missing required field**
Expected (assumed): 400 Bad Request for any omitted field
Actual:
- Omitting `firstname`, `lastname`, `totalprice`, `depositpaid`, or `bookingdates` → **500 Internal Server Error**
- Omitting `additionalneeds` → **200** (field is optional, not required — original assumption was wrong to treat it as required)

**Test 4: POST request with empty string field(s)**
(`firstname`/`lastname`/`additionalneeds` as `""`, dates as `"0NaN-aN-aN"`, `totalprice`/`depositpaid` as `False`.)
Expected (assumed): 400 Bad Request
Actual: **200** — the API accepts empty strings and malformed date strings with no validation, and silently corrupts the data instead of rejecting it:
- 🐛 **Bug:** sending `totalprice: False` (a boolean) is accepted with a 200, but the returned/stored `totalprice` comes back as **`None`** — the value is silently dropped/corrupted rather than the request being rejected.
- 🐛 **Bug:** the clearly-invalid date string `"0NaN-aN-aN"` is accepted verbatim for both `checkin` and `checkout` with no format validation.

**Test 5: POST request with an extremely long string in a field (e.g. "firstname")**
Expected (assumed): 400 Bad Request, per API documentation
Actual: **Not yet executed** — no automated test written for this case.

**Test 6: POST request — equivalence partitioning on checkin/checkout dates**
Valid range (checkout after checkin) vs. invalid range (checkout before/equal to checkin).
Expected (assumed): valid → 200, invalid → 400
Actual: **Not yet executed** — no automated test written for this case.

---

## Summary of bugs / API behavior discovered

1. **Invalid input triggers 500s, not 400s.** Any malformed field type or missing required field results in a raw `500 Internal Server Error` rather than a client-facing `400 Bad Request`. The API does not distinguish client error from server error.
2. **Non-standard/invalid IDs on GET return 404, not 400.** Malformed IDs, whitespace IDs, and oversized IDs are all treated the same as "not found" — there is no separate bad-request path for unparseable IDs.
3. **`additionalneeds` is optional**, not required — omitting it returns 200, unlike every other field.
4. **Empty strings and malformed data are silently accepted (200)** instead of rejected, and in the case of `totalprice` sent as a boolean, the value is **corrupted to `None`** rather than validated or rejected. This is a data-integrity bug, not just a missing-validation issue.
5. **Untested per API docs:** long-string field limits (Test 5) and checkin/checkout date-range validation (Test 6) still need automated coverage — current actual behavior is unknown.

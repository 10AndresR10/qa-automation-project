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
(Tested with `firstname` at 288 chars, `lastname` at 299 chars, `additionalneeds` at 360 chars.)
Expected (assumed): 400 Bad Request, per API documentation
Actual: **200** — all three long strings are accepted and echoed back unmodified (no truncation, no length validation).

**Test 6: POST request — equivalence partitioning on checkin/checkout dates**
(Tested with an out-of-range invalid pair: `checkin: "2099-13-01"` (month 13), `checkout: "1999-01-32"` (day 32).)
Expected (assumed): valid → 200, invalid → 400
Actual: **200** — both invalid dates are silently coerced to `"0NaN-aN-aN"` instead of being rejected. (Only the invalid-range half of this test has been automated; the valid-range case still needs a dedicated test.)

---

# Test Cases — PUT Method

**Test 1: PUT request (happy path)**
Creates a booking, authenticates, then fully updates all fields of the existing booking with valid data.
Expected: 200, response body reflects all updated field values.
Actual: 200 ✅ — all fields (`firstname`, `lastname`, `totalprice`, `depositpaid`, `bookingdates.checkin`, `bookingdates.checkout`, `additionalneeds`) are returned updated as sent.

**Test 2: PUT request with wrong data type per field**
(`firstname` as an int, `lastname` as a bool, `totalprice` as a string, `depositpaid` as an int, `checkin` as an int, `checkout` as a whitespace string, `additionalneeds` as a bool — auth token included.)
Expected (assumed): 400 Bad Request
Actual: **500 Internal Server Error** ("Internal Server Error" body) — consistent with POST's handling of mistyped fields (see POST Test 2).

**Test 3: PUT request against a non-existent booking ID**
(Tested with a 11-digit numeric ID, `99999999999`, valid auth token included.)
Expected (assumed): 404 Not Found
Actual: **405 Method Not Allowed** ("Method Not Allowed" body) — unlike GET (see GET Test 3), a non-existent ID on PUT is not treated as "not found"; it's rejected before the ID is even looked up.

**Test 4: PUT request with a missing required field**
(Created a valid booking, then sent a full update payload with each field omitted in turn — `firstname`, `lastname`, `depositpaid`, `totalprice`, `bookingdates`, and `additionalneeds` — valid auth token included each time.)
Expected (assumed): 400 Bad Request for any omitted field
Actual:
- Omitting `firstname`, `lastname`, `depositpaid`, `totalprice`, or `bookingdates` → **400 Bad Request** ("Bad Request" body) ✅ — but note this is **inconsistent with POST's** handling of the same condition, which returns 500 (see POST Test 3 and bug #1); PUT validates a missing required field before hitting the server error POST triggers.
- Omitting `additionalneeds` → **200** — consistent with PUT Test 1/POST Test 3: `additionalneeds` is optional, not required (see bug #3).

**Test 5: PUT request with an extremely long string in a field**
(Created a valid booking, then sent a full update payload with each field in turn replaced by a 91-char string, valid auth token included — including `totalprice` and `depositpaid`, which are normally numeric/boolean.)
Expected (assumed): 400 Bad Request, per API documentation
Actual: **200** for every field, including `totalprice`/`depositpaid` set to a long string — consistent with POST's long-string handling (see POST Test 5) and, for the type mismatch on `totalprice`/`depositpaid`, notably *not* the 500 seen in PUT Test 2's wrong-data-type test; a single mistyped field alongside otherwise-valid data doesn't trigger the same server error as changing every field's type at once.
⚠️ **Test gap:** the `bookingdates` iteration has a copy/paste bug — it sets top-level `checkin`/`checkout` keys instead of the nested `bookingdates.checkin`/`bookingdates.checkout`, so the nested `bookingdates` object is never actually replaced with a long string. This case still needs to be re-tested correctly.

---

## Test Cases — PUT Method: still needed

- PUT with no `Cookie`/auth token (expect 403 Forbidden, per API docs)
- PUT with an invalid/expired token
- PUT with empty-string field(s)
- PUT with a genuinely long-string `bookingdates.checkin`/`bookingdates.checkout` (Test 5's nested-field case is currently untested — see gap noted above)
- Partial update via PATCH, for comparison (out of scope for this file but worth noting as a gap)

---

## Summary of bugs / API behavior discovered

1. **Invalid input triggers 500s, not 400s — for mistyped fields.** A malformed field type (wrong data type) results in a raw `500 Internal Server Error` rather than a client-facing `400 Bad Request`, on both POST and PUT. A *missing* required field behaves inconsistently across methods — see bug #9.
2. **Non-standard/invalid IDs on GET return 404, not 400.** Malformed IDs, whitespace IDs, and oversized IDs are all treated the same as "not found" — there is no separate bad-request path for unparseable IDs.
3. **`additionalneeds` is optional**, not required — omitting it returns 200, unlike every other field.
4. **Empty strings and malformed data are silently accepted (200)** instead of rejected, and in the case of `totalprice` sent as a boolean, the value is **corrupted to `None`** rather than validated or rejected. This is a data-integrity bug, not just a missing-validation issue.
5. **No length limit on string fields.** Fields up to 360 characters (`firstname`, `lastname`, `additionalneeds`) are accepted and returned as-is with a 200 — no server-side length validation.
6. **Invalid calendar dates are silently coerced, not rejected.** An out-of-range date like `checkin: "2099-13-01"` (month 13) or `checkout: "1999-01-32"` (day 32) returns 200, and both values come back corrupted to `"0NaN-aN-aN"` rather than the request being rejected — consistent with bug #4.
7. **Still untested:** the valid-range half of Test 6 (checkout genuinely after checkin) has not been automated yet.
8. **PUT against a non-existent ID returns 405, not 404.** Unlike GET, which treats any unresolvable ID as "not found" (see bug #2), PUT against a well-formed but non-existent ID returns `405 Method Not Allowed` — inconsistent handling of the same underlying condition (no matching record) across methods.
9. **Missing required field is handled differently by POST vs. PUT.** POST returns `500 Internal Server Error` when a required field is omitted (bug #1), but PUT returns `400 Bad Request` for the identical condition — the two methods validate the same requirement at different points in the request lifecycle.
10. **No length limit on PUT string fields either**, matching bug #5 on POST — long strings (91 chars tested) in any field, including a numeric/boolean field replaced with a string, return 200 with no length or type validation, and don't trigger the 500 seen when every field is mistyped at once (see PUT Test 2). **Automation gap:** the `bookingdates` case in this test doesn't actually exercise a long nested date string due to a copy/paste bug — see PUT Test 5.

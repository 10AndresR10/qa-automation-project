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
(Sent a valid payload with one field in turn replaced by a wrong type: `firstname`/`lastname` as `12345`, `True`, `False` and `3.14`; `totalprice` as `"One"`, `"12345"`, `True`, `False` and `-1000`; `depositpaid` as `"True"`, `"False"`, `"Andres"`, `123456`, `3.1233`, `0` and `-99`; the whole `bookingdates` object as `True`, `False`, `0`, `12345`, `-12345`, `"Andres"` and `3.14`; and `additionalneeds` as `0`, `12345`, `-12345`, `True`, `False` and `3.14`.)
Expected (assumed): 400 Bad Request for any field
Actual:
- `firstname`/`lastname` set to `12345`, `True` or `3.14` → **500 Internal Server Error** ("Internal Server Error" body) — 🐛 **Bug:** the server crashes instead of returning 400 (see bug #1). PUT accepts a number in these fields instead (see bug #18).
- `firstname`/`lastname` set to `False` → **200**, stored as the boolean `false` — 🐛 **Bug:** the falsy value isn't rejected like `True` is (see bug #14).
- `totalprice` set to `"One"`, `True` or `False` → **200**, but the stored `totalprice` comes back as **`null`** — 🐛 **Bug:** the same silent corruption as bug #4. `totalprice` doesn't distinguish `True` from `False`.
- `totalprice` set to `"12345"` → **200**, coerced to the number `12345` — reasonable type coercion, not a bug.
- `totalprice` set to `-1000` → **200**, stored as `-1000` — 🐛 **Bug:** the type is correct, but a negative price should be rejected (see bug #21). This case checks an invalid value, not a wrong type, so it may move to its own test.
- `depositpaid` set to `"True"`, `"Andres"`, `123456`, `3.1233` or `-99` → **200**, coerced to `true` — a non-empty string or a non-zero number is truthy, not a bug.
- `depositpaid` set to `0` → **200**, coerced to `false` (`bool(0)`), not a bug.
- `depositpaid` set to `"False"` → **200**, coerced to **`true`** — 🐛 **Bug:** the truthy-string rule turns `"False"` into the opposite of what was sent, the same as PUT (see bug #19).
- `bookingdates` set to `True`, `False`, `0`, `12345`, `-12345`, `"Andres"` or `3.14` (replacing the whole nested object) → **500 Internal Server Error** ("Internal Server Error" body) — 🐛 **Bug:** the server crashes instead of returning 400. **Inconsistent with PUT**, which correctly rejects the same kinds of values with 400 (see bug #20).
- `additionalneeds` set to `0`, `12345`, `-12345`, `True`, `False` or `3.14` → **200**, stored as sent — 🐛 **Bug:** no type validation (see bug #15).
- Re-confirmed on 2026-10-26 by sending the requests directly: the raw JSON stores `firstname: False` as `false`, `depositpaid` as `true`/`false` (not `1`/`0`), and `additionalneeds` as `0`, `12345`, `-12345`, `true`, `false` and `3.14`. The automated asserts can't tell these apart on their own, because in Python `0 == False` and `True == 1`.
- ✅ **Test status: REFACTORED (2026-10-26).** `test_wrong_data_type` used to loop over the fields with one `if key == ...` block per field, so the first failing field stopped the test and hid the rest, and some inputs (`totalprice: "123456"`, `depositpaid: 123456`, `additionalneeds: 123456`) only had their status code checked. It is now parametrized like PUT Test 2: each row holds the field, the wrong value, the expected status and the expected stored value — 33 cases in total, all passing. The `500` cases assert the `"Internal Server Error"` body, and every `200` case compares the stored value with the row's expected value. Every row has its own comment: `# Known API bug` for bugs, and a short note for coercions that aren't bugs.
- ⚠️ **Coverage gap (2026-10-26):** the old loop also sent 6-digit numeric strings (`275759`, `275760`, `275761`) to the nested `bookingdates.checkin`/`checkout` fields (see bug #16). The refactor removed these cases, because the table only replaces whole top-level fields. They are planned as their own parametrized boundary-value test; until then, bug #16 isn't covered by an automated test.

**Test 3: POST request with a missing required field**
Expected (assumed): 400 Bad Request for any omitted field
Actual:
- Omitting `firstname`, `lastname`, `totalprice`, `depositpaid`, or `bookingdates` → **500 Internal Server Error**
- Omitting `additionalneeds` → **200** (field is optional, not required — original assumption was wrong to treat it as required)

**Test 4: POST request with empty string field(s)**
(Every field set to `""` in a single request: `firstname`, `lastname`, `totalprice`, `depositpaid`, `bookingdates.checkin`, `bookingdates.checkout`, `additionalneeds`.)
Expected (assumed): 400 Bad Request
Actual: **200** — the API accepts empty strings with no validation, and silently corrupts the non-string fields instead of rejecting them:
- `firstname`, `lastname`, `additionalneeds` → stored as `""`, as sent.
- 🐛 **Bug:** `totalprice: ""` comes back as **`None`** — the value is silently dropped/corrupted rather than the request being rejected (bug #4).
- 🐛 **Bug:** `depositpaid: ""` comes back coerced to boolean **`false`** instead of being stored as sent or rejected — the same corruption as PUT Test 6 (bug #13).
- 🐛 **Bug:** `checkin: ""` and `checkout: ""` both come back corrupted to **`"0NaN-aN-aN"`** — the same coercion as bug #6, and the same result PUT gives for an empty nested date (PUT Test 7).
- ✅ **Test status: FIXED (2026-10-12).** `test_empty_string_field` used to send `totalprice`/`depositpaid` as `False` and both dates as `"0NaN-aN-aN"`, so only 3 of the 7 fields were actually empty strings, and `depositpaid` was never asserted. Every field is now `""`, and all seven stored values are asserted. The old payload also showed that the API accepts the string `"0NaN-aN-aN"` verbatim as a date; that behavior is no longer covered by an automated test.

**Test 5: POST request with an extremely long string in a field (e.g. "firstname")**
(Tested with `firstname` at 288 chars, `lastname` at 299 chars, `additionalneeds` at 360 chars.)
Expected (assumed): 400 Bad Request, per API documentation
Actual: **200** — all three long strings are accepted and echoed back unmodified (no truncation, no length validation).

**Test 6: POST request — equivalence partitioning on checkin/checkout dates**
(Tested with an out-of-range invalid pair: `checkin: "2099-13-01"` (month 13), `checkout: "1999-01-32"` (day 32).)
Expected (assumed): valid → 200, invalid → 400
Actual: **200** — both invalid dates are silently coerced to `"0NaN-aN-aN"` instead of being rejected.

**Test 6b: POST request — equivalence partitioning, valid-range counterpart**
(Tested with a well-formed pair where `checkout` genuinely comes after `checkin`: `checkin: "2026-12-01"`, `checkout: "2026-12-10"`.)
Expected: 200, both dates returned as sent.
Actual: **200** ✅ — both dates are returned unmodified, as expected. Confirmed by `test_equivalence_partitioning_valid_dates`. This completes the equivalence-partitioning pair for Test 6 (see bug #7, now resolved).

---

**POST test run — 2026-09-29:** all 7 tests in `test_booking_post.py` pass. `test_wrong_data_type` is no longer flaky (see Test 2). See the full-suite results at the end of this file.

**POST test run — 2026-09-30:** all 7 tests in `test_booking_post.py` pass after tightening the truncated-year assertion (see Test 2). `test_wrong_data_type` was then run 12 more times in a row: 12/12 passed. The date values are random, so a direct check was also made to confirm the API behavior hasn't changed: `"193735"` → `"3735-01-01"`, `"123456"` → `"3456-01-01"`, `"543219"` → `"0NaN-aN-aN"` (bug #16 still present).
Later the same day, the `firstname`/`lastname` boolean checks in `test_wrong_data_type` were rewritten to assert bug #14 directly (see Test 2). All 7 tests in `test_booking_post.py` pass.

**POST test run — 2026-10-26:** all 44 tests in `test_booking_post.py` pass after parametrizing `test_wrong_data_type` (see Test 2). The count is higher than before because each wrong-data-type case is now reported as its own test (33 cases).

---

# Test Cases — PUT Method

**Test 1: PUT request (happy path)**
Creates a booking, authenticates, then fully updates all fields of the existing booking with valid data.
Expected: 200, response body reflects all updated field values.
Actual: 200 ✅ — all fields (`firstname`, `lastname`, `totalprice`, `depositpaid`, `bookingdates.checkin`, `bookingdates.checkout`, `additionalneeds`) are returned updated as sent.
- ✅ **Test status: FIXED (2026-10-12).** `test_put_method` used to call `.json()` before checking the status code, so a non-200 response without a JSON body failed with a JSON decode error instead of the real problem. It now asserts the status first and shows the response body in the failure message. The update payload also used to keep `depositpaid`, `bookingdates` and `additionalneeds` the same as the original booking (`True`, `2026-01-01`/`2026-01-05`, `"Breakfast"`), so the test would still pass if the API ignored those fields. Every field now changes (`depositpaid: False`, `2026-02-01`/`2026-02-05`, `"Soccer"`), so the test shows that each field is actually updated.

**Test 2: PUT request with wrong data type per field**
(Created a valid booking, then sent a full update payload with one field in turn replaced by a wrong type, valid auth token included: `firstname`/`lastname` as `0`, `True` and `False`; `totalprice` as `"One"`, `True` and `False`; `depositpaid` as `0`, `"True"`, `"False"` and `888.0`; the whole `bookingdates` object as `0`, `False` and `"One"`; and `additionalneeds` as `False`, `0`, `True` and `8.9999`.)
Expected (assumed): 400 Bad Request for any field
Actual:
- `firstname`/`lastname` set to `0` → **200**, stored as the number `0` — 🐛 **Bug:** the wrong type is accepted and stored as sent. This is **inconsistent with POST**, which returns 500 for a number in the same fields (see POST Test 2 and bug #18).
- `firstname`/`lastname` set to `True` → **500 Internal Server Error** ("Internal Server Error" body) — 🐛 **Bug:** the server crashes instead of returning 400, the same as POST (see bug #14).
- `firstname`/`lastname` set to `False` → **200**, stored as the boolean `false` — 🐛 **Bug:** the same `True`-vs-`False` split as POST (see bug #14).
- `totalprice` set to `"One"`, `True` or `False` → **200**, but the stored `totalprice` comes back as **`null`** — 🐛 **Bug:** the same silent corruption as bug #4. Like POST, `totalprice` doesn't distinguish `True` from `False`.
- `depositpaid` set to `0` → **200**, coerced to `false` — the same numeric-truthiness coercion as POST (`bool(0)`), not a bug (see POST Test 2).
- `depositpaid` set to `"True"` → **200**, coerced to `true` — a non-empty string is truthy, the same truthy-string coercion as POST, not a bug.
- `depositpaid` set to `888.0` → **200**, coerced to `true` — a non-zero number is truthy, not a bug.
- `depositpaid` set to `"False"` → **200**, coerced to **`true`** — 🐛 **Bug:** the same truthy-string rule turns `"False"` into the opposite of what was sent (see bug #19).
- `bookingdates` set to `0`, `False` or `"One"` (replacing the whole nested object) → **400 Bad Request** ("Bad Request" body) ✅ — the only field actually rejected, the same as replacing it with `""` (see Test 6).
- `additionalneeds` set to `False`, `0`, `True` or `8.9999` → **200**, stored as sent (`false`, `0`, `true`, `8.9999`) — 🐛 **Bug:** no type validation, the same as POST (see bug #15). Unlike `firstname`/`lastname`, `True` doesn't cause a 500 here.
- Re-confirmed on 2026-10-24 by sending the requests directly: the raw JSON response stores `firstname`/`lastname` as the number `0` and `additionalneeds` as the boolean `false`. The automated asserts alone can't show this, because in Python `0 == False`.
- Re-confirmed on 2026-10-25 by sending the new cases directly: the raw JSON stores `firstname`/`lastname: False` as `false`, `depositpaid` as `true` for `"True"`, `"False"` and `888.0`, and `additionalneeds` as `0`, `true` and `8.9999`. The automated asserts can't tell these apart on their own either, because in Python `True == 1`.
- Originally this was one manual request with **every** field mistyped at once (`checkin` as an int, `checkout` as a whitespace string), which returned **500 Internal Server Error**. With one wrong field per request, only `True` in `firstname`/`lastname` returns 500.
- ✅ **Test status: REFACTORED (2026-10-24).** `test_put_wrong_data` is now parametrized like Test 4–6: each field runs as its own case, and each row holds the wrong value, the expected status and the expected stored value. The `400` case (`bookingdates`) asserts the `"Bad Request"` body instead of parsing JSON, and every `200` case compares the stored value with the row's expected value. The bug rows have `# Known API bug` comments.
- ✅ **Test status: EXTENDED (2026-10-25).** Added boolean cases for `firstname`/`lastname` and `totalprice`, string and float cases for `depositpaid`, boolean and string cases for `bookingdates`, and number, boolean and float cases for `additionalneeds` — 20 cases in total, all passing. The test has a new `500` branch that asserts the `"Internal Server Error"` body. Every row has its own comment: `# Known API bug` for bugs, and a short note for correct rejections and coercions that aren't bugs.

**Test 3: PUT request against a non-existent booking ID**
(Created a valid booking, deleted it, then sent a full update payload to the now-deleted ID, valid auth token included. Originally tested with a hard-coded 11-digit ID, `99999999999`; a booking that is known to be gone is more reliable than guessing an ID that doesn't exist.)
Expected (assumed): 404 Not Found
Actual: **405 Method Not Allowed** ("Method Not Allowed" body) — unlike GET (see GET Test 3), a non-existent ID on PUT is not treated as "not found"; it's rejected before the ID is even looked up.

**Test 4: PUT request with a missing required field**
(Created a valid booking, then sent a full update payload with each field omitted in turn — `firstname`, `lastname`, `depositpaid`, `totalprice`, `bookingdates`, and `additionalneeds` — valid auth token included each time.)
Expected (assumed): 400 Bad Request for any omitted field
Actual:
- Omitting `firstname`, `lastname`, `depositpaid`, `totalprice`, or `bookingdates` → **400 Bad Request** ("Bad Request" body) ✅ — but note this is **inconsistent with POST's** handling of the same condition, which returns 500 (see POST Test 3 and bug #1); PUT validates a missing required field before hitting the server error POST triggers.
- Omitting `additionalneeds` → **200** — consistent with PUT Test 1/POST Test 3: `additionalneeds` is optional, not required (see bug #3).
  - 🐛 **Bug:** the response still contains the booking's old value (`"additionalneeds": "Breakfast"`). PUT is supposed to replace the whole booking, so an omitted optional field should be cleared, not kept (see bug #17). Found by a direct request on 2026-10-17; not asserted by an automated test yet.
- ✅ **Test status: REFACTORED (2026-10-17).** `test_missing_required_field` used to loop over the fields with six near-identical `if key == ...` blocks, so the first failing field stopped the test and hid the rest. It is now parametrized like the POST version: each omitted field runs as its own case (`[firstname-400]` … `[additionalneeds-200]`). Every case asserts the status code, and the `400` cases also assert the `"Bad Request"` body. The body check is chosen from the expected status, not the actual response, so an unexpected `400` for `additionalneeds` fails the test instead of passing.

**Test 5: PUT request with an extremely long string in a field**
(Created a valid booking, then sent a full update payload with each field in turn replaced by a 1,100-char string (`"Andres12324" * 100`), valid auth token included — including `totalprice` and `depositpaid`, which are normally numeric/boolean.)
Expected (assumed): 400 Bad Request, per API documentation
Actual: **200** for every field, including `totalprice`/`depositpaid` set to a long string — consistent with POST's long-string handling (see POST Test 5) and, for the type mismatch on `totalprice`/`depositpaid`, notably *not* the 500 seen in PUT Test 2's wrong-data-type test; a single mistyped field alongside otherwise-valid data doesn't trigger the same server error as changing every field's type at once.
- `firstname`, `lastname`, `additionalneeds` → stored and returned as sent, with no truncation.
- `totalprice` set to a long string → the stored `totalprice` comes back as **`null`** — 🐛 **Bug:** silently corrupted, the same as the empty-string case (see Test 6 and bug #4).
- `depositpaid` set to a long string → the stored `depositpaid` comes back as **`true`** — 🐛 **Bug:** the non-empty string is coerced to boolean `true`, the opposite of the empty-string case, which becomes `false` (see Test 6). The fixture already stores `depositpaid: true`, so the automated test alone can't tell this conversion apart from the API keeping the old value. A direct request on 2026-10-19 stored `false` first and still got `true` back, which confirms the conversion.
- `bookingdates` (both nested dates set to a long string) → both dates come back corrupted to **`"0NaN-aN-aN"`** — the same coercion as bug #6 (invalid calendar dates), not a distinct behavior.
- ✅ **Test status: REFACTORED (2026-10-19).** `test_extremely_long_string_field` used to loop over the fields, so the first failing field stopped the test and hid the rest, and it only asserted the stored value for `bookingdates`. It is now parametrized like Test 6: each field runs as its own case, and each row holds its expected status and stored value. The `totalprice`, `depositpaid` and `bookingdates` rows have `# Known API bug` comments. The long string is defined once as `LONG_STRING` at the top of the module, and it is now 1,100 characters instead of 91.

**Test 6: PUT request with empty-string field(s)**
(Created a valid booking, then sent a full update payload with each field in turn replaced by `""`, valid auth token included.)
Expected (assumed): 400 Bad Request for any field
Actual:
- `firstname`, `lastname`, `additionalneeds` → **200**, empty string accepted and stored as sent ✅ — consistent with POST's empty-string handling (see POST Test 4 and bug #4).
- `totalprice` set to `""` → **200**, but the returned/stored `totalprice` comes back as **`null`** — 🐛 **Bug:** silently corrupted rather than stored as `""` or rejected, consistent with POST Test 4's `totalprice: ""` → `None` corruption (bug #4).
- `depositpaid` set to `""` → **200**, but the returned/stored `depositpaid` comes back as **`false`** — 🐛 **Bug:** an empty string is silently coerced to boolean `false` instead of being stored as sent or rejected.
- `bookingdates` set to `""` (replacing the whole nested object with a string) → **400 Bad Request** ("Bad Request" body) — the only field actually rejected, since `bookingdates` must be an object, not a scalar.

The automated version of this test (`test_empty_string_field`) no longer uses `xfail`: it asserts the two known-bug values directly (`totalprice` → `None`, `depositpaid` → `False`), so both corruptions are confirmed by the automated assertions, not a manual/ad-hoc script. The extraneous top-level `checkin`/`checkout` assignment (dead code left over from the original copy/paste bug) has been removed; this test still only covers replacing the whole `bookingdates` object with `""`, which correctly gets 400 — the nested-field case is now covered separately by Test 7 below.
- ✅ **Test status: REFACTORED (2026-10-18).** `test_empty_string_field` used to loop over the fields and look up the bug values in a `known_bugs` map, so the first failing field stopped the test and hid the rest. It is now parametrized like Test 4: each field runs as its own case (`[firstname-200-]` … `[additionalneeds-200-]`), and each row holds its expected status and stored value. The `totalprice` and `depositpaid` rows have `# Known API bug` comments in place of the map. Every `200` case compares the stored value from the response with the row's expected value, and the `400` case (`bookingdates`) asserts the `"Bad Request"` body.

**Test 7: PUT request with nested `bookingdates.checkin`/`checkout` set to an empty string**
(Created a valid booking, then sent a full update payload with `bookingdates.checkin` set to `""` — leaving `checkout` valid — then repeated with `bookingdates.checkout` set to `""` — leaving `checkin` valid, valid auth token included both times.)
Expected (assumed): 400 Bad Request
Actual: **200** for both cases, and the empty-string date value comes back corrupted to **`"0NaN-aN-aN"`** — the same coercion as bug #6, not a distinct behavior; unlike replacing the whole `bookingdates` object (which is correctly rejected with 400, see Test 6), an empty string for just one nested date field is silently accepted and corrupted. Confirmed by `test_empty_string_nested_bookingdates_field`.

**Test 8: PUT request with no `Cookie`/auth token**
(Created a valid booking, then sent a full update payload to it with no `Cookie` header at all.)
Expected: 403 Forbidden, per API docs.
Actual: **403 Forbidden** ✅ — matches documented behavior, consistent with DELETE's handling of the same condition (see DELETE Test 6).

**Test 9: PUT request with an invalid/expired auth token**
(Created a valid booking, then sent a full update payload to it with a well-formed but bogus `Cookie: token=invalidtoken123` instead of a real token.)
Expected: 403 Forbidden, per API docs.
Actual: **403 Forbidden** ✅ — matches documented behavior, consistent with DELETE's handling of the same condition (see DELETE Test 5).

---

PUT method test cases are complete — all planned cases (happy path, wrong data type, non-existent ID, missing required field, long strings incl. nested `bookingdates`, empty strings incl. nested `bookingdates`, no auth token, invalid auth token) are automated in `test_booking_put.py` and pass.

---

## Summary of bugs / API behavior discovered

1. **Invalid input triggers 500s, not 400s — for mistyped fields.** A malformed field type (wrong data type) results in a raw `500 Internal Server Error` rather than a client-facing `400 Bad Request`, on both POST and PUT. A *missing* required field behaves inconsistently across methods — see bug #9.
2. **Non-standard/invalid IDs on GET return 404, not 400.** Malformed IDs, whitespace IDs, and oversized IDs are all treated the same as "not found" — there is no separate bad-request path for unparseable IDs.
3. **`additionalneeds` is optional**, not required — omitting it returns 200, unlike every other field.
4. **Empty strings and malformed data are silently accepted (200)** instead of rejected, and in the case of `totalprice` sent as an empty string or a boolean, the value is **corrupted to `None`** rather than validated or rejected. This is a data-integrity bug, not just a missing-validation issue. Confirmed via both the empty-string test (`totalprice: ""`, see POST Test 4, which also confirms `depositpaid: ""` → `false` and empty dates → `"0NaN-aN-aN"` on POST) and the wrong-data-type test (`totalprice: True`/`False`, see POST Test 2) — `totalprice` is corrupted to `None` for either boolean value, unlike `firstname`/`lastname`'s `True`-vs-`False` split (bug #14).
5. **No length limit on string fields.** Fields up to 360 characters (`firstname`, `lastname`, `additionalneeds`) are accepted and returned as-is with a 200 — no server-side length validation.
6. **Invalid calendar dates are silently coerced, not rejected.** An out-of-range date like `checkin: "2099-13-01"` (month 13) or `checkout: "1999-01-32"` (day 32) returns 200, and both values come back corrupted to `"0NaN-aN-aN"` rather than the request being rejected — consistent with bug #4.
7. ~~**Still untested:** the valid-range half of Test 6 (checkout genuinely after checkin) has not been automated yet.~~ **Resolved:** the valid-range half of Test 6 is now automated in `test_equivalence_partitioning_valid_dates` (see Test 6b) — the API correctly returns the dates as sent for a well-formed, chronologically-ordered pair.
8. **PUT against a non-existent ID returns 405, not 404.** Unlike GET, which treats any unresolvable ID as "not found" (see bug #2), PUT against a well-formed but non-existent ID returns `405 Method Not Allowed` — inconsistent handling of the same underlying condition (no matching record) across methods.
9. **Missing required field is handled differently by POST vs. PUT.** POST returns `500 Internal Server Error` when a required field is omitted (bug #1), but PUT returns `400 Bad Request` for the identical condition — the two methods validate the same requirement at different points in the request lifecycle.
10. **No length limit on PUT string fields either**, matching bug #5 on POST — long strings (1,100 chars tested) in any field, including a numeric/boolean field replaced with a string, return 200 with no length or type validation, and don't trigger the 500 seen when every field is mistyped at once (see PUT Test 2). The string fields are stored as sent, but a long string in `totalprice` is corrupted to `null` and a long string in `depositpaid` is coerced to `true`. A long string in the nested `bookingdates.checkin`/`checkout` fields is also accepted with 200, but corrupted to `"0NaN-aN-aN"` rather than stored as sent — consistent with bug #6 (see PUT Test 5).
11. **DELETE against a non-existent ID also returns 405, not 404**, matching PUT's behavior (bug #8) rather than GET's (bug #2) — the same "record not found" condition is handled inconsistently depending on the HTTP method used, now confirmed across three methods (GET: 404, PUT: 405, DELETE: 405).
12. **DELETE doesn't distinguish a malformed ID from a not-found one.** A malformed (alphanumeric) ID on DELETE returns the same `405 Method Not Allowed` as a well-formed but non-existent ID (bug #11), unlike GET, which returns `404 Not Found` for both malformed and non-existent IDs alike (bug #2) — DELETE and GET are each internally consistent, but disagree with each other on the status code for the same class of condition.
13. **PUT accepts empty strings for `firstname`/`lastname`/`additionalneeds`, but corrupts `totalprice` and `depositpaid`.** Sending `""` for `totalprice` returns 200 but the stored value comes back as `null` (matching bug #4's POST-side corruption), and sending `""` for `depositpaid` returns 200 but the stored value comes back coerced to boolean `false` — neither is rejected nor stored as sent. Both are now confirmed by automated assertions in `test_empty_string_field` (no longer `xfail`). Replacing the whole `bookingdates` object with `""` is correctly rejected with 400, but an empty string for just a nested `bookingdates.checkin`/`checkout` field is accepted with 200 and corrupted to `"0NaN-aN-aN"`, consistent with bug #6 (see PUT Test 7, confirmed by `test_empty_string_nested_bookingdates_field`).
14. **POST treats the wrong-type boolean `False` differently from `True` on string fields.** Sending `firstname`/`lastname: True` returns 500 (consistent with bug #1), but sending `False` for the same field is silently accepted with 200 and stored as the literal `false` — the falsy value slips past whatever check produces the 500 for other wrong types. Confirmed by `test_wrong_data_type`, which asserts both halves of the split, including the stored `false` (see POST Test 2). Re-confirmed on 2026-09-30 by sending the requests directly. Possible cause (not yet tested): the server may only validate a field when its value is truthy. Sending other falsy values for `firstname`, such as `0`, `""` or `null`, would confirm or rule this out. PUT has the same split: `True` → 500, `False` → 200 stored as `false` (confirmed by `test_put_wrong_data`, see PUT Test 2).
15. **`additionalneeds` has no type validation.** On POST, a number or boolean `additionalneeds` is accepted with 200 and stored with its wrong type (`0`, `12345`, `-12345`, `true`, `false`, `3.14`) — no rejection and no conversion to a string, unlike the other string fields `firstname`/`lastname`, which return 500 for the same inputs (bug #1, bug #14). Confirmed by `test_wrong_data_type` (see POST Test 2). PUT behaves the same: `0`, `True`, `False` and `8.9999` are all stored as sent (confirmed by `test_put_wrong_data`, see PUT Test 2).
16. **Numeric strings in `bookingdates` are parsed as years and silently truncated.** On POST, a numeric string such as `"193735"` for `checkin`/`checkout` is accepted with 200 and stored as `"3735-01-01"` — the API treats it as year 193735 and keeps only the last four digits. Values above `275760` (the JavaScript `Date` year limit) fall back to `"0NaN-aN-aN"` (bug #6). The truncated result looks like a valid date, which makes this worse than the `NaN` case: the corruption is hard to spot. Found when `test_wrong_data_type` failed intermittently (see POST Test 2). Re-confirmed on 2026-09-28 by sending the requests directly: still present. Not covered by an automated test since the 2026-10-26 refactor of `test_wrong_data_type`; a separate boundary-value test is planned (see POST Test 2).
17. **PUT keeps an omitted optional field's old value.** Sending a PUT without `additionalneeds` returns 200, and the booking keeps its previous `additionalneeds` (e.g. `"Breakfast"`) instead of clearing it. PUT should replace the whole resource, so here it behaves more like a partial update (PATCH). Found by a direct request on 2026-10-17 (see PUT Test 4); not yet covered by an automated assertion.
18. **POST and PUT handle a number in `firstname`/`lastname` differently.** POST returns `500 Internal Server Error` for a number in these fields (bug #1), but PUT accepts `0` with 200 and stores it as the number `0` — no rejection and no conversion to a string. This is the same kind of POST-vs-PUT split as bug #9. Confirmed by `test_put_wrong_data` (see PUT Test 2) and re-confirmed on 2026-10-24 by sending the requests directly. Booleans don't split the same way: PUT matches POST's `True` → 500 / `False` → 200 behavior (bug #14).
19. **`depositpaid: "False"` is stored as `true`.** On PUT, the string `"False"` is accepted with 200 and coerced to `true`, because any non-empty string counts as truthy. The value means the opposite of what the client sent, so a booking can be marked as paid when it isn't. `"True"` and non-zero numbers are coerced the same way, but there the result matches what was meant. Confirmed by `test_put_wrong_data` (see PUT Test 2) and re-confirmed on 2026-10-25 by sending the request directly. POST has the same bug: confirmed by `test_wrong_data_type` (see POST Test 2) and re-confirmed on 2026-10-26 by sending the request directly.
20. **POST and PUT handle a wrong type for the whole `bookingdates` object differently.** POST returns `500 Internal Server Error` when `bookingdates` is replaced by a boolean, number, string or float (`True`, `False`, `0`, `12345`, `-12345`, `"Andres"`, `3.14`), but PUT correctly rejects the same kinds of values (`0`, `False`, `"One"`) with `400 Bad Request`. The same kind of POST-vs-PUT split as bug #9. Confirmed by `test_wrong_data_type` (see POST Test 2) and `test_put_wrong_data` (see PUT Test 2), and re-confirmed on 2026-10-26 by sending the POST requests directly.
21. **POST accepts a negative `totalprice`.** Sending `totalprice: -1000` returns 200 and stores `-1000`. The type is correct, but a booking can't have a negative price, so the value should be rejected. Confirmed by `test_wrong_data_type` (see POST Test 2) and re-confirmed on 2026-10-26 by sending the request directly. Not yet tested on PUT.

---

# Test Cases — DELETE Method

**Test 1: DELETE request (happy path)**
Creates a booking, authenticates, deletes the booking, then confirms with a follow-up GET that the record is actually gone.
Expected: 201 on delete, 404 on the follow-up GET.
Actual: 201 ✅ ("Created" body) on delete, 404 ✅ ("Not Found" body) on the follow-up GET — the booking is genuinely removed, not just marked deleted.

**Test 2: DELETE request against a non-existent booking ID**
(Tested with the `non_existent_booking_id` fixture from `conftest.py`: the highest existing booking ID + 1000, valid auth token included. Originally tested with a hard-coded ID, `9999`, which could exist on the shared public API.)
Expected (assumed): 404 Not Found
Actual: **405 Method Not Allowed** ("Method Not Allowed" body) — consistent with PUT's handling of the same condition (see PUT Test 3 and bug #8); DELETE against a well-formed but non-existent ID is rejected the same way PUT is, not treated as "not found" the way GET is.

**Test 3: DELETE request against an already-deleted booking ID (double delete)**
(Created a valid booking, then sent the same DELETE request twice with a valid auth token.)
Expected (assumed): 404 Not Found on the second delete
Actual: **201** ✅ ("Created" body) on the first delete, then **405 Method Not Allowed** ("Method Not Allowed" body) on the second — matches Test 2's non-existent-ID behavior, since the ID no longer resolves to a record after the first delete.
- ⚠️ **Intermittent failure (2026-09-29):** in 1 of 10 runs, `test_already_deleted_booking_ID` failed on the body assertion. The second delete returned **405**, but the body was not `"Method Not Allowed"`. The other 9 runs passed. The failure output didn't include the actual body, so it wasn't captured. This is most likely an unstable response from the public API rather than a change in behavior. To confirm, add the actual body to the assertion message next time it fails.

**Test 4: DELETE request with a malformed ID (alphanumeric, e.g. "olXYD841")**
(Valid auth token included.)
Expected (assumed): 400 Bad Request
Actual: **405 Method Not Allowed** ("Method Not Allowed" body) — same handling as a well-formed but non-existent ID (see Test 2 and bug #8); DELETE doesn't distinguish a malformed ID from a not-found one, unlike GET (see GET Test 2), which returns 404 for both.

**Test 5: DELETE request with an invalid/expired auth token**
(Created a valid booking, then sent the DELETE with a well-formed but bogus `Cookie: token=invalidtoken123` instead of a real token.)
Expected: 403 Forbidden, per API docs.
Actual: **403 Forbidden** ✅ — matches documented behavior.

**Test 6: DELETE request with no `Cookie`/auth token**
(Created a valid booking, then sent the DELETE with no `Cookie` header at all.)
Expected: 403 Forbidden, per API docs.
Actual: **403 Forbidden** ✅ — matches documented behavior.

---

DELETE method test cases are now complete — all planned cases (happy path, non-existent ID, double delete, malformed ID, invalid token, missing token) are automated in `test_booking_delete.py` and pass.

---

# Full Test Suite Run — 2026-09-29

All four test files now take the shared `base_url` fixture from `conftest.py` instead of a per-class `base_url` attribute.

| File | Tests | Result |
|---|---|---|
| `test_booking_get.py` | 5 | 5 passed ✅ |
| `test_booking_post.py` | 7 | 7 passed ✅ |
| `test_booking_put.py` | 9 | 9 passed ✅ |
| `test_booking_delete.py` | 6 | 6 passed on re-run; `test_already_deleted_booking_ID` failed once ⚠️ |
| **Total** | **27** | **26 passed, 1 failed on first run; 27/27 on re-run** |

- Every result matches the Actual values documented above. No API behavior has changed since the last run.
- `test_wrong_data_type` (POST) is no longer flaky: both date partitions are now asserted (see POST Test 2).
- `test_already_deleted_booking_ID` (DELETE) is intermittent: 1 failure in 10 runs, on the response body only (see DELETE Test 3).

---

# Full Test Suite Run — 2026-10-17

Changes since the last run:
- POST and PUT `test_missing_required_field` are parametrized, so each omitted field is reported as its own test. That is why the count is higher than before: no test cases were added or removed.
- The f-strings in the GET, PUT and DELETE tests use single quotes inside (`existing_booking_id['id']`). Nested double quotes in f-strings are a syntax error before Python 3.12.

| File | Tests | Result |
|---|---|---|
| `test_booking_get.py` | 5 | 5 passed ✅ |
| `test_booking_post.py` | 12 | 12 passed ✅ |
| `test_booking_put.py` | 14 | 14 passed ✅ |
| `test_booking_delete.py` | 6 | 6 passed ✅ |
| **Total** | **37** | **37 passed ✅** |

- Every result matches the Actual values documented above.
- On 2026-10-16, the old (loop) PUT `test_missing_required_field` failed once in a full run and passed on re-run. It made 6 requests in a row to the public API, so this was most likely a slow or unstable response, not a change in behavior.

---

# Full Test Suite Run — 2026-10-18

Changes since the last run:
- PUT `test_empty_string_field` is parametrized, so each field is reported as its own test (see PUT Test 6). That is why the count is higher than before: no test cases were added or removed.

| File | Tests | Result |
|---|---|---|
| `test_booking_get.py` | 5 | 5 passed ✅ |
| `test_booking_post.py` | 12 | 12 passed ✅ |
| `test_booking_put.py` | 19 | 19 passed ✅ |
| `test_booking_delete.py` | 6 | 6 passed ✅ |
| **Total** | **42** | **42 passed ✅** |

- Every result matches the Actual values documented above.

---

# Full Test Suite Run — 2026-10-19

Changes since the last run:
- PUT `test_extremely_long_string_field` is parametrized, so each field is reported as its own test (see PUT Test 5). That is why the count is higher than before: no test cases were added or removed.

| File | Tests | Result |
|---|---|---|
| `test_booking_get.py` | 5 | 5 passed ✅ |
| `test_booking_post.py` | 12 | 12 passed ✅ |
| `test_booking_put.py` | 24 | 24 passed ✅ |
| `test_booking_delete.py` | 6 | 6 passed ✅ |
| **Total** | **47** | **47 passed ✅** |

- Every result matches the Actual values documented above.

---

# Full Test Suite Run — 2026-10-20

No test changes since the last run. This run was used to generate the HTML report (`report.html`) and the [test summary report](../test-summary-report.md).

| File | Tests | Result |
|---|---|---|
| `test_booking_get.py` | 5 | 5 passed ✅ |
| `test_booking_post.py` | 12 | 12 passed ✅ |
| `test_booking_put.py` | 24 | 24 passed ✅ |
| `test_booking_delete.py` | 6 | 6 passed ✅ |
| **Total** | **47** | **47 passed ✅** |

- Every result matches the Actual values documented above.

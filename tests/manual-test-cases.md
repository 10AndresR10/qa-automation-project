# Manual Test Cases

Test cases written before each test was automated, with the expected and actual results.
Bug numbers ("see bug #4") refer to [`known-bugs.md`](../known-bugs.md). Full suite runs and
test data cleanup notes are in [`test-run-log.md`](test-run-log.md).

---

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
(Sent a valid payload with one field in turn replaced by a wrong type: `firstname`/`lastname` as `12345`, `True`, `False`, `3.14` and `0`; `totalprice` as `"One"`, `"12345"`, `True`, `False` and `-1000`; `depositpaid` as `"True"`, `"False"`, `"Andres"`, `123456`, `3.1233`, `0` and `-99`; the whole `bookingdates` object as `True`, `False`, `0`, `12345`, `-12345`, `"Andres"` and `3.14`; and `additionalneeds` as `0`, `12345`, `-12345`, `True`, `False` and `3.14`.)
Expected (assumed): 400 Bad Request for any field
Actual:
- `firstname`/`lastname` set to `12345`, `True` or `3.14` → **500 Internal Server Error** ("Internal Server Error" body) — 🐛 **Bug:** the server crashes instead of returning 400 (see bug #1).
- `firstname`/`lastname` set to `False` → **200**, stored as the boolean `false` — 🐛 **Bug:** the falsy value isn't rejected like `True` is (see bug #14).
- `firstname`/`lastname` set to `0` → **200**, stored as the number `0` — 🐛 **Bug:** the falsy value isn't rejected and is stored as sent, the same as PUT (see bugs #14 and #18).
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
- ~~⚠️ **Coverage gap (2026-10-26):** the old loop also sent 6-digit numeric strings (`275759`, `275760`, `275761`) to the nested `bookingdates.checkin`/`checkout` fields (see bug #16). The refactor removed these cases, because the table only replaces whole top-level fields. They are planned as their own parametrized boundary-value test; until then, bug #16 isn't covered by an automated test.~~ **Resolved (2026-10-28):** these cases are back in their own boundary-value test (see Test 2b).
- ✅ **Test status: EXTENDED (2026-11-03).** Added `0` for `firstname`/`lastname` — 35 cases in total, all passing. Re-confirmed the same day by sending the requests directly: the raw JSON stores the number `0`, not `false`. This shows bug #18 is not a POST-vs-PUT split.
- ✅ **Test status: UPDATED (2026-11-08).** Each `200` case now deletes the booking it created, with `delete_booking` from `tests/helpers.py` (moved there from `conftest.py` so tests can call it). The delete runs before the stored-value assert, so the booking is removed even when the assert fails. The `500` cases create no booking, so they have nothing to delete. The test now takes its base payload from the `existing_booking_id` fixture, so each case also creates and deletes one booking it doesn't use. All 35 cases pass.

**Test 2b: POST request with a wrong data type in a nested `bookingdates` date**
(Sent a valid payload with `bookingdates.checkin` replaced by a wrong value — leaving `checkout` valid — then repeated for `checkout`. Each date was set to the numbers `275759`, `275760` and `275761`; the numeric strings `"275759"`, `"275760"` and `"275761"`; the word `"Tomorrow"`; `True` and `False`; `None` (JSON `null`); the negative-year string `"-2026-01-21"`; an empty list `[]`; and the float `3.14`. `275760` is the largest year a JavaScript `Date` can hold.)
Expected (assumed): 400 Bad Request
Actual: **200** for every case except `None`, and the date is never stored as sent:
- The numbers `275759`, `275760` and `275761` → stored as **`"1970-01-01"`** — 🐛 **Bug:** a number is read as milliseconds since 1970-01-01, not as a year, so all three values mean about 4.6 minutes after midnight on 1970-01-01. Any small number gives the same date (see bug #22).
- The float `3.14` → stored as **`"1970-01-01"`** — 🐛 **Bug:** read as milliseconds, the same as the whole numbers (see bug #22).
- `True` and `False` → stored as **`"1970-01-01"`** — 🐛 **Bug:** the booleans are converted to the numbers `1` and `0` and then read as milliseconds (see bug #22). This is **inconsistent with POST Test 2**, where replacing the whole `bookingdates` object with `True` or `False` crashes the server with 500 (bug #20).
- The strings `"275759"` and `"275760"` → stored as **`"5759-01-01"`** and **`"5760-01-01"`** — 🐛 **Bug:** the string is read as a year and only its last four digits are kept (see bug #16). `275760` is still inside the `Date` limit, so it is truncated, not rejected.
- The string `"275761"` → stored as **`"0NaN-aN-aN"`** — 🐛 **Bug:** one year past the limit gives an Invalid Date, the same corruption as bug #6.
- The string `"Tomorrow"` and the empty list `[]` → stored as **`"0NaN-aN-aN"`** — 🐛 **Bug:** neither can be read as a date, so both become an Invalid Date (see bug #6).
- The string `"-2026-01-21"` → stored as **`"2026-01-21"`** — 🐛 **Bug:** year -2026 is a valid `Date` year, but the minus sign is dropped and the date is stored as year 2026. The result looks like a normal date, so the corruption is hard to spot (see bug #23).
- `None` → **500 Internal Server Error** ("Internal Server Error" body) — 🐛 **Bug:** a `null` date crashes the server instead of returning 400 (see bug #24).
- The results are the same for `checkin` and `checkout`.
- ✅ **Test status: AUTOMATED (2026-10-28).** `test_wrong_data_type_nested_dict` is parametrized over the date field (`checkin`/`checkout`) and the values above. Each row holds the wrong value, the expected status and the expected stored date, and has its own `# Known API bug` comment. Both asserts have failure messages that name the date field.
- ✅ **Test status: EXTENDED (2026-10-28).** Added the `"Tomorrow"`, `True`, `False`, `None`, `"-2026-01-21"`, `[]` and `3.14` cases — 13 values and 26 cases in total, all passing. The test has a new `500` branch that asserts the `"Internal Server Error"` body, like `test_wrong_data_type`.
- ✅ **Test status: UPDATED (2026-11-09).** Each `200` case now deletes the booking it created, before the stored-date assert, the same as Test 2. The test now takes its base payload from the `existing_booking_id` fixture instead of its own dict. It copies both the payload and the nested `bookingdates` dict before changing a date. A plain `.copy()` only copies the outer dict, so without the second copy the wrong value would also change the fixture's payload. All 26 cases pass. Using the fixture means each case also creates and deletes one booking it doesn't use.
- Not covered yet: the number boundary of `Date` (`8.64e15` milliseconds, the latest date it can hold, and `8.64e15 + 1`, which should give an Invalid Date).

**Test 3: POST request with a missing required field**
Expected (assumed): 400 Bad Request for any omitted field
Actual:
- Omitting `firstname`, `lastname`, `totalprice`, `depositpaid`, or `bookingdates` → **500 Internal Server Error**
- Omitting `additionalneeds` → **200** (field is optional, not required — original assumption was wrong to treat it as required)
- ✅ **Test status: UPDATED (2026-11-09).** The `additionalneeds` case now deletes the booking it created, then asserts that `additionalneeds` is not in the stored booking (`body["booking"]`). Before this, the test only checked the status code for this case. A direct request the same day showed the API leaves the key out of the response when it isn't sent. The failure path was checked by temporarily keeping `additionalneeds` in the payload: the test failed with `additionalneeds was not sent, but the API stored additionalneeds='Breakfast'`, and the booking was still deleted, because the delete runs before the assert. The `500` cases create no booking. All 6 cases pass.

**Test 4: POST request with empty string field(s)**
(Every field set to `""` in a single request: `firstname`, `lastname`, `totalprice`, `depositpaid`, `bookingdates.checkin`, `bookingdates.checkout`, `additionalneeds`.)
Expected (assumed): 400 Bad Request
Actual: **200** — the API accepts empty strings with no validation, and silently corrupts the non-string fields instead of rejecting them:
- `firstname`, `lastname`, `additionalneeds` → stored as `""`, as sent.
- 🐛 **Bug:** `totalprice: ""` comes back as **`None`** — the value is silently dropped/corrupted rather than the request being rejected (bug #4).
- 🐛 **Bug:** `depositpaid: ""` comes back coerced to boolean **`false`** instead of being stored as sent or rejected — the same corruption as PUT Test 6 (bug #13).
- 🐛 **Bug:** `checkin: ""` and `checkout: ""` both come back corrupted to **`"0NaN-aN-aN"`** — the same coercion as bug #6, and the same result PUT gives for an empty nested date (PUT Test 7).
- ✅ **Test status: FIXED (2026-10-12).** `test_empty_string_field` used to send `totalprice`/`depositpaid` as `False` and both dates as `"0NaN-aN-aN"`, so only 3 of the 7 fields were actually empty strings, and `depositpaid` was never asserted. Every field is now `""`, and all seven stored values are asserted. The old payload also showed that the API accepts the string `"0NaN-aN-aN"` verbatim as a date; that behavior is no longer covered by an automated test.
- ✅ **Test status: UPDATED (2026-11-09).** The test now deletes its booking right after reading the response, before the seven stored-value asserts. Every assert now has a failure message that names the field (`totalprice: expected None, got 0`), and the status-code assert has one too. The test passes.

**Test 5: POST request with an extremely long string in a field (e.g. "firstname")**
(Tested with `firstname` at 288 chars, `lastname` at 299 chars, `additionalneeds` at 360 chars.)
Expected (assumed): 400 Bad Request, per API documentation
Actual: **200** — all three long strings are accepted and echoed back unmodified (no truncation, no length validation).
- ✅ **Test status: REFACTORED (2026-11-10).** `test_extremely_long_string` used to send all three long strings in one request. It is now parametrized like PUT Test 5: each field gets its long string in turn, while the other fields keep normal values — `firstname` at 600 characters (`"Andres" * 100`), `lastname` at 500 (`"Reyes" * 100`) and `additionalneeds` at 900 (`"Breakfast" * 100`). That is 3 cases, all passing, and the strings are longer than before. Each case deletes its booking before the stored-value assert. The failure messages show the string length and the first 30 characters of what was stored, so a long value doesn't fill the output.

**Test 6: POST request — equivalence partitioning on checkin/checkout dates**
(Tested with an out-of-range invalid pair: `checkin: "2099-13-01"` (month 13), `checkout: "1999-01-32"` (day 32).)
Expected (assumed): valid → 200, invalid → 400
Actual: **200** — both invalid dates are silently coerced to `"0NaN-aN-aN"` instead of being rejected.
- ✅ **Test status: REFACTORED AND EXTENDED (2026-11-11).** `test_equivalence_partitioning_checkvariables` is now parametrized like Test 2b: the date field (`checkin`/`checkout`) and the invalid value are separate decorators, so only one date is invalid in each case. The other date keeps a valid base value (`checkin: "2099-12-01"`, `checkout: "2999-01-31"`). The values are `"2099-13-01"` (month 13), `"2026-12-32"` (day 32) and the new `"2026-02-29"` (29 February in a non-leap year) — 6 cases in total, all passing. Each case deletes its booking before the stored-date assert, every row has a `# Known API bug` comment, and both asserts have failure messages that name the date field and the value sent.
- `"2026-02-29"` → stored as **`"2026-03-01"`** — 🐛 **Bug:** the impossible date is not rejected, it rolls over into March (see bug #26). Re-confirmed on 2026-11-11 by sending the requests directly: `"2026-02-31"` → `"2026-03-03"`, the same for `checkout`, while the real leap day `"2028-02-29"` is stored as sent.
- Note: in the `checkout` cases the invalid value is before the base `checkin` (`2099-12-01`), so those requests are also out of order. This doesn't change the results today.

**Test 6b: POST request — equivalence partitioning, valid-range counterpart**
(Tested with a well-formed pair where `checkout` genuinely comes after `checkin`: `checkin: "2026-12-01"`, `checkout: "2026-12-10"`.)
Expected: 200, both dates returned as sent.
Actual: **200** ✅ — both dates are returned unmodified, as expected. Confirmed by `test_equivalence_partitioning_valid_dates`. This completes the equivalence-partitioning pair for Test 6 (see bug #7, now resolved).
- ✅ **Test status: REFACTORED AND EXTENDED (2026-11-11).** `test_equivalence_partitioning_valid_dates` is now parametrized like Test 6: the date field (`checkin`/`checkout`) and the valid value are separate decorators. The values are `"2026-11-10"`, `"2026-11-11"` and the leap day `"2028-02-29"` — 6 cases in total, all passing, and each date is stored as sent. The leap day is the valid counterpart of Test 6's `"2026-02-29"`: the same day and month, valid in a leap year and rolled over in a non-leap year (bug #26). The base booking is `checkin: "2026-01-01"`, `checkout: "2029-01-01"`, so every test value falls between them and each case is a valid booking whichever field it replaces. Each case deletes its booking before the stored-date assert, and both asserts have failure messages that name the date field and the value sent.

---

**POST test run — 2026-09-29:** all 7 tests in `test_booking_post.py` pass. `test_wrong_data_type` is no longer flaky (see Test 2). See the full-suite results at the end of this file.

**POST test run — 2026-09-30:** all 7 tests in `test_booking_post.py` pass after tightening the truncated-year assertion (see Test 2). `test_wrong_data_type` was then run 12 more times in a row: 12/12 passed. The date values are random, so a direct check was also made to confirm the API behavior hasn't changed: `"193735"` → `"3735-01-01"`, `"123456"` → `"3456-01-01"`, `"543219"` → `"0NaN-aN-aN"` (bug #16 still present).
Later the same day, the `firstname`/`lastname` boolean checks in `test_wrong_data_type` were rewritten to assert bug #14 directly (see Test 2). All 7 tests in `test_booking_post.py` pass.

**POST test run — 2026-10-26:** all 44 tests in `test_booking_post.py` pass after parametrizing `test_wrong_data_type` (see Test 2). The count is higher than before because each wrong-data-type case is now reported as its own test (33 cases).

**POST test run — 2026-10-28:** all 56 tests in `test_booking_post.py` pass after adding `test_wrong_data_type_nested_dict` (see Test 2b, 12 cases).
Later the same day, `test_wrong_data_type_nested_dict` was extended to 26 cases (see Test 2b). All 70 tests in `test_booking_post.py` pass.

---

# Test Cases — PUT Method

**Test 1: PUT request (happy path)**
Creates a booking, authenticates, then fully updates all fields of the existing booking with valid data.
Expected: 200, response body reflects all updated field values.
Actual: 200 ✅ — all fields (`firstname`, `lastname`, `totalprice`, `depositpaid`, `bookingdates.checkin`, `bookingdates.checkout`, `additionalneeds`) are returned updated as sent.
- ✅ **Test status: FIXED (2026-10-12).** `test_put_method` used to call `.json()` before checking the status code, so a non-200 response without a JSON body failed with a JSON decode error instead of the real problem. It now asserts the status first and shows the response body in the failure message. The update payload also used to keep `depositpaid`, `bookingdates` and `additionalneeds` the same as the original booking (`True`, `2026-01-01`/`2026-01-05`, `"Breakfast"`), so the test would still pass if the API ignored those fields. Every field now changes (`depositpaid: False`, `2026-02-01`/`2026-02-05`, `"Soccer"`), so the test shows that each field is actually updated.

**Test 2: PUT request with wrong data type per field**
(Created a valid booking, then sent a full update payload with one field in turn replaced by a wrong type, valid auth token included: `firstname`/`lastname` as `0`, `True`, `False` and `3.14`; `totalprice` as `"One"`, `True` and `False`, plus the numeric string `"12345"` and the negative number `-1000`; `depositpaid` as `0`, `"True"`, `"False"`, `888.0`, `"Andres"` and `-99`; the whole `bookingdates` object as `0`, `False`, `"One"`, `True` and `3.14`; and `additionalneeds` as `False`, `0`, `True`, `8.9999` and `-12345`.)
Expected (assumed): 400 Bad Request for any field
Actual:
- `firstname`/`lastname` set to `0` → **200**, stored as the number `0` — 🐛 **Bug:** the wrong type is accepted and stored as sent, the same as POST (see POST Test 2 and bug #18).
- `firstname`/`lastname` set to `True` → **500 Internal Server Error** ("Internal Server Error" body) — 🐛 **Bug:** the server crashes instead of returning 400, the same as POST (see bug #14).
- `firstname`/`lastname` set to `False` → **200**, stored as the boolean `false` — 🐛 **Bug:** the same `True`-vs-`False` split as POST (see bug #14).
- `firstname`/`lastname` set to `3.14` → **500 Internal Server Error** ("Internal Server Error" body) — 🐛 **Bug:** the server crashes instead of returning 400, like `True`. So PUT doesn't store every number: `0` and `False` (falsy) are stored, `True` and `3.14` (truthy) crash the server (see bugs #14 and #18).
- `totalprice` set to `"One"`, `True` or `False` → **200**, but the stored `totalprice` comes back as **`null`** — 🐛 **Bug:** the same silent corruption as bug #4. Like POST, `totalprice` doesn't distinguish `True` from `False`.
- `totalprice` set to `"12345"` → **200**, coerced to the number `12345` — the same numeric-string coercion as POST (`Number("12345")`), not a bug.
- `totalprice` set to `-1000` → **200**, stored as `-1000` — 🐛 **Bug:** the type is correct, but a negative price should be rejected. The same as POST (see bug #21).
- `depositpaid` set to `0` → **200**, coerced to `false` — the same numeric-truthiness coercion as POST (`bool(0)`), not a bug (see POST Test 2).
- `depositpaid` set to `"True"` → **200**, coerced to `true` — a non-empty string is truthy, the same truthy-string coercion as POST, not a bug.
- `depositpaid` set to `888.0` or `-99` → **200**, coerced to `true` — a non-zero number is truthy, not a bug.
- `depositpaid` set to `"Andres"` → **200**, coerced to `true` — a non-empty string is truthy, not a bug.
- `depositpaid` set to `"False"` → **200**, coerced to **`true`** — 🐛 **Bug:** the same truthy-string rule turns `"False"` into the opposite of what was sent (see bug #19).
- `bookingdates` set to `0`, `False`, `"One"`, `True` or `3.14` (replacing the whole nested object) → **400 Bad Request** ("Bad Request" body) ✅ — the only field actually rejected, the same as replacing it with `""` (see Test 6).
- `additionalneeds` set to `False`, `0`, `True`, `8.9999` or `-12345` → **200**, stored as sent (`false`, `0`, `true`, `8.9999`, `-12345`) — 🐛 **Bug:** no type validation, the same as POST (see bug #15). Unlike `firstname`/`lastname`, `True` doesn't cause a 500 here.
- Re-confirmed on 2026-10-24 by sending the requests directly: the raw JSON response stores `firstname`/`lastname` as the number `0` and `additionalneeds` as the boolean `false`. The automated asserts alone can't show this, because in Python `0 == False`.
- Re-confirmed on 2026-10-25 by sending the new cases directly: the raw JSON stores `firstname`/`lastname: False` as `false`, `depositpaid` as `true` for `"True"`, `"False"` and `888.0`, and `additionalneeds` as `0`, `true` and `8.9999`. The automated asserts can't tell these apart on their own either, because in Python `True == 1`.
- Originally this was one manual request with **every** field mistyped at once (`checkin` as an int, `checkout` as a whitespace string), which returned **500 Internal Server Error**. With one wrong field per request, only `True` in `firstname`/`lastname` returns 500.
- ✅ **Test status: REFACTORED (2026-10-24).** `test_put_wrong_data` is now parametrized like Test 4–6: each field runs as its own case, and each row holds the wrong value, the expected status and the expected stored value. The `400` case (`bookingdates`) asserts the `"Bad Request"` body instead of parsing JSON, and every `200` case compares the stored value with the row's expected value. The bug rows have `# Known API bug` comments.
- ✅ **Test status: EXTENDED (2026-10-25).** Added boolean cases for `firstname`/`lastname` and `totalprice`, string and float cases for `depositpaid`, boolean and string cases for `bookingdates`, and number, boolean and float cases for `additionalneeds` — 20 cases in total, all passing. The test has a new `500` branch that asserts the `"Internal Server Error"` body. Every row has its own comment: `# Known API bug` for bugs, and a short note for correct rejections and coercions that aren't bugs.
- ✅ **Test status: EXTENDED (2026-11-02).** Added the two `totalprice` values that POST Test 2 already covered: the numeric string `"12345"` (coerced to `12345`, not a bug) and the negative number `-1000` (stored as sent, bug #21) — 22 cases in total, all passing. Both rows have comments worded like the matching POST rows.
- ✅ **Test status: EXTENDED (2026-11-02).** Added more of the values POST Test 2 already covered: `3.14` for `firstname`/`lastname`, `"Andres"` and `-99` for `depositpaid`, `True` and `3.14` for `bookingdates`, and `-12345` for `additionalneeds` — 29 cases in total, all passing. Every row has a comment. The `3.14` result for `firstname`/`lastname` (500) narrows bug #18: PUT stores `0`, but not every number.
- ✅ **Test status: UPDATED (2026-11-04).** The status-code failure message now includes the response body and headers, and the `token` fixture prints the token, which pytest shows only for failing tests. This is to help diagnose the intermittent `403` (see section 4 of the [test summary report](../test-summary-report.md)). Checked with a fake token: the failure showed `403`, the `Forbidden` body, the headers and the printed token. The fake token has been removed, and all 29 cases pass.

**Test 2b: PUT request with a wrong data type in a nested `bookingdates` date**
(Created a valid booking, then sent a full update payload with `bookingdates.checkin` replaced by a wrong value — leaving `checkout` valid — then repeated for `checkout`, valid auth token included. Each date was set to the numbers `275759`, `275760` and `275761`, and to the numeric strings `"275759"`, `"275760"` and `"275761"`, the same values as POST Test 2b.)
Expected (assumed): 400 Bad Request
Actual: **200** for every case, and the date is never stored as sent — the same results as POST (see POST Test 2b):
- The numbers `275759`, `275760` and `275761` → stored as **`"1970-01-01"`** — 🐛 **Bug:** a number is read as milliseconds since 1970-01-01, not as a year (see bug #22).
- The strings `"275759"` and `"275760"` → stored as **`"5759-01-01"`** and **`"5760-01-01"`** — 🐛 **Bug:** the string is read as a year and only its last four digits are kept (see bug #16).
- The string `"275761"` → stored as **`"0NaN-aN-aN"`** — 🐛 **Bug:** one year past the `Date` limit gives an Invalid Date, the same corruption as bug #6.
- The results are the same for `checkin` and `checkout`. Re-confirmed on 2026-10-30 by sending the requests directly.
- Unlike replacing the whole `bookingdates` object with a wrong type, which PUT correctly rejects with 400 (see Test 2), a wrong value in just one nested date is accepted.
- ✅ **Test status: AUTOMATED (2026-10-30).** `test_put_wrong_data_nested_dict` is parametrized over the date field (`checkin`/`checkout`) and the six values — 12 cases in total, all passing. Each row holds the wrong value, the expected status and the expected stored date, and has its own `# Known API bug` comment. Both asserts have failure messages that name the date field.
- ✅ **Test status: EXTENDED (2026-10-31).** Added `True`, `False`, `"Tomorrow"`, the empty dict `{}`, `3.14`, `None` and the US-style date `"01/02/2026"` — 13 values and 26 cases in total, all passing. The test has a new `400` branch that asserts the `"Bad Request"` body instead of parsing JSON. Results:
  - `True`, `False` and `3.14` → stored as **`"1970-01-01"`** — 🐛 **Bug:** read as milliseconds since 1970-01-01, the same as POST (see bug #22).
  - `"Tomorrow"` and `{}` → stored as **`"0NaN-aN-aN"`** — 🐛 **Bug:** neither can be read as a date, so both become an Invalid Date (see bug #6).
  - `None` → **400 Bad Request** ("Bad Request" body) ✅ — correctly rejected. **Inconsistent with POST**, where a `null` date crashes the server with 500 (bug #24).
  - `"01/02/2026"` → stored as **`"2026-01-02"`** — 🐛 **Bug:** a date that isn't in `YYYY-MM-DD` format is accepted, and the ambiguous day/month order is silently read as month/day (see bug #25).
  - Every new row has its own comment: `# Known API bug` for bugs, and a short note for the correct `None` rejection.
  - The test now copies the payload and its nested `bookingdates` dict before changing a date. Before, it wrote the wrong value straight into the fixture's payload; a shallow `.copy()` alone wouldn't have fixed that, because the nested dict would still be shared.
- ✅ **Test status: EXTENDED (2026-10-31).** Added the last two values from POST Test 2b, the negative-year string `"-2026-01-21"` and the empty list `[]` — 15 values and 30 cases in total, all passing. Every wrong value from POST Test 2b is now covered on PUT. Results, both the same as POST:
  - `"-2026-01-21"` → stored as **`"2026-01-21"`** — 🐛 **Bug:** the minus sign is dropped and year -2026 is stored as 2026 (see bug #23).
  - `[]` → stored as **`"0NaN-aN-aN"`** — 🐛 **Bug:** it can't be read as a date, so it becomes an Invalid Date, the same as `{}` (see bug #6).
  - Both rows have their own `# Known API bug` comment.

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
  - 🐛 **Bug:** the response still contains the booking's old value (`"additionalneeds": "Breakfast"`). PUT is supposed to replace the whole booking, so an omitted optional field should be cleared, not kept (see bug #17). A follow-up GET also returns `"Breakfast"`, so the old value is really still stored. Found by a direct request on 2026-10-17; now asserted by `test_missing_required_field` (see the status notes below).
- ✅ **Test status: REFACTORED (2026-10-17).** `test_missing_required_field` used to loop over the fields with six near-identical `if key == ...` blocks, so the first failing field stopped the test and hid the rest. It is now parametrized like the POST version: each omitted field runs as its own case (`[firstname-400]` … `[additionalneeds-200]`). Every case asserts the status code, and the `400` cases also assert the `"Bad Request"` body. The body check is chosen from the expected status, not the actual response, so an unexpected `400` for `additionalneeds` fails the test instead of passing.
- ✅ **Test status: EXTENDED (2026-11-02).** `test_missing_required_field` now has an `expected_value` column, so bug #17 is asserted automatically. The `additionalneeds` case (`[additionalneeds-200-Breakfast]`) checks that the PUT response still contains the old `"Breakfast"`, with a `# Known API bug` comment and a failure message naming the missing field. The `400` cases use `None` as a placeholder, because `expected_value` is not checked for them. All 6 cases pass. At this point the check was on the PUT response only.
- ✅ **Test status: EXTENDED (2026-11-04).** The `additionalneeds` case now also sends a follow-up GET. It asserts `200` and that the stored value is still `"Breakfast"`, with failure messages that name the follow-up GET. The `400` cases don't have this check. All 6 cases pass.

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

**Test 7: PUT request with nested `bookingdates.checkin`/`checkout` set to an empty or whitespace-only string**
(Created a valid booking, then sent a full update payload with `bookingdates.checkin` set to `""` — leaving `checkout` valid — then repeated with `bookingdates.checkout` set to `""` — leaving `checkin` valid. Repeated both with the whitespace-only string `" "`. Valid auth token included every time.)
Expected (assumed): 400 Bad Request
Actual: **200** for all four cases, and the date value comes back corrupted to **`"0NaN-aN-aN"`** — the same coercion as bug #6, not a distinct behavior; unlike replacing the whole `bookingdates` object (which is correctly rejected with 400, see Test 6), an empty or whitespace-only string for just one nested date field is silently accepted and corrupted. Confirmed by `test_empty_string_nested_bookingdates_field`.
- `""` → **200**, stored as `"0NaN-aN-aN"` — 🐛 **Bug:** should be rejected with 400.
- `" "` → **200**, stored as `"0NaN-aN-aN"` — 🐛 **Bug:** should be rejected with 400.
- ✅ **Test status: REFACTORED AND EXTENDED (2026-11-01).** `test_empty_string_nested_bookingdates_field` used to loop over `checkin` and `checkout`, so a failure on `checkin` stopped the test and hid `checkout`. It is now parametrized like Test 2b: `date_key` and the empty value are separate parametrize decorators, so each combination runs as its own case — 4 cases in total, all passing. Each row holds its expected status and stored value, and both rows have `# Known API bug` comments. The status code is asserted for every case, with failure messages naming the date key and the value sent; `400` cases would assert the `"Bad Request"` body, and `200` cases compare the stored date with the row's expected value. Added the whitespace-only value `" "`, which behaves the same as `""`.

**Test 8: PUT request with no `Cookie`/auth token**
(Created a valid booking, then sent a full update payload to it with no `Cookie` header at all.)
Expected: 403 Forbidden, per API docs.
Actual: **403 Forbidden** ✅ — matches documented behavior, consistent with DELETE's handling of the same condition (see DELETE Test 6). A follow-up GET returns 200 with the original `firstname`, so the update was not applied (check added 2026-11-03).

**Test 9: PUT request with an invalid/expired auth token**
(Created a valid booking, then sent a full update payload to it with a well-formed but bogus `Cookie: token=invalidtoken123` instead of a real token.)
Expected: 403 Forbidden, per API docs.
Actual: **403 Forbidden** ✅ — matches documented behavior, consistent with DELETE's handling of the same condition (see DELETE Test 5). A follow-up GET returns 200 with the original `firstname`, so the update was not applied (check added 2026-11-03).

---

PUT method test cases are complete — all planned cases (happy path, wrong data type incl. nested `bookingdates` dates, non-existent ID, missing required field, long strings incl. nested `bookingdates`, empty strings incl. nested `bookingdates`, no auth token, invalid auth token) are automated in `test_booking_put.py` and pass.

---

# Test Cases — DELETE Method

**Test 1: DELETE request (happy path)**
Creates a booking, authenticates, deletes the booking, then confirms with a follow-up GET that the record is actually gone.
Expected: 201 on delete, 404 on the follow-up GET.
Actual: 201 ✅ ("Created" body) on delete, 404 ✅ ("Not Found" body) on the follow-up GET — the booking is genuinely removed, not just marked deleted.
✅ **Test status: UPDATED (2026-11-04).** The status-code failure message now includes the response body and headers, to help diagnose the intermittent `403` (see section 4 of the [test summary report](../test-summary-report.md)). The test passes. This message has not been seen in a real failure yet.

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
Actual: **403 Forbidden** ✅ — matches documented behavior. A follow-up GET returns 200, so the booking was not deleted (check added 2026-11-03).

**Test 6: DELETE request with no `Cookie`/auth token**
(Created a valid booking, then sent the DELETE with no `Cookie` header at all.)
Expected: 403 Forbidden, per API docs.
Actual: **403 Forbidden** ✅ — matches documented behavior. A follow-up GET returns 200, so the booking was not deleted (check added 2026-11-03).

---

DELETE method test cases are now complete — all planned cases (happy path, non-existent ID, double delete, malformed ID, invalid token, missing token) are automated in `test_booking_delete.py` and pass.

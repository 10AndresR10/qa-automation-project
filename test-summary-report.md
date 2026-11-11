# Test Summary Report — restful-booker API

**Date:** 2026-11-11
**Tester:** Andres Reyes
**System under test:** [restful-booker](https://restful-booker.herokuapp.com/apidoc/index.html) (public QA practice API)
**Environment:** Python 3.14.7, pytest 9.1.1, requests 2.34.2, pytest-html 4.2.0, Windows 11

## 1. Summary

The automated suite ran 180 tests against the GET, POST, PUT and DELETE
`/booking` endpoints. **179 of 180 tests passed** in about 178 seconds in the
latest run. The one failure, `test_empty_string_field[lastname-200-]` (PUT),
passed in 5 re-runs right after, and its status code wasn't recorded (see
section 4). A run of the PUT tests on 2026-11-05 had one cleanup error that was
most likely caused by the API resetting, and `test_delete_method` failed once on
2026-11-06 for a reason that wasn't recorded (see section 4). Most tests are
parametrized, so each wrong value or field runs as its own case.

A passing test does not mean the API is correct. Many tests assert the
API's *actual* behavior, and several of those behaviors are bugs. Each one is
marked with a `Known API bug` comment in the test code. If the API is fixed,
those tests will fail, and that failure shows the behavior changed.

The happy paths work: bookings can be created, read, updated and deleted, and
authentication is enforced on PUT and DELETE. The main problems are **weak
input validation** and **inconsistent status codes**. The most serious finding
is that the API **silently corrupts data** instead of rejecting bad input.

## 2. Results by endpoint

| Endpoint | Tests | Passed | Failed | Areas covered |
|---|---|---|---|---|
| GET `/booking/{id}` | 5 | 5 | 0 | Happy path, malformed / non-existent / whitespace / very large ID |
| POST `/booking` | 84 | 84 | 0 | Happy path, wrong data types (incl. nested `bookingdates` dates), boundary values, missing fields, empty strings, long strings, equivalence partitioning on dates (incl. a non-leap-year and a leap-year 29 February) |
| PUT `/booking/{id}` | 85 | 84 | 1 | Happy path, wrong data types (incl. nested `bookingdates` dates), non-existent ID, missing fields, long strings, empty strings (incl. nested `bookingdates` dates), missing / invalid token |
| DELETE `/booking/{id}` | 6 | 6 | 0 | Happy path, non-existent / already-deleted / malformed ID, missing / invalid token |
| **Total** | **180** | **179** | **1** | |

To reproduce the HTML report:

```bash
pytest tests/ --html=report.html --self-contained-html
```

## 3. Key findings

Bug numbers refer to the full list in
[`tests/manual-test-cases.md`](tests/manual-test-cases.md#summary-of-bugs--api-behavior-discovered).

### High severity: silent data corruption

The API returns `200 OK` but stores a different value than the client sent.
The client has no way to know the data is wrong.

| Input | Stored as | Bugs |
|---|---|---|
| `totalprice` as `""`, a boolean, or a long string | `null` | #4, #10, #13 |
| `depositpaid` as `""` | `false` | #4, #13 |
| `depositpaid` as a long string | `true` | #10 |
| `depositpaid` as the string `"False"` | `true` | #19 |
| `checkin` / `checkout` as an invalid date (e.g. `"2099-13-01"`), `""`, `" "`, or a long string | `"0NaN-aN-aN"` | #6, #10, #13 |
| `checkin` / `checkout` as a numeric string (e.g. `"275759"`) | `"5759-01-01"` (year truncated) | #16 |
| `checkin` / `checkout` as a number or boolean (e.g. `275760`) | `"1970-01-01"` (read as milliseconds) | #22 |
| `checkin` / `checkout` as a negative year (`"-2026-01-21"`) | `"2026-01-21"` (minus sign dropped) | #23 |
| `checkin` / `checkout` as `"01/02/2026"` | `"2026-01-02"` (read as month/day) | #25 |
| `checkin` / `checkout` as an impossible day (`"2026-02-29"`) | `"2026-03-01"` (rolled over into the next month) | #26 |

The rows where the stored value looks normal are the most dangerous: a
truncated year, a dropped minus sign, a swapped day and month, a rolled-over
day, or
`depositpaid` flipped to `true` are all hard to notice.

### Medium severity: missing or inconsistent validation

- **Wrong data types cause `500 Internal Server Error`** instead of
  `400 Bad Request` (#1). A 500 means the server crashed on the input instead
  of validating it. On POST, a `null` date in `bookingdates` also returns
  `500` (#24).
- **POST and PUT validate the same input differently.** For a missing field,
  POST returns `500` and PUT returns `400` (#9). For a wrong type in the whole
  `bookingdates` object, POST returns `500` and PUT returns `400` (#20).
- **`firstname` / `lastname`: `true` returns `500`, but `false` is accepted**
  and stored as `false` (#14). The server may only check values that are
  truthy: on POST and PUT, `0` is stored too, but `3.14` returns `500` (#18).
- **`additionalneeds` has no type check.** Numbers and booleans are stored
  as sent (#15).
- **No range check on `totalprice`.** POST and PUT both accept and store a
  negative price such as `-1000` (#21).
- **No length limit** on string fields. 1,100-character values are accepted
  (#5, #10).
- **PUT acts like PATCH** for the optional `additionalneeds` field. When it
  is omitted, the old value is kept instead of cleared (#17). An automated
  test asserts this on the PUT response and with a follow-up GET.

### Low severity: inconsistent status codes

- **A booking that doesn't exist returns different codes depending on the
  method.** GET returns `404 Not Found`, but PUT and DELETE return
  `405 Method Not Allowed` (#8, #11). `405` means the method itself is not
  supported, which is misleading.
- **Malformed IDs are not treated as bad requests.** GET returns `404` and
  DELETE returns `405`, but neither returns `400` (#2, #12).
- **A successful DELETE returns `201 Created`** with a `"Created"` body.
  `200 OK` or `204 No Content` would be the standard response. This matches
  the API docs, so it is a design issue, not a bug.

### What works as expected

- Create, read, update and delete all work for valid input.
- PUT and DELETE return `403 Forbidden` with a missing or invalid token, and a
  follow-up GET confirms the update or delete was not applied.
- Valid dates are stored exactly as sent (equivalence partitioning, valid
  partition).
- `additionalneeds` is correctly optional on both POST and PUT.

## 4. Test stability

- `test_already_deleted_booking_ID` (DELETE) failed once in 10 runs on
  2026-09-29, on the response body only. This is most likely an unstable
  response from the shared public API.
- **Intermittent `403` with a token from `/auth`.** This has happened three
  times. It is most likely caused by the API resetting its data during a test,
  not by an authentication bug:
  - `test_delete_method` (DELETE) failed once in a full run on 2026-11-03: it
    got `403` instead of `201`. It passed in the next full run and in 10 runs on
    its own, and 5 direct requests also returned `201`.
  - `test_put_wrong_data[totalprice-200-False-None]` (PUT) failed once in a full
    run on 2026-11-04: it got `403` instead of `200`. It passed in the next full
    run and in 10 runs on its own.
  - `test_empty_string_field[totalprice-200-None]` (PUT) passed on 2026-11-05,
    but its cleanup reported an error: the DELETE for booking `5326` got `403`
    instead of `201` or `405`.
- **Unexplained failure on 2026-11-06.** `test_delete_method` failed once in a
  run of the GET and DELETE tests, and that run took about 15 seconds instead of
  about 8. The failure output was not kept, so the status code is unknown and this
  may not be the same `403`. The test then passed 6 times in a row, and the next
  full run passed. The highest booking ID dropped from `1333` to `264` in the
  8 minutes around it, which fits another reset but doesn't prove one.
- **Unexplained failure on 2026-11-11.** `test_empty_string_field[lastname-200-]`
  (PUT) failed once in a full run, on the status-code assert. That assert has no
  failure message, and the rest of the output was not kept, so the status code
  is unknown. All 6 cases of the test then passed in 5 re-runs in a row. The
  highest booking ID was `550` right after, much lower than the IDs seen on
  2026-11-09 (around `3353`), so a reset happened at some point in between, but
  there is no evidence that it happened during this test.
- **Evidence for the reset, from the 2026-11-05 error.** The PUT in that test
  returned `200`, so the token was valid, but the cleanup DELETE with the same
  token got `403`. About 23 seconds later, a GET for booking `5326` returned
  `404` even though the DELETE had failed, and the same token still got `403`.
  The highest booking ID on the API had also dropped from `5326` to `282`. The
  reset itself was not observed, so this is strong evidence from one failure, not
  proof. The token and response details were not recorded for the first two
  failures.
- **What failures show now.** `test_delete_method`, `test_put_wrong_data` and
  the cleanup in `delete_booking` show the response body and headers if the
  status code is wrong. From 2026-11-04 to 2026-11-09, failing tests that used
  the `token` fixture also printed the token. That print was removed so the
  token doesn't end up in CI logs.
- **How cleanup handles a reset.** Since 2026-11-06, if the cleanup DELETE gets
  `403`, the fixture sends a GET. A `404` means the booking is already gone, so
  cleanup passes. Anything else fails, because a valid token was rejected while
  the booking still exists. Both paths were checked by temporarily using a fake
  token. A real reset has not gone through this code yet.
- **Known limitation.** A reset during a test can make that test fail, and the
  suite can't prevent this on a shared public API. Re-run the test before
  treating a `403` with a valid token as a bug.
- The suite depends on a public API that other people use at the same time,
  so run times and occasional responses can vary. Cleanup also adds requests
  to most tests: the latest full run took about 178 seconds with 180 tests, up
  from about 159 seconds with 168 tests on 2026-11-09, about 105 on 2026-11-06
  and about 87 before cleanup was added. Part of the increase comes from the two POST wrong-data tests. Each of their 61 cases now
  creates and deletes an unused `existing_booking_id` booking, and the `200`
  cases also delete their own booking. API speed varies too, so the exact
  share is not known.

## 5. Recommendations

**For the API:**
1. Validate every field's type, format and length, and return `400` with a
   clear message instead of storing a corrupted value.
2. Return `404 Not Found` for a missing booking on every method.
3. Handle missing required fields the same way on POST and PUT.

**For the test suite:**
1. Add a fixture that only returns a valid booking payload. The POST
   wrong-data tests use `existing_booking_id` just for its payload, so each of
   their 61 cases creates and deletes a booking it never uses (see section 4).
   The same payload dict is also repeated in several POST tests.
2. Run the suite in CI (GitHub Actions) on every push. This is Milestone 6.
3. Confirm the reset by checking the highest booking ID regularly, to see whether
   it drops at a steady interval.
4. If the intermittent `403` in section 4 appears in another test, add the
   response body and headers to that test's failure message too. The PUT
   `test_empty_string_field` status-code assert is the next candidate: it failed
   on 2026-11-11 without showing the status code.

Done since the last report:
- The wrong-data, missing-field, empty-string and long-string tests on POST
  and PUT are now parametrized, one case per field or value, so a failure
  points to the exact input.
- Bug #17 (PUT keeps the old `additionalneeds`) is now asserted by
  `test_missing_required_field` (2026-11-02).
- A negative `totalprice` is now tested on PUT too, which confirms bug #21
  there (2026-11-02).
- `test_put_wrong_data` now covers most of the wrong values POST Test 2
  tests: 29 cases (2026-11-02).
- `0` in `firstname` / `lastname` is now tested on POST. It is stored, the same
  as on PUT, so bug #18 is not a POST-vs-PUT split (2026-11-03).
- The PUT and DELETE missing-token and invalid-token tests now use a follow-up
  GET to confirm the update or delete was not applied (2026-11-03).
- `test_missing_required_field` now confirms bug #17 with a follow-up GET, not
  only the PUT response (2026-11-04).
- Failing tests now show the token, and `test_delete_method` and
  `test_put_wrong_data` also show the response body and headers, to help
  diagnose the intermittent `403` (2026-11-04).
- The `existing_booking_id` fixture now deletes its booking after each test. In
  a checked GET run, the DELETE returned `201` and a follow-up GET returned `404`
  (2026-11-05).
- The cleanup no longer fails when a `403` is caused by the booking already being
  gone, which is what an API reset would do (2026-11-06).
- `delete_booking` moved to `tests/helpers.py`, and `test_wrong_data_type`
  (POST) now deletes the bookings it creates (2026-11-08).
- `test_wrong_data_type_nested_dict` (POST) now deletes the bookings it
  creates, and the `token` fixture no longer prints the token (2026-11-09).
- `test_missing_required_field` (POST) now deletes the booking from its
  `additionalneeds` case and asserts that `additionalneeds` is not stored. Before
  this, that case only checked the status code (2026-11-09).
- `test_empty_string_field` (POST) now deletes its booking, and its asserts
  have failure messages that name the field (2026-11-09).
- `test_extremely_long_string` (POST) is now parametrized, one field per case
  at 500–900 characters, and deletes its bookings (2026-11-10).
- Both POST equivalence-partitioning tests are now parametrized over
  `checkin`/`checkout` and delete their bookings. The invalid-date test found
  bug #26 (`"2026-02-29"` rolls over to `"2026-03-01"`), and the valid-date test
  confirms the real leap day `"2028-02-29"` is stored as sent (2026-11-11).
- Every POST test now cleans up the bookings it creates, so the POST cleanup
  recommendation from the last report is done (2026-11-11).

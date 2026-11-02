# Test Summary Report — restful-booker API

**Date:** 2026-11-01
**Tester:** Andres Reyes
**System under test:** [restful-booker](https://restful-booker.herokuapp.com/apidoc/index.html) (public QA practice API)
**Environment:** Python 3.14.7, pytest 9.1.1, requests 2.34.2, pytest-html 4.2.0, Windows 11

## 1. Summary

The automated suite ran 157 tests against the GET, POST, PUT and DELETE
`/booking` endpoints. **All 157 tests passed** in about 77 seconds. Most
tests are parametrized, so each wrong value or field runs as its own case.

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
| POST `/booking` | 70 | 70 | 0 | Happy path, wrong data types (incl. nested `bookingdates` dates), boundary values, missing fields, empty strings, long strings, equivalence partitioning on dates |
| PUT `/booking/{id}` | 76 | 76 | 0 | Happy path, wrong data types (incl. nested `bookingdates` dates), non-existent ID, missing fields, long strings, empty strings (incl. nested `bookingdates` dates), missing / invalid token |
| DELETE `/booking/{id}` | 6 | 6 | 0 | Happy path, non-existent / already-deleted / malformed ID, missing / invalid token |
| **Total** | **157** | **157** | **0** | |

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

The rows where the stored value looks normal are the most dangerous: a
truncated year, a dropped minus sign, a swapped day and month, or
`depositpaid` flipped to `true` are all hard to notice.

### Medium severity: missing or inconsistent validation

- **Wrong data types cause `500 Internal Server Error`** instead of
  `400 Bad Request` (#1). A 500 means the server crashed on the input instead
  of validating it. On POST, a `null` date in `bookingdates` also returns
  `500` (#24).
- **POST and PUT validate the same input differently.** For a missing field,
  POST returns `500` and PUT returns `400` (#9). For a wrong type in the whole
  `bookingdates` object, POST returns `500` and PUT returns `400` (#20). For a
  number in `firstname` / `lastname`, POST returns `500` and PUT stores it
  (#18).
- **`firstname` / `lastname`: `true` returns `500`, but `false` is accepted**
  and stored as `false` (#14). The server may only check values that are
  truthy.
- **`additionalneeds` has no type check.** Numbers and booleans are stored
  as sent (#15).
- **No range check on `totalprice`.** POST accepts and stores a negative
  price such as `-1000` (#21).
- **No length limit** on string fields. 1,100-character values are accepted
  (#5, #10).
- **PUT acts like PATCH** for the optional `additionalneeds` field. When it
  is omitted, the old value is kept instead of cleared (#17).

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
- PUT and DELETE return `403 Forbidden` with a missing or invalid token.
- Valid dates are stored exactly as sent (equivalence partitioning, valid
  partition).
- `additionalneeds` is correctly optional on both POST and PUT.

## 4. Test stability

- `test_already_deleted_booking_ID` (DELETE) failed once in 10 runs on
  2026-09-29, on the response body only. This is most likely an unstable
  response from the shared public API.
- The suite depends on a public API that other people use at the same time,
  so run times and occasional responses can vary.

## 5. Recommendations

**For the API:**
1. Validate every field's type, format and length, and return `400` with a
   clear message instead of storing a corrupted value.
2. Return `404 Not Found` for a missing booking on every method.
3. Handle missing required fields the same way on POST and PUT.

**For the test suite:**
1. Add an automated assertion for bug #17 (PUT keeps the old
   `additionalneeds`).
2. Test a negative `totalprice` on PUT too (bug #21 is only confirmed on
   POST).
3. Clean up the bookings each test creates (a `yield` fixture), so the suite
   doesn't leave test data on the shared API.
4. Run the suite in CI (GitHub Actions) on every push. This is Milestone 6.

Done since the last report: the wrong-data, missing-field, empty-string and
long-string tests on POST and PUT are now parametrized, one case per field or
value, so a failure points to the exact input.

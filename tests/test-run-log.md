# Test Run Log

Results of full test suite runs and notes on test data cleanup, oldest first.
The test cases these runs refer to are in [`manual-test-cases.md`](manual-test-cases.md).
For the latest results, see the [test summary report](../test-summary-report.md).

# Full Test Suite Run — 2026-09-29

All four test files now take the shared `base_url` fixture from `conftest.py` instead of a per-class `base_url` attribute.

| File | Tests | Result |
|---|---|---|
| `test_booking_get.py` | 5 | 5 passed ✅ |
| `test_booking_post.py` | 7 | 7 passed ✅ |
| `test_booking_put.py` | 9 | 9 passed ✅ |
| `test_booking_delete.py` | 6 | 6 passed on re-run; `test_already_deleted_booking_ID` failed once ⚠️ |
| **Total** | **27** | **26 passed, 1 failed on first run; 27/27 on re-run** |

- Every result matches the Actual values in [`manual-test-cases.md`](manual-test-cases.md). No API behavior has changed since the last run.
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

- Every result matches the Actual values in [`manual-test-cases.md`](manual-test-cases.md).
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

- Every result matches the Actual values in [`manual-test-cases.md`](manual-test-cases.md).

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

- Every result matches the Actual values in [`manual-test-cases.md`](manual-test-cases.md).

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

- Every result matches the Actual values in [`manual-test-cases.md`](manual-test-cases.md).

---

# Test Data Cleanup — 2026-11-06

**`existing_booking_id` cleanup.** Since 2026-11-05, the fixture in `conftest.py` deletes its booking after each test. It accepts `201` (deleted) and `405` (the test already deleted the booking). In a checked GET run, the DELETE returned `201` and a follow-up GET returned `404`. Most POST tests create their own bookings with `requests.post`, so this cleanup doesn't cover them yet.

**Intermittent `403` and the API reset.** On 2026-11-05, the cleanup DELETE for booking `5326` got `403` right after a PUT with the same token returned `200`. About 23 seconds later, a GET for that booking returned `404`, the same token still got `403`, and the highest booking ID had dropped from `5326` to `282`. This suggests the API reset its data during the test. The reset itself was not observed, so this is strong evidence from one failure, not proof. See section 4 of the [test summary report](../test-summary-report.md).

**How cleanup handles a `403`.** Since 2026-11-06, if the cleanup DELETE gets `403`, the fixture sends a GET:
- `404` → the booking is already gone, so cleanup passes.
- Anything else → cleanup fails with an `ERROR`, because a valid token was rejected while the booking still exists.

Checked by temporarily sending a fake token in the cleanup DELETE:
- `test_get_method` passed, then reported an `ERROR` at teardown: the DELETE got `403` and the GET got `200`.
- `test_delete_method` passed with no `ERROR`, because the test had already deleted its booking.

The fake token has been removed. A real reset has not gone through this code yet.

**Full suite run — 2026-11-06:** 168 tests, 168 passed, in about 105 seconds. Before this, `test_delete_method` failed once in a run of the GET and DELETE tests. The failure output was not kept, so the cause is unknown. It then passed 6 times in a row (see section 4 of the [test summary report](../test-summary-report.md)).

# Test Data Cleanup — 2026-11-09

**POST test cleanup.** `delete_booking` now lives in `tests/helpers.py`, so tests can call it as well as the `existing_booking_id` fixture. POST Test 2 (2026-11-08), Test 2b (2026-11-09) and Test 3 (2026-11-09, the `additionalneeds` case) now delete the bookings they create. These POST tests still leave their bookings on the API:
- `test_empty_string_field`
- `test_extremely_long_string`
- `test_equivalence_partitioning_checkvariables`
- `test_equivalence_partitioning_valid_dates`

**Full suite run — 2026-11-09:** 168 tests, 168 passed, in about 159 seconds (up from about 105 on 2026-11-06; see section 4 of the [test summary report](../test-summary-report.md)).

**Token no longer printed.** The `token` fixture stopped printing the token on 2026-11-09. The assert in the fixture already shows the `/auth` response body when no token comes back, and a printed token would end up in CI logs once the suite runs on GitHub Actions.

# Test Data Cleanup — 2026-11-11

**POST test cleanup is finished.** `test_empty_string_field` (2026-11-09), `test_extremely_long_string` (2026-11-10) and both equivalence-partitioning tests (2026-11-11) now delete the bookings they create, so every POST test cleans up after itself. In every test the delete runs before the stored-value asserts, so a failing assert doesn't leave a booking behind.

**Full suite run — 2026-11-11:** 180 tests, 179 passed, 1 failed, in about 178 seconds. The count went up from 168 because `test_extremely_long_string` (1 → 3 cases) and both equivalence-partitioning tests (1 → 6 cases each) are now parametrized. The failure was `test_empty_string_field[lastname-200-]` (PUT), on its status-code assert. The status code was not recorded, and the test passed in 5 re-runs right after (see section 4 of the [test summary report](../test-summary-report.md)).

# GitHub Actions Runs — 2026-11-20 (UTC)

**Run `44669259098` (commit `a0a0e71`):** 186 tests, 185 passed, 1 failed, in about 141 seconds. The failure was `test_wrong_data_type_nested_dict[200-275759-1970-01-01-checkout]` (POST), in its cleanup, not in its own asserts: the DELETE for booking `32` got `403 Forbidden`, and the follow-up GET returned `200`, so `delete_booking` failed because the booking still existed. The low booking ID suggests the API had just reset. This is the first real `403` to reach the reset check in `delete_booking`, and it shows a case that check doesn't cover: the booking was most likely created after the reset, while the token was fetched before it (see section 4 of the [test summary report](../test-summary-report.md)).

**Run `44670324242` (commit `c9aa1a6`):** 188 tests, 188 passed, in about 16 seconds, about 10 minutes after the failed run.

# QA Automation Project — API Test Automation Suite

[![API Tests](https://github.com/10AndresR10/qa-automation-project/actions/workflows/tests.yml/badge.svg?branch=master)](https://github.com/10AndresR10/qa-automation-project/actions/workflows/tests.yml)

Portfolio project for API test automation in Python, built against the
[restful-booker API](https://restful-booker.herokuapp.com/apidoc/index.html)
(a public API made for QA practice).

- **188 automated tests** with `pytest` and `requests`, covering the GET, POST,
  PUT and DELETE `/booking` endpoints
- **26 API bugs found** and documented, most of them asserted by the tests
- **Test design techniques:** boundary value analysis, equivalence
  partitioning, negative testing (wrong types, missing fields, empty and long
  strings) and authentication checks
- **CI in GitHub Actions** on every push, with an HTML test report

## Bugs found

Testing found 26 bugs and unexpected behaviors in the API. The most serious
ones return `200 OK` but store a different value than the client sent, so the
client has no way to know the data is wrong:

| Severity | What the client sends | What the API does | Bug |
|---|---|---|---|
| High | `depositpaid: "False"` | Stores `true`: the booking is marked as paid | [#19](known-bugs.md) |
| High | `checkin: "2026-02-31"` (an impossible date) | Stores `"2026-03-03"`: rolls over into March | [#26](known-bugs.md) |
| High | `checkin: "01/02/2026"` (not `YYYY-MM-DD`) | Stores `"2026-01-02"`: silently reads it as month/day | [#25](known-bugs.md) |
| High | `checkin: "-2026-01-21"` (a negative year) | Stores `"2026-01-21"`: drops the minus sign | [#23](known-bugs.md) |
| High | `checkin: "275759"` (a numeric string) | Stores `"5759-01-01"`: keeps the last 4 digits of the year | [#16](known-bugs.md) |
| High | `totalprice: ""` or a boolean | Stores `null` | [#4](known-bugs.md), [#13](known-bugs.md) |
| Medium | A wrong data type, e.g. `firstname: true` | Crashes with `500 Internal Server Error` instead of `400` | [#1](known-bugs.md) |
| Medium | The same missing field on POST and PUT | POST returns `500`, PUT returns `400` | [#9](known-bugs.md) |
| Medium | `totalprice: -1000` | Accepts and stores a negative price | [#21](known-bugs.md) |
| Low | PUT or DELETE on a booking that doesn't exist | Returns `405 Method Not Allowed` instead of `404 Not Found` | [#8](known-bugs.md), [#11](known-bugs.md) |

Most of these bugs are asserted by automated tests, marked with a
`Known API bug` comment, so a fix in the API makes that test fail and shows
the change.
See [`known-bugs.md`](known-bugs.md) for the full list, and the
[test summary report](test-summary-report.md) for all of them by severity.
Results of past test runs are in [`tests/test-run-log.md`](tests/test-run-log.md).

## What's tested

| Endpoint | Tests | What's covered |
|---|---|---|
| GET `/booking/{id}` | 5 | Happy path; malformed, non-existent, whitespace and very large IDs |
| POST `/booking` | 88 | Happy path; a wrong data type in each field and in the nested `checkin`/`checkout` dates; boundary values on dates; missing fields; empty strings; long strings; equivalence partitioning on dates, including leap days |
| PUT `/booking/{id}` | 89 | Happy path, confirmed with a follow-up GET; the same wrong types and date values as POST; non-existent ID; missing fields; empty strings; long strings; missing and invalid token |
| DELETE `/booking/{id}` | 6 | Happy path, confirmed with a follow-up GET; non-existent, already-deleted and malformed IDs; missing and invalid token |

Most tests are parametrized, so each wrong value or field runs as its own test
case and a failure points to the exact input. Every test that creates a
booking deletes it afterwards.

See [`tests/manual-test-cases.md`](tests/manual-test-cases.md) for the test
cases, written before the code, with the actual results of each one.

## Tech stack

- Python 3 (CI uses Python 3.14)
- `requests` — HTTP calls
- `pytest` — test runner, fixtures and parametrization
- `pytest-html` — HTML test reports
- GitHub Actions — continuous integration

## Setup

```bash
git clone https://github.com/10AndresR10/qa-automation-project.git
cd qa-automation-project
python -m venv venv
venv\Scripts\activate      # Windows
source venv/bin/activate   # macOS/Linux
pip install -r requirements.txt
```

## Running the tests

```bash
pytest tests/
```

Generate an HTML report:

```bash
pytest tests/ --html=report.html --self-contained-html
```

The tests send real requests to the public restful-booker API, so they need an
internet connection. The API is shared with other users and resets its data
from time to time. If a reset happens during a run, a test can fail with
`403 Forbidden`; it passes on re-run (see section 4 of the
[test summary report](test-summary-report.md)).

## Continuous integration

A GitHub Actions workflow ([`.github/workflows/tests.yml`](.github/workflows/tests.yml))
runs the full suite on every push and pull request, and can be started by hand
from the Actions tab. Each run uploads the HTML report as a `test-report`
artifact, even when tests fail.

## Test report

The latest CI run (2026-11-21 UTC, run `44867387206`): **188 tests, all
passed**, in about 72 seconds. Several tests assert known API bugs, so a pass
means the API still behaves as documented, not that it is bug-free.

See [`test-summary-report.md`](test-summary-report.md) for the results by
endpoint, all bugs ranked by severity, and recommendations.

## Status

Complete: all seven milestones in
[`qa-automation-project-plan.md`](qa-automation-project-plan.md) are done.
Possible extensions:

- Test the number boundary of the JavaScript `Date` behind `checkin`/`checkout`
  (`8.64e15` milliseconds and one more)
- Validate the response structure against a JSON schema

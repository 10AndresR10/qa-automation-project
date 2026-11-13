# QA Automation Project — API Test Automation Suite

[![API Tests](https://github.com/10AndresR10/qa-automation-project/actions/workflows/tests.yml/badge.svg)](https://github.com/10AndresR10/qa-automation-project/actions/workflows/tests.yml)

Portfolio project for API test automation in Python, built against the
[restful-booker API](https://restful-booker.herokuapp.com/apidoc/index.html)
(a public API made for QA practice).

## What's tested

- **GET /booking/{id}**
  - Happy path: valid booking ID returns 200 with all booking fields, including the optional `additionalneeds`
  - Malformed ID, non-existent ID, whitespace ID, extremely large ID
- **POST /booking**
  - Happy path: valid payload creates a booking and returns the expected data
  - Wrong data type in each field (asserts known API bugs: `firstname`/`lastname` accept `false` but reject `true`, `totalprice` corrupted to `null` for booleans, no type check on `additionalneeds`)
  - Boundary values on numeric `checkin`/`checkout` strings (`275759`, `275760`, `275761`): up to `275760` the year is truncated to its last four digits (e.g. `"275759"` → `"5759-01-01"`); above it the date is corrupted to `"0NaN-aN-aN"`
  - Missing required field (each field omitted in turn; `additionalneeds` is optional, and the test checks it is not stored when omitted)
  - Empty-string field(s) (asserts known API bugs: `totalprice` corrupted to `null`, `depositpaid` corrupted to `false`, `checkin`/`checkout` corrupted to `"0NaN-aN-aN"`, instead of being rejected or stored as sent)
  - Extremely long string field (each string field set to a 500–900-character string in turn; stored as sent, so there is no length limit)
  - Equivalence partitioning on `checkin`/`checkout`: invalid calendar dates (month 13 and day 32 corrupted to `"0NaN-aN-aN"`; known API bug: `"2026-02-29"` in a non-leap year silently rolled over to `"2026-03-01"`) and valid dates, including the leap day `"2028-02-29"`
- **PUT /booking/{id}**
  - Happy path: authenticated update of all fields on an existing booking
  - Wrong data types in the payload (including a negative `totalprice`, which is stored as sent — known API bug)
  - Non-existent booking ID (asserts known API bug: returns `405 Method Not Allowed` instead of `404 Not Found`)
  - Missing required field (each field omitted in turn; asserts `400 Bad Request` for required fields, and `200` for the optional `additionalneeds`, including the known API bug that the old value is kept instead of cleared, confirmed with a follow-up GET)
  - Extremely long string field (each field set to a 1,100-character string in turn; asserts the stored value, including known API bugs: `totalprice` corrupted to `null`, `depositpaid` corrupted to `true`, `checkin`/`checkout` corrupted to `"0NaN-aN-aN"`, instead of being rejected or stored as sent)
  - Empty-string field (each field set to `""` in turn; asserts `400 Bad Request` for `bookingdates`, and for the other fields the stored value, including known API bugs: `totalprice` corrupted to `null`, `depositpaid` corrupted to `false`, instead of being rejected or stored as sent)
- **DELETE /booking/{id}**
  - Happy path: authenticated delete of an existing booking, confirmed with a follow-up GET
  - Non-existent booking ID, already-deleted booking ID (double delete), malformed (alphanumeric) booking ID (asserts known API bug: all return `405 Method Not Allowed` instead of `404 Not Found`)
  - Invalid/expired auth token
  - Missing `Cookie`/auth token

See [`tests/manual-test-cases.md`](tests/manual-test-cases.md) for the full
test case list written before implementation.

## Tech stack

- Python 3 (f-strings avoid nested double quotes, so the tests don't need 3.12+)
- `requests` — HTTP calls
- `pytest` — test runner and assertions
- `pytest-html` — HTML test reports

## Setup

```bash
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

## Continuous integration

A GitHub Actions workflow ([`.github/workflows/tests.yml`](.github/workflows/tests.yml))
runs the full suite on every push and pull request, and can be started by hand
from the Actions tab. Each run uploads the HTML report as a `test-report`
artifact, even when tests fail. The first CI run (2026-11-12) passed all 180
tests.

## Test report

The latest run (2026-11-11): **180 tests, 179 passed, 1 failed**. The failure
was a PUT test that passed in 5 re-runs right after, most likely the shared
API being unstable (see the report, section 4). Several tests assert
known API bugs, so a pass means the API still behaves as documented, not that
it is bug-free.

See [`test-summary-report.md`](test-summary-report.md) for the results by
endpoint, the key bugs ranked by severity, and recommendations.

## Status

Work in progress — see
[`qa-automation-project-plan.md`](qa-automation-project-plan.md) for the
project roadmap and next milestones.

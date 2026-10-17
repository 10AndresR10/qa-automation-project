# QA Automation Project — API Test Automation Suite

Portfolio project for API test automation in Python, built against the
[restful-booker API](https://restful-booker.herokuapp.com/apidoc/index.html)
(a public API made for QA practice).

## What's tested

- **GET /booking/{id}**
  - Happy path: valid booking ID returns 200 with the expected fields
  - Malformed ID, non-existent ID, whitespace ID, extremely large ID
- **POST /booking**
  - Happy path: valid payload creates a booking and returns the expected data
  - Wrong data type in each field (asserts known API bugs: `firstname`/`lastname` accept `false` but reject `true`, `totalprice` corrupted to `null` for booleans, no type check on `additionalneeds`)
  - Boundary values on numeric `checkin`/`checkout` strings (`275759`, `275760`, `275761`): up to `275760` the year is truncated to its last four digits (e.g. `"275759"` → `"5759-01-01"`); above it the date is corrupted to `"0NaN-aN-aN"`
  - Missing required field (each field omitted in turn; `additionalneeds` is optional)
  - Empty-string field(s) (asserts known API bugs: `totalprice` corrupted to `null`, `depositpaid` corrupted to `false`, `checkin`/`checkout` corrupted to `"0NaN-aN-aN"`, instead of being rejected or stored as sent)
  - Extremely long string in the string fields
  - Equivalence partitioning on `checkin`/`checkout`: invalid calendar dates (corrupted to `"0NaN-aN-aN"`) and valid dates
- **PUT /booking/{id}**
  - Happy path: authenticated update of all fields on an existing booking
  - Wrong data types in the payload
  - Non-existent booking ID (asserts known API bug: returns `405 Method Not Allowed` instead of `404 Not Found`)
  - Missing required field (each field omitted in turn; asserts `400 Bad Request` for required fields, `200` for the optional `additionalneeds`)
  - Extremely long string in a field
  - Empty-string field(s) (asserts known API bugs: `totalprice` corrupted to `null`, `depositpaid` corrupted to `false`, instead of being rejected or stored as sent)
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

## Status

Work in progress — see
[`qa-automation-project-plan.md`](qa-automation-project-plan.md) for the
project roadmap and next milestones.

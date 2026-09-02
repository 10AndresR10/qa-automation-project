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
  - Wrong data types in the payload
- **PUT /booking/{id}**
  - Happy path: authenticated update of all fields on an existing booking
  - Wrong data types in the payload
  - Non-existent booking ID
  - Missing required field (each field omitted in turn)
  - Extremely long string in a field

See [`tests/manual-test-cases.md`](tests/manual-test-cases.md) for the full
test case list written before implementation.

## Tech stack

- Python 3
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

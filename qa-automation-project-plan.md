# Bilingual QA Automation Engineer — Project Plan

## Goal
Build a portfolio-ready API test automation suite in Python, while practicing
technical English and core QA concepts along the way.

## Project 1: API Test Automation Suite

### Target API
- Restful-booker API (https://restful-booker.herokuapp.com/apidoc/index.html)
  — built specifically for QA practice
- Alternative: JSONPlaceholder (https://jsonplaceholder.typicode.com/) — simpler,
  good if Restful-booker feels like too much at first

### Tech stack
- Python 3.x
- `requests` — for making API calls
- `pytest` — test runner and assertions
- `pytest-html` — for generating readable test reports
- Git/GitHub — version control + portfolio hosting

### Milestones

1. **Manual test case design (no code yet)**
   Write 8–10 test cases in plain English covering:
   - Happy path (valid requests, expected 200/201 responses)
   - Invalid input (missing fields, wrong data types)
   - Edge cases (empty strings, very long strings, boundary values)
   - Not found / error cases (invalid IDs, wrong endpoints)

2. **Environment setup**
   - Create virtual environment
   - Install `requests`, `pytest`, `pytest-html`
   - Set up folder structure (see below)

3. **First working tests**
   - GET request tests: status code + response structure assertions
   - POST request tests: creating a resource, validating response

4. **Edge case coverage**
   - Boundary value tests
   - Invalid/malformed input tests
   - Equivalence partitioning applied to at least one endpoint

5. **Test reporting**
   - Generate HTML report with `pytest-html`
   - Review report and write a short summary of findings (practice English
     technical writing here)

6. **CI integration (stretch goal)**
   - Add a GitHub Actions workflow to run tests automatically on push

7. **Portfolio polish**
   - Clear README: what the project does, what's tested, how to run it
   - Push to GitHub

### Suggested folder structure
```
api-test-automation/
├── venv/
├── tests/
│   ├── test_booking_get.py
│   ├── test_booking_post.py
│   └── test_edge_cases.py
├── requirements.txt
├── pytest.ini
└── README.md
```

## Parallel tracks (ongoing, not sequential)

- **English practice:** narrate your code/thinking out loud in English while
  building; write commit messages, README, and test case descriptions in
  English
- **Testing theory:** as you write each test, note which concept it
  demonstrates (boundary value analysis, equivalence partitioning, etc.)
- **AI-assisted workflow:** use Claude Code to help debug, refactor, and
  explain errors — practice describing bugs in English when asking for help

## Next steps
- [ ] Open this plan in Claude Code
- [ ] Set up the project folder structure
- [ ] Write manual test cases (Milestone 1)
- [ ] Start coding first test file

# Unittests and Integration Tests

This project focuses on understanding and implementing unit tests and integration tests in Python using the `unittest` framework and `unittest.mock` library.

## Learning Objectives

At the end of this project, you should be able to explain:
- The difference between unit and integration tests
- Common testing patterns such as mocking, parametrizations and fixtures

## Project Structure

```
0x03-Unittests_and_integration_tests/
├── utils.py              # Generic utilities for github org client
├── client.py             # GitHub organization client
├── fixtures.py           # Test fixtures data
├── test_utils.py         # Unit tests for utils module
├── test_client.py        # Unit and integration tests for client module
└── README.md            # This file
```

## Requirements

- All files interpreted/compiled on Ubuntu 18.04 LTS using python3 (version 3.7)
- All files should end with a new line
- First line of all files should be exactly `#!/usr/bin/env python3`
- Code should use the pycodestyle style (version 2.5)
- All files must be executable
- All modules, classes and functions must have documentation
- All functions and coroutines must be type-annotated

## Setup

1. Install required dependencies:
```bash
pip install parameterized
```

2. Make all Python files executable:
```bash
chmod +x *.py
```

## Running Tests

Execute individual test files:
```bash
python -m unittest test_utils.py
python -m unittest test_client.py
```

Execute all tests:
```bash
python -m unittest discover
```

## Tasks Completed

### ✅ Task 0: Parameterize a unit test

**File:** `test_utils.py`

Created `TestAccessNestedMap` class to test the `utils.access_nested_map` function using parameterized testing.

**Key Concepts:**
- Parameterized testing with `@parameterized.expand`
- Testing nested dictionary access
- Using `assertEqual` for assertions

**Test Cases:**
- `nested_map={"a": 1}, path=("a",)` → returns `1`
- `nested_map={"a": {"b": 2}}, path=("a",)` → returns `{"b": 2}`
- `nested_map={"a": {"b": 2}}, path=("a", "b")` → returns `2`

**Usage:**
```python
from parameterized import parameterized

@parameterized.expand([
    (input1, input2, expected_output),
    # ... more test cases
])
def test_method(self, input1, input2, expected):
    self.assertEqual(actual_result, expected)
```

# Welcome Link Test Suite

## Structure

```
tests/
├── test_api.py           # API endpoint tests
├── test_security.py      # Security and validation tests
├── test_integration.py   # Integration tests for full flows
└── load/
    └── test_load.py      # Load and performance tests
```

## Running Tests

### Unit Tests

```bash
# Run all tests
python3 -m pytest tests/ -v

# Run specific test file
python3 -m pytest tests/test_security.py -v

# Run with coverage
python3 -m pytest tests/ --cov=server
```

### Load Tests

```bash
# Run load tests
python3 tests/load/test_load.py
```

## Test Categories

### Security Tests (`test_security.py`)

- Security Headers (X-Frame-Options, CSP, etc.)
- Input Validation
- Authentication Security
- Rate Limiting

### Integration Tests (`test_integration.py`)

- Auth Flow (register, login, protected endpoints)
- Guestview Flow
- API Endpoints
- Health Checks

### API Tests (`test_api.py`)

- Endpoint availability
- Response formats
- Error handling

### Load Tests (`load/test_load.py`)

- Health endpoint performance
- Auth endpoint performance
- Guestview endpoint performance
- Concurrent request handling

## Test Results (Phase 29)

```
Backend Tests: 38 passed, 6 skipped
Frontend Tests: 30 passed
Load Tests: 100% success rate (80/80 requests)

Performance:
- Health Endpoint: 59ms avg (EXCELLENT)
- Auth Login: 325ms avg (including bcrypt)
- Concurrent Requests: 76ms avg (GOOD)
```

## Writing New Tests

### Backend Test Example

```python
def test_my_endpoint():
    response = client.get("/api/my-endpoint")
    assert response.status_code == 200
    data = response.json()
    assert "id" in data
```

### Security Test Example

```python
def test_input_validation():
    response = client.post("/api/auth/register", json={
        "email": "invalid",
        "password": "123"
    })
    assert response.status_code == 422
```

### Load Test Example

```python
def test_endpoint():
    for i in range(10):
        start = time.time()
        response = requests.get(f"{BASE_URL}/api/endpoint")
        elapsed = (time.time() - start) * 1000
        print(f"Request {i}: {response.status_code} in {elapsed:.0f}ms")
```

## CI/CD Integration

Tests run automatically on:
- Push to main branch
- Pull requests
- Before deployment

## Notes

- Security header tests are skipped in TestClient due to middleware limitations
- Security headers are verified in production via curl tests
- Load tests run against production API
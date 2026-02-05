# Troubleshooting Guide for Phase Gate Testing

Common issues and solutions for detection, test generation, execution, and decision problems.

---

## Detection Issues

### Cannot Identify Integration Surface

**Symptom**: Unclear what Phase N exports or what Phase N+1 expects.

**Possible Causes**:
- Plan document is incomplete or ambiguous
- Implementation drifted from plan
- No clear boundary between phases

**Solutions**:

1. **Review Plan Document Carefully**
   ```bash
   # Read the plan with focus on phase boundaries
   grep -A 20 "Phase N" docs/plans/implementation.md
   grep -B 5 -A 20 "Phase N+1" docs/plans/implementation.md
   ```

2. **Inspect Actual Implementation**
   ```bash
   # List exported functions from Phase N
   grep -r "^def " src/phase_n/
   grep -r "^class " src/phase_n/
   grep -r "export " src/phase_n/
   ```

3. **Check for TODO Comments**
   ```bash
   # Find TODOs that might indicate integration points
   grep -r "TODO.*Phase N+1" src/phase_n/
   grep -r "FIXME.*integration" src/
   ```

4. **Examine Imports in Phase N+1 (if exists)**
   ```bash
   # See what Phase N+1 tries to import from Phase N
   grep -r "from phase_n" src/phase_n_plus_1/
   grep -r "import phase_n" src/phase_n_plus_1/
   ```

---

### False Positives in Surface Detection

**Symptom**: Detection finds items that are not actually part of the contract.

**Possible Causes**:
- Internal utilities marked as public
- Test utilities in source directories
- Auto-generated code included

**Solutions**:

1. **Filter by Naming Conventions**
   ```python
   # Only consider items without underscore prefix
   public_functions = [f for f in functions if not f.startswith('_')]

   # Only consider items in __all__
   if hasattr(module, '__all__'):
       public_items = module.__all__
   ```

2. **Exclude Test Utilities**
   ```python
   # Filter out test helpers
   exclude_patterns = ['test_', 'mock_', 'fixture_', 'helper_']
   contract_items = [i for i in items if not any(i.startswith(p) for p in exclude_patterns)]
   ```

3. **Check Documentation Tags**
   ```python
   # Look for @public or @api tags in docstrings
   def is_public_api(obj):
       docstring = inspect.getdoc(obj) or ""
       return '@public' in docstring or '@api' in docstring
   ```

---

### Missing Critical Integration Points

**Symptom**: Important integration points not detected automatically.

**Possible Causes**:
- Dynamic exports (e.g., `__getattr__`)
- Configuration-driven contracts
- Event-based communication

**Solutions**:

1. **Check for Dynamic Exports**
   ```python
   # Look for __getattr__ or dynamic imports
   grep -r "__getattr__" src/phase_n/
   grep -r "importlib" src/phase_n/
   grep -r "globals\(\)" src/phase_n/
   ```

2. **Review Configuration Files**
   ```bash
   # Check for API definitions in config
   cat config/api_endpoints.yaml
   cat config/event_definitions.json
   ```

3. **Manual Review Checklist**
   ```markdown
   - [ ] All public functions/classes documented
   - [ ] All API endpoints listed
   - [ ] All events documented
   - [ ] All database tables mapped
   - [ ] All configuration keys listed
   ```

---

## Test Generation Issues

### Generated Tests Are Too Generic

**Symptom**: Tests don't validate meaningful contract aspects.

**Possible Causes**:
- Insufficient type information
- Missing examples in documentation
- Complex validation logic

**Solutions**:

1. **Add Type Hints**
   ```python
   # Before: Generic test
   def test_function_exists():
       assert callable(module.function)

   # After: Type-aware test
   def test_function_signature():
       hints = get_type_hints(module.function)
       assert 'param1' in hints
       assert hints['param1'] == str
   ```

2. **Use Examples from Documentation**
   ```python
   # Extract examples from docstrings
   def extract_example_from_docstring(func):
       doc = inspect.getdoc(func)
       # Parse Example: sections
       # Generate tests from examples
   ```

3. **Add Custom Validators**
   ```python
   # Define contract-specific validation
   def validate_user_id(user_id):
       assert len(user_id) == 36  # UUID
       assert UUID(user_id)  # Valid format

   # Use in generated tests
   def test_user_id_format():
       user = create_user("test", "test@example.com")
       validate_user_id(user.id)
   ```

---

### Tests Fail to Compile or Import

**Symptom**: Generated tests have syntax errors or import failures.

**Possible Causes**:
- Module paths incorrect
- Missing dependencies in test environment
- Name conflicts

**Solutions**:

1. **Verify Module Paths**
   ```python
   # Check actual module structure
   python -c "import phase_n; print(phase_n.__file__)"

   # Fix import paths in generated tests
   # Before
   from phase_n import function

   # After
   from src.phase_n.module import function
   ```

2. **Check Dependencies**
   ```bash
   # Install missing dependencies
   pip install -r requirements.txt
   pip install -r requirements-test.txt
   ```

3. **Resolve Name Conflicts**
   ```python
   # Use aliases for conflicting names
   from phase_n import function as phase_n_function
   from phase_n_plus_1 import function as phase_n_plus_1_function
   ```

---

### Tests Are Too Brittle

**Symptom**: Tests fail on minor implementation changes that don't break contract.

**Possible Causes**:
- Testing implementation details
- Hardcoded values
- Overly specific assertions

**Solutions**:

1. **Test Behavior, Not Implementation**
   ```python
   # Brittle: Tests internal cache
   def test_uses_cache():
       with mock.patch('cache.get') as m:
           get_user(1)
           m.assert_called_once()

   # Robust: Tests observable behavior
   def test_returns_consistent_result():
       user1 = get_user(1)
       user2 = get_user(1)
       assert user1 == user2  # Cache is implementation detail
   ```

2. **Use Flexible Assertions**
   ```python
   # Brittle: Exact match
   assert error.message == "User not found with ID 123"

   # Robust: Pattern match
   assert "not found" in error.message.lower()
   assert "123" in error.message
   ```

3. **Validate Structure, Not Content**
   ```python
   # Brittle: Tests exact timestamp
   assert user.created_at == "2024-01-15T10:30:00Z"

   # Robust: Tests timestamp format
   assert isinstance(user.created_at, datetime)
   assert user.created_at <= datetime.now()
   ```

---

## Test Execution Issues

### Tests Fail Due to Environment

**Symptom**: Tests pass locally but fail in CI or vice versa.

**Possible Causes**:
- Environment-specific configuration
- Missing environment variables
- Database or service not available

**Solutions**:

1. **Standardize Environment**
   ```yaml
   # docker-compose.test.yml
   services:
     test:
       environment:
         - DATABASE_URL=postgresql://test:test@db/test
         - API_BASE_URL=http://api:8000
       depends_on:
         - db
         - api
   ```

2. **Use Test Configuration**
   ```python
   # config/test.py
   DATABASE_URL = os.getenv('TEST_DATABASE_URL', 'sqlite:///:memory:')
   API_TIMEOUT = 5  # Shorter timeout for tests
   ```

3. **Mock External Services**
   ```python
   @pytest.fixture
   def mock_external_api():
       with responses.RequestsMock() as rsps:
           rsps.add(
               responses.GET,
               'https://api.external.com/data',
               json={'status': 'ok'},
               status=200
           )
           yield rsps
   ```

---

### Flaky Tests

**Symptom**: Tests pass/fail inconsistently without code changes.

**Possible Causes**:
- Race conditions
- Time-dependent logic
- External service dependencies
- Random data in tests

**Solutions**:

1. **Fix Race Conditions**
   ```python
   # Bad: Depends on timing
   def test_async_operation():
       async_task()
       time.sleep(0.1)  # Flaky!
       assert result_ready()

   # Good: Proper synchronization
   def test_async_operation():
       event = threading.Event()
       async_task(callback=event.set)
       event.wait(timeout=5)
       assert result_ready()
   ```

2. **Control Time**
   ```python
   # Use freezegun for time-dependent tests
   @freeze_time("2024-01-15 10:30:00")
   def test_timestamp_generation():
       user = create_user("test", "test@example.com")
       assert user.created_at == datetime(2024, 1, 15, 10, 30, 0)
   ```

3. **Seed Random Data**
   ```python
   # Control randomness
   @pytest.fixture(autouse=True)
   def seed_random():
       random.seed(42)
       faker.seed_instance(42)
   ```

---

### Slow Test Execution

**Symptom**: Tests take too long to run, slowing down development.

**Possible Causes**:
- Integration tests running for every change
- Unnecessary database operations
- No test parallelization

**Solutions**:

1. **Categorize Tests**
   ```python
   # Mark slow tests
   @pytest.mark.slow
   def test_full_integration():
       pass

   # Run only fast tests during development
   # pytest -m "not slow"
   ```

2. **Use Transactions**
   ```python
   @pytest.fixture
def db_transaction():
       """Rollback after each test."""
       transaction = db.begin()
       yield db
       transaction.rollback()
   ```

3. **Parallel Execution**
   ```bash
   # Run tests in parallel
   pytest -n auto
   ```

---

## Decision Issues

### Gate Status Is Unclear

**Symptom**: Difficult to determine PASS/WARN/FAIL status.

**Possible Causes**:
- Ambiguous risk criteria
- Conflicting test results
- Subjective risk assessment

**Solutions**:

1. **Define Clear Criteria**
   ```yaml
   # gate-criteria.yaml
   pass:
     - all_tests_pass: true
     - no_high_risks: true
     - test_coverage_above: 80

   warn:
     - all_tests_pass: true
     - medium_risks_allowed: 3
     - untested_code_below: 20%

   fail:
     - any_test_fails: true
     - any_high_risk: true
     - breaking_changes: true
   ```

2. **Use Decision Matrix**
   ```python
   def determine_gate_status(test_results, risks):
       if not test_results.all_passed:
           return GateStatus.FAIL

       high_risks = [r for r in risks if r.level == RiskLevel.HIGH]
       if high_risks:
           return GateStatus.FAIL

       medium_risks = [r for r in risks if r.level == RiskLevel.MEDIUM]
       if medium_risks:
           return GateStatus.WARN

       return GateStatus.PASS
   ```

---

### False Positive Gate Pass

**Symptom**: Gate passes but integration fails later.

**Possible Causes**:
- Tests don't cover actual usage patterns
- Mocks don't match real behavior
- Environment differences

**Solutions**:

1. **Add Consumer-Driven Tests**
   ```python
   # Test actual consumer usage patterns
   def test_consumer_usage_pattern():
       """Replicate how Phase N+1 will actually use Phase N."""
       # Simulate Phase N+1 code
       user = phase_n.create_user("test", "test@example.com")
       profile = phase_n.get_profile(user.id)
       phase_n.update_profile(profile.id, {"name": "Test"})
   ```

2. **Validate Mocks Against Reality**
   ```python
   # Periodically verify mocks match real implementation
   def test_mock_accuracy():
       real_result = real_implementation()
       mock_result = mock_implementation()
       assert real_result.keys() == mock_result.keys()
   ```

3. **Run in Production-Like Environment**
   ```yaml
   # staging-tests.yml
   environment: staging
   tests:
     - contract_tests
     - integration_tests
     - smoke_tests
   ```

---

### False Negative Gate Fail

**Symptom**: Gate fails but integration would actually work.

**Possible Causes**:
- Overly strict tests
- Tests check implementation details
- Environment issues mistaken for contract issues

**Solutions**:

1. **Review Test Validity**
   ```markdown
   For each failing test, ask:
   - [ ] Does this test a real contract requirement?
   - [ ] Would the consumer actually fail if this failed?
   - [ ] Is this testing behavior or implementation?
   ```

2. **Relax Overly Strict Checks**
   ```python
   # Too strict: Requires exact error message
   assert error.message == "Specific error message"

   # Appropriate: Checks error type and general content
   assert isinstance(error, ValidationError)
   assert "invalid" in error.message.lower()
   ```

3. **Distinguish Environment from Contract Issues**
   ```python
   def diagnose_failure(test_result):
       if test_result.error_type == 'ConnectionError':
           return 'ENVIRONMENT'  # Not a contract issue
       if test_result.error_type == 'AssertionError':
           return 'CONTRACT'  # Real contract violation
   ```

---

## Common Error Messages

### "ModuleNotFoundError: No module named 'phase_n'"

**Cause**: Python path not set correctly.

**Solution**:
```bash
export PYTHONPATH="${PYTHONPATH}:$(pwd)/src"
# or
python -m pytest tests/  # Run as module
```

---

### "AssertionError: Expected 200, got 404"

**Cause**: API endpoint not registered or wrong URL.

**Solution**:
```python
# Check route registration
@app.get("/api/v1/users/{user_id}")  # Note: trailing slash matters!

# Verify URL construction
assert endpoint == "/api/v1/users/123"  # Not "/api/v1/users/123/"
```

---

### "KeyError: 'expected_key'"

**Cause**: Response schema changed or test out of sync.

**Solution**:
```python
# Add defensive checks
response = client.get('/api/v1/data')
data = response.json()

# Check before accessing
if 'expected_key' not in data:
    print(f"Available keys: {data.keys()}")
    raise

# Or use .get() with default
value = data.get('expected_key', default_value)
```

---

### "Database connection refused"

**Cause**: Database not running or wrong connection string.

**Solution**:
```bash
# Start test database
docker-compose up -d db

# Check connection string
python -c "import sqlalchemy; engine = sqlalchemy.create_engine(url); engine.connect()"
```

---

## Debugging Checklist

When tests fail unexpectedly:

- [ ] Check test environment matches production
- [ ] Verify all dependencies installed
- [ ] Check for recent changes to Phase N
- [ ] Review test logs for full error details
- [ ] Run tests individually to isolate failures
- [ ] Check for race conditions in async code
- [ ] Verify mocks match actual implementation
- [ ] Check for time-dependent logic
- [ ] Review database state between tests
- [ ] Check for environment variable differences

---

## Getting Help

If issues persist:

1. **Check Skill Documentation**
   - Review SKILL.md for usage examples
   - Check references/ for detailed guides

2. **Examine Logs**
   ```bash
   # Enable verbose logging
   export PHASE_GATE_DEBUG=1
   python scripts/run_gate_tests.py --verbose
   ```

3. **Run Diagnostics**
   ```bash
   # Check environment setup
   python scripts/diagnose_environment.py

   # Verify phase boundaries
   python scripts/detect_integration_surface.py --verify
   ```

4. **Compare with Working Examples**
   - Look at examples/ directory for reference implementations
   - Compare your setup with known working configurations

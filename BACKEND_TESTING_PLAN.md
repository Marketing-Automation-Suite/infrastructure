# Backend Testing & Quality Assurance Plan

**Focus Areas:** Backend Services, Contracts, Testing  
**Date:** 2025-12-16

---

## 🎯 Current Testing Status

### Services with Tests:
- ✅ `mcp-config-server` - Basic tests exist (needs auth tests)
- ✅ `xlam-server` - Basic health/endpoint tests
- ⚠️ `nft-software-engine` - Test file referenced but not found

### Services Missing Tests:
- ❌ `auth-service` - No tests found
- ❌ `token-verification-service` - No tests found
- ❌ `payment-service` - No tests found
- ❌ `nft-software-engine` - Tests missing

---

## 🔒 Priority 1: MCP Config Server - Security Test Updates

**Status:** ⚠️ **URGENT** - Tests need updating after security fixes

### Required Test Updates:

#### 1. Authentication Tests
```python
# tests/test_auth.py - NEW FILE NEEDED
- Test API key authentication
- Test missing API key (should fail)
- Test invalid API key (should fail)
- Test DISABLE_AUTH flag
- Test production mode enforcement
```

#### 2. CORS Tests
```python
# Update tests/test_api.py
- Test CORS with allowed origins
- Test CORS with unauthorized origins
- Test CORS in production mode
- Test ALLOWED_ORIGINS validation
```

#### 3. Encryption Tests
```python
# Update tests/test_encryption.py
- Test encryption key validation in production
- Test salt management
- Test key generation (dev only)
- Test that keys are never logged
```

---

## 🧪 Priority 2: Comprehensive Test Suite

### Test Coverage Goals:

| Service | Current | Target | Priority |
|---------|---------|--------|----------|
| mcp-config-server | 40% | 85% | HIGH |
| xlam-server | 30% | 80% | MEDIUM |
| nft-software-engine | 0% | 90% | HIGH |
| auth-service | 0% | 80% | HIGH |
| token-verification-service | 0% | 75% | MEDIUM |

---

## 📋 Testing Implementation Plan

### Phase 1: MCP Config Server Security Tests (IMMEDIATE)

**Files to Create/Update:**
1. `services/mcp-config-server/tests/test_auth.py` - NEW
2. `services/mcp-config-server/tests/test_api.py` - UPDATE
3. `services/mcp-config-server/tests/test_encryption.py` - UPDATE
4. `services/mcp-config-server/tests/test_cors.py` - NEW

### Phase 2: NFT Software Engine Tests

**Files to Create:**
1. `services/nft-software-engine/tests/test_wallet.py`
2. `services/nft-software-engine/tests/test_verification.py`
3. `services/nft-software-engine/tests/test_api.py`
4. `services/nft-software-engine/tests/test_contracts.py`

### Phase 3: Auth Service Tests

**Files to Create:**
1. `services/auth-service/tests/test_jwt.py`
2. `services/auth-service/tests/test_auth.py`
3. `services/auth-service/tests/test_api.py`

---

## 🔧 Test Infrastructure

### Required Test Dependencies:
```python
# pytest
# pytest-asyncio
# httpx (for async testing)
# pytest-mock
# pytest-cov (coverage)
# testcontainers (for database testing)
```

### Test Configuration:
```python
# pytest.ini or pyproject.toml
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
asyncio_mode = auto
```

---

## 📊 Test Categories

### 1. Unit Tests
- Individual function testing
- Mock external dependencies
- Fast execution
- High coverage

### 2. Integration Tests
- Service-to-service communication
- Database interactions
- External API calls (mocked)
- End-to-end flows

### 3. Security Tests
- Authentication/authorization
- Input validation
- SQL injection prevention
- XSS prevention
- CORS validation

### 4. Contract Tests
- API contract validation
- Schema validation
- Error response formats

---

## 🚀 Next Steps

1. **Immediate:** Update mcp-config-server tests for security fixes
2. **Short-term:** Create NFT engine test suite
3. **Medium-term:** Add auth-service tests
4. **Long-term:** Achieve 80%+ coverage across all services


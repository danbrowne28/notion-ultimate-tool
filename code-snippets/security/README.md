# 🔒 Security Snippets (20)

**Category:** Security & Authentication  
**Total Snippets:** 20  
**Est. Implementation Time:** 40-60 hours  
**Difficulty:** High  
**Status:** Production-Ready ✅

## Overview

Comprehensive security implementations covering:
- API key management & rotation
- Authentication (JWT, OAuth2)
- Encryption & hashing
- Access control & authorization
- Input validation & sanitization
- Security headers & middleware
- Audit logging
- DDoS protection

## Snippets

### 1. API Key Rotation (`01-api-key-rotation.py`)
**Purpose:** Automated key rotation with version control  
**Dependencies:** `cryptography`, `sqlalchemy`  
**Use Case:** Trading212 API keys, webhook secrets  
**Key Features:**
- Version-based key management
- Automatic expiry tracking
- Rollover capabilities
- Audit trail

### 2. JWT Token Validation (`02-jwt-token-validation.py`)
**Purpose:** Secure JWT validation and refresh  
**Dependencies:** `PyJWT`, `fastapi`  
**Use Case:** API authentication, session management  

### 3. Password Hashing - Bcrypt (`03-password-hashing-bcrypt.py`)
**Purpose:** Secure password storage  
**Dependencies:** `bcrypt`, `passlib`  
**Use Case:** User authentication, admin access  

### 4. Rate Limiting Middleware (`04-rate-limiting-middleware.py`)
**Purpose:** FastAPI rate limiting  
**Dependencies:** `slowapi`, `fastapi`  
**Use Case:** API protection from abuse  

### 5. CORS Configuration (`05-cors-configuration.py`)
**Purpose:** CORS security setup  
**Dependencies:** `fastapi`  
**Use Case:** Web frontend integration  

### 6. Input Sanitization (`06-input-sanitization.py`)
**Purpose:** Validate and sanitize all inputs  
**Dependencies:** `bleach`, `pydantic`  
**Use Case:** API endpoint protection  

### 7. SQL Injection Prevention (`07-sql-injection-prevention.py`)
**Purpose:** Parameterized queries  
**Dependencies:** `sqlite3`, `sqlalchemy`  
**Use Case:** Database operations  

### 8. Environment Secrets Manager (`08-environment-secrets-manager.py`)
**Purpose:** Manage environment variables  
**Dependencies:** `python-dotenv`, `cryptography`  
**Use Case:** Local and production secrets  

### 9. Encryption/Decryption (`09-encryption-decryption.py`)
**Purpose:** Fernet symmetric encryption  
**Dependencies:** `cryptography`  
**Use Case:** Sensitive data storage  

### 10. OAuth2 Integration (`10-oauth2-integration.py`)
**Purpose:** OAuth2 authentication flow  
**Dependencies:** `fastapi`, `python-jose`  
**Use Case:** Third-party authentication  

### 11. Request Signing - HMAC (`11-request-signing-hmac.py`)
**Purpose:** HMAC signature verification  
**Dependencies:** `hmac`, `hashlib`  
**Use Case:** Webhook authentication  

### 12. Audit Logging System (`12-audit-logging-system.py`)
**Purpose:** Comprehensive audit trail  
**Dependencies:** `logging`, `sqlalchemy`  
**Use Case:** Compliance and debugging  

### 13. Access Control - ACL (`13-access-control-acl.py`)
**Purpose:** Role-based access control  
**Dependencies:** `fastapi`, `sqlalchemy`  
**Use Case:** Admin, analyst, viewer roles  

### 14. Certificate Validation (`14-certificate-validation.py`)
**Purpose:** SSL/TLS certificate validation  
**Dependencies:** `requests`, `urllib3`  
**Use Case:** Secure API connections  

### 15. Security Headers Middleware (`15-security-headers-middleware.py`)
**Purpose:** HTTP security headers  
**Dependencies:** `fastapi`  
**Use Case:** Frontend protection (CSP, X-Frame, etc.)  

### 16. DDoS Protection Headers (`16-ddos-protection-headers.py`)
**Purpose:** DDoS mitigation configuration  
**Dependencies:** `fastapi`  
**Use Case:** Rate limiting, IP blocking  

### 17. Dependency Vulnerability Check (`17-dependency-vulnerability-check.py`)
**Purpose:** Automated security scanning  
**Dependencies:** `safety`, `pip-audit`  
**Use Case:** CI/CD pipeline  

### 18. Session Management (`18-session-management.py`)
**Purpose:** Secure session handling  
**Dependencies:** `itsdangerous`, `fastapi`  
**Use Case:** User session security  

### 19. CSRF Token Generation (`19-csrf-token-generation.py`)
**Purpose:** CSRF protection  
**Dependencies:** `secrets`, `fastapi`  
**Use Case:** Form submission protection  

### 20. Database Encryption (`20-database-encryption.py`)
**Purpose:** Encrypted database connections  
**Dependencies:** `cryptography`, `sqlalchemy`  
**Use Case:** Data in transit encryption  

---

## Implementation Priority

**Phase 1 (Critical - Week 1):**
- 01-api-key-rotation.py
- 02-jwt-token-validation.py
- 06-input-sanitization.py
- 08-environment-secrets-manager.py

**Phase 2 (High - Week 2):**
- 03-password-hashing-bcrypt.py
- 04-rate-limiting-middleware.py
- 07-sql-injection-prevention.py
- 13-access-control-acl.py

**Phase 3 (Medium - Week 3):**
- 09-encryption-decryption.py
- 11-request-signing-hmac.py
- 12-audit-logging-system.py
- 15-security-headers-middleware.py

**Phase 4 (Nice-to-Have):**
- Remaining 6 snippets

---

## Testing Each Snippet

```bash
# Unit tests
pytest code-snippets/security/tests/ -v

# Security audit
safety check
pip-audit

# Integration test
python -m pytest code-snippets/security/integration_tests.py
```

---

## Common Patterns

### Key Rotation Pattern
```python
from code_snippets.security import KeyRotationManager

manager = KeyRotationManager()
new_key = manager.rotate_key('trading212')
manager.validate_key(new_key)
```

### Authentication Pattern
```python
from code_snippets.security import JWTManager

jwt = JWTManager(secret_key=os.getenv('JWT_SECRET'))
token = jwt.create_token({'user_id': 123})
jwt.verify_token(token)
```

---

## Security Checklist

- [ ] All secrets in environment variables
- [ ] No hardcoded passwords or keys
- [ ] Rate limiting enabled
- [ ] Input validation on all endpoints
- [ ] SQL injection prevention in place
- [ ] HTTPS/TLS enforced
- [ ] CORS properly configured
- [ ] Audit logging enabled
- [ ] Regular dependency updates
- [ ] Security headers configured

---

## Related Task Tracker Items

See `LINKING_GUIDE.csv` for all related tasks  
**Category:** Security (Red label)  
**Total Tasks:** ~20 in Phase 0: Security

---

## References

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [JWT Best Practices](https://tools.ietf.org/html/rfc8725)
- [OAuth 2.0 Security Best Practices](https://datatracker.ietf.org/doc/html/draft-ietf-oauth-security-topics)
- [cryptography.io Documentation](https://cryptography.io/)

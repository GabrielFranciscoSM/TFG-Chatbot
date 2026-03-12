---
adr: 0028
title: "Use pydantic-settings for configuration management"
date: 2024-12-06
status: Accepted
parent: Architecture Decision Records
nav_order: 28
---

# ADR 0028 — Use pydantic-settings for configuration management

## Status

Accepted

## Context

The microservices in this project (backend, chatbot, rag_service) need to manage configuration from environment variables and `.env` files. Previously, configuration was handled inconsistently across services:

- **backend**: Used a plain Python class with `os.getenv()` and `python-dotenv`
- **chatbot**: Mixed `pydantic_settings.BaseSettings` with `os.getenv()` calls (incorrect usage)
- **rag_service**: Similar mixed pattern with manual type conversions like `int(os.getenv(...))`

This approach had several problems:

1. **Security risks**: Sensitive values (API keys, passwords, secret keys) could be accidentally logged or exposed in error messages
2. **Inconsistent patterns**: Each service handled configuration differently
3. **Type safety**: Manual `int()`, `float()` conversions were error-prone
4. **Hardcoded defaults**: `secret_key = "supersecretkey"` was a security vulnerability
5. **Code duplication**: MongoDB URI construction logic was duplicated across services

## Decision

Adopt `pydantic-settings` as the standard configuration management library across all Python microservices with the following conventions:

### 1. Use `BaseSettings` with `SettingsConfigDict`

```python
from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )
```

### 2. Use `SecretStr` for sensitive values

```python
secret_key: SecretStr = SecretStr("dev-only-secret-key-change-in-production")
mongo_root_password: SecretStr | None = None
gemini_api_key: SecretStr | None = None
```

This ensures secrets are displayed as `**********` in logs and repr.

### 3. Use lowercase field names

Pydantic Settings automatically maps `SECRET_KEY` env var to `secret_key` field when `case_sensitive=False`.

### 4. Provide helper methods for complex configurations

```python
def get_mongo_uri(self) -> str:
    """Construct MongoDB URI from configuration."""
    if self.mongo_uri:
        return self.mongo_uri.get_secret_value()
    # ... construction logic
```

### 5. Remove `python-dotenv` dependency

`pydantic-settings` handles `.env` file loading natively; `python-dotenv` is no longer needed in service code.

## Consequences

### Positive

- **Type safety**: Automatic type coercion and validation
- **Security**: `SecretStr` prevents accidental exposure of secrets in logs
- **Consistency**: Same pattern across all services
- **Less code**: Removed ~50 lines of boilerplate (manual `os.getenv()` calls, type conversions)
- **Better defaults**: Descriptive default for `secret_key` makes it obvious it must be changed
- **Centralized logic**: MongoDB URI construction in one place per service

### Negative

- **Migration effort**: Required updating all settings usages to lowercase names
- **Learning curve**: Team members need to understand `SecretStr.get_secret_value()` pattern
- **Slight verbosity**: Accessing secrets requires `.get_secret_value()` call

### Follow-ups

- [x] Update `backend/config.py` to use `pydantic-settings`
- [x] Update `chatbot/config.py` to remove `os.getenv()` mixing
- [x] Update `rag_service/config.py` to remove `os.getenv()` mixing
- [x] Update all usages of settings from `UPPERCASE` to `lowercase`
- [x] Add `SecretStr` for all sensitive fields
- [x] Remove `python-dotenv` from service dependencies
- [x] Verify all 102 tests pass

## Alternatives considered

### Option A: Continue with `python-dotenv` + `os.getenv()`

**Pros:**
- No migration needed
- Simple and familiar

**Cons:**
- No type safety
- No secret protection
- Inconsistent patterns
- More boilerplate code

### Option B: Use `dynaconf`

**Pros:**
- Multi-format support (YAML, TOML, JSON)
- Environment layering

**Cons:**
- Additional dependency
- More complex than needed
- Less Pydantic integration

### Option C: Use `pydantic-settings` (chosen)

**Pros:**
- Native Pydantic integration
- Type safety and validation
- `SecretStr` for security
- Already partially adopted

**Cons:**
- Requires migration
- Team learning curve

## References

- [pydantic-settings documentation](https://docs.pydantic.dev/latest/concepts/pydantic_settings/)
- [Pydantic SecretStr](https://docs.pydantic.dev/latest/concepts/types/#secret-types)
- [ADR 0005: Use Pydantic for data models](0005-use-pydantic-for-data-models.md)

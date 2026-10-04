## 2026-10-04 - Command Allowlisting and Execution Timeout in Frankenagent
**Vulnerability:** Arbitrary binary execution via unvalidated task commands and Denial of Service (DoS) risks from unbounded subprocess execution.
**Learning:** Naive denylists fail against path or argument tampering; commands must be checked against a strict executable allowlist, and subprocesses must enforce explicit execution timeouts.
**Prevention:** Always validate commands using an allowlist before execution and set `timeout=30` on all subprocess invocations.

## 2026-10-04 - Adding Unit Tests for Extract Data
**Vulnerability:** Missing unit tests could allow silent regressions in simple pipeline functions.
**Learning:** Even simple functions returning dictionaries require unit tests to verify the schema matches the downstream expectations and prevents future breaking changes.
**Prevention:** Always write robust test suites covering schema generation, dictionary key presence, and timestamp validation.

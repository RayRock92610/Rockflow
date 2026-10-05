## 2024-10-27 - Information Leakage in Task Execution
**Vulnerability:** Found `output=str(e)` in multiple files (`frankenagent_8_0_kesselflow.py`, `frankenagent_8_1_kesselflow.py`, `frankenagent_kesselflow.py`). This allows stack traces and internal exception details (such as local paths, environmental data, or syntax details) to be leaked into the database when a task fails.
**Learning:** Returning raw exception strings directly into persistent storage or APIs can inadvertently expose system internals. An attacker could intentionally trigger errors to map the environment.
**Prevention:** Catch generic exceptions and log them securely using `logging.error(..., exc_info=True)` while returning a sanitized, generic error message (e.g., "An error occurred during execution.") to the user or database.

## 2026-10-04 - Command Allowlisting and Execution Timeout in Frankenagent
**Vulnerability:** Arbitrary binary execution via unvalidated task commands and Denial of Service (DoS) risks from unbounded subprocess execution.
**Learning:** Naive denylists fail against path or argument tampering; commands must be checked against a strict executable allowlist, and subprocesses must enforce explicit execution timeouts.
**Prevention:** Always validate commands using an allowlist before execution and set `timeout=30` on all subprocess invocations.

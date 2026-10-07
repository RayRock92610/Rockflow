## 2024-10-27 - Information Leakage in Task Execution
**Vulnerability:** Found `output=str(e)` in multiple files (`frankenagent_8_0_kesselflow.py`, `frankenagent_8_1_kesselflow.py`, `frankenagent_kesselflow.py`). This allows stack traces and internal exception details (such as local paths, environmental data, or syntax details) to be leaked into the database when a task fails.
**Learning:** Returning raw exception strings directly into persistent storage or APIs can inadvertently expose system internals. An attacker could intentionally trigger errors to map the environment.
**Prevention:** Catch generic exceptions and log them securely using `logging.error(..., exc_info=True)` while returning a sanitized, generic error message (e.g., "An error occurred during execution.") to the user or database.

## 2026-10-04 - Command Allowlisting and Execution Timeout in Frankenagent
**Vulnerability:** Arbitrary binary execution via unvalidated task commands and Denial of Service (DoS) risks from unbounded subprocess execution.
**Learning:** Naive denylists fail against path or argument tampering; commands must be checked against a strict executable allowlist, and subprocesses must enforce explicit execution timeouts.
**Prevention:** Always validate commands using an allowlist before execution and set `timeout=30` on all subprocess invocations.

## 2026-10-04 - Enforcing Network Timeouts in External SDKs
**Vulnerability:** Denial of Service (DoS) risks via unbounded network calls when integrating with external services (e.g., GitHub, Gemini APIs).
**Learning:** Default timeout values for external SDK connections (or requests libraries) may be extremely high or nonexistent, leading to worker exhaustion if the external service hangs.
**Prevention:** Always enforce explicit read and connect timeouts (e.g., `timeout=30` or `request_options={"timeout": 30}`) when initializing clients or making network requests with external API SDKs.
## 2026-10-07 - [Path Traversal / Wrapper Script Execution in Subprocess]
**Vulnerability:** Command allowlist logic in `obey_rayrock_decree` checked only the basename of the given executable name, allowing an attacker to bypass the allowlist using directory path traversal (e.g., `./malicious/git`).
**Learning:** Checking only `os.path.basename` for command authorization permits unauthorized local wrapper scripts matching the name of an allowed binary to be executed, breaking the intended sandbox isolation.
**Prevention:** explicitly reject directory separators in command tokens (e.g., `if os.path.dirname(tokens[0]): return False`), and use `shutil.which()` to resolve absolute paths of system binaries before updating the invocation token for `subprocess.check_output`.

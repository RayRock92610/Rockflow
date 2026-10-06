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
## 2024-10-06 - Path Traversal & Wrapper Bypass in Command Allowlist
**Vulnerability:** The current `obey_rayrock_decree` implementation tokenizes user input and strictly extracts the base executable via `os.path.basename(tokens[0])` for validation. This allows attackers to bypass the allowlist by creating a malicious binary named identically to an allowed command (e.g., `./ls`) and using path traversals to execute it, as the path context is discarded prior to allowlist validation.
**Learning:** `os.path.basename` alone strips path context, which breaks the assumption that the invoked binary is exactly the one expected by the system (such as `/usr/bin/ls`).
**Prevention:** Strictly enforce that the user-provided command does not contain directory separators (i.e., `os.path.dirname` must be empty). Additionally, resolve the absolute path of the command using `shutil.which` and execute the absolute path to guarantee the system-level binary is invoked, preventing execution of local wrapper scripts.

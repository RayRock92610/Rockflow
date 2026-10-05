## 2026-10-04 - Command Allowlisting and Execution Timeout in Frankenagent
**Vulnerability:** Arbitrary binary execution via unvalidated task commands and Denial of Service (DoS) risks from unbounded subprocess execution.
**Learning:** Naive denylists fail against path or argument tampering; commands must be checked against a strict executable allowlist, and subprocesses must enforce explicit execution timeouts.
**Prevention:** Always validate commands using an allowlist before execution and set `timeout=30` on all subprocess invocations.

## 2026-10-04 - Enforcing Network Timeouts in External SDKs
**Vulnerability:** Denial of Service (DoS) risks via unbounded network calls when integrating with external services (e.g., GitHub, Gemini APIs).
**Learning:** Default timeout values for external SDK connections (or requests libraries) may be extremely high or nonexistent, leading to worker exhaustion if the external service hangs.
**Prevention:** Always enforce explicit read and connect timeouts (e.g., `timeout=30` or `request_options={"timeout": 30}`) when initializing clients or making network requests with external API SDKs.

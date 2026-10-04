## 2026-10-04 - Command Allowlisting and Execution Timeout in Frankenagent
**Vulnerability:** Arbitrary binary execution via unvalidated task commands and Denial of Service (DoS) risks from unbounded subprocess execution.
**Learning:** Naive denylists fail against path or argument tampering; commands must be checked against a strict executable allowlist, and subprocesses must enforce explicit execution timeouts.
**Prevention:** Always validate commands using an allowlist before execution and set `timeout=30` on all subprocess invocations.
## 2024-10-04 - Strict Path Resolution with shutil.which
**Vulnerability:** Path Traversal / Wrapper Bypass allowing Arbitrary Command Execution
**Learning:** Checking only the `basename` of an executable against an allowlist (e.g. allowing `python3` but getting passed `/tmp/python3`) permits arbitrary commands to run securely-validated binary names via custom malicious binaries.
**Prevention:** Use `shutil.which` to resolve both the expected base binary and the requested binary string. Block execution if the requested absolute path deviates from the actual absolute path of the allowed system binary, and substitute the command with the exact system path.

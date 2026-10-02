## 2024-05-18 - Fix Command Injection and Information Leakage in Task Executor
**Vulnerability:** Command injection vulnerability in `subprocess.check_output(content, shell=True)` allowing execution of arbitrary shell commands from unverified `content`. In addition, catching exceptions via `Exception as e` and directly storing `str(e)` in database exposed sensitive system internals/stack traces (Information Leakage).
**Learning:** Using `shell=True` on dynamic user input is always a critical risk. Storing raw exception strings directly to a public or persistent record database exposes the system structure. Combining both made the environment highly susceptible to discovery and command execution attacks.
**Prevention:** Always use `shell=False` combined with array arguments (`shlex.split`) for dynamic arguments. Exception contents should be securely logged internally rather than returned directly to user inputs/records; generic error messages must be returned instead.
## 2024-05-18 - Fix Command Injection in Backup Script
**Vulnerability:** Command injection vulnerability in `backup_kesselflow.sh` where `tar -czf "$ARCHIVE" $FILES` is used. Unquoted variable expansion like `$FILES` in a command is vulnerable to option injection. If a malicious file name starts with `--checkpoint`, `tar` would execute arbitrary code.
**Learning:** Using unquoted shell variables containing file names in commands like `tar` is a critical risk, allowing option injection and code execution.
**Prevention:** Always use `find -print0` piped to commands that support `--null -T -` (like `tar`) or `xargs -0` to handle file names safely and prevent option injection.
## 2025-02-23 - Fix Insecure Deserialization in Vector Storage
**Vulnerability:** Insecure deserialization via `np.load(VECTOR_PATH, allow_pickle=True)`. Loading unverified numpy arrays with `allow_pickle=True` can lead to Arbitrary Code Execution (ACE) because it uses Python's `pickle` module under the hood.
**Learning:** Storing dictionaries in numpy files requires `allow_pickle=True`, which bypasses security controls and introduces critical ACE/RCE vectors if the storage file is ever tampered with or replaced.
**Prevention:** Always use safe serialization formats like JSON for dictionaries, even if they contain numpy arrays. Convert arrays to lists for JSON storage, and reconstruct them upon loading.
## 2024-05-18 - Fix Sensitive Data Leakage in DAG Logs
**Vulnerability:** Raw exception strings printed directly to standard output/logs (`print(f"Error: {e}")`) when external API requests failed in DAG tasks.
**Learning:** Catching and printing the raw Python `Exception` object can leak sensitive information like HTTP URLs, query parameters, API keys, or request payloads directly into Airflow task execution logs, creating a credential exposure risk.
**Prevention:** Never print or log raw exceptions directly when integrating with third-party APIs. Catch the exception and use generic error messages via standard logging (`logging.error("API request failed")`) instead to fail securely.
## 2025-02-23 - Fix Sensitive Data Leakage in DAG exceptions
**Vulnerability:** Catching `Exception as e` and logging `e` directly via `logging.error(f"...: {e}")` exposes raw exception objects (which may include API keys, query parameters, stack traces, or other sensitive details) in DAG execution logs.
**Learning:** Binding and logging the raw Python exception object directly can result in sensitive system internals or credential leakage into persistent logs, increasing attack surface area or exposing authentication tokens.
**Prevention:** Do not log or print the raw `Exception` object (e.g. `except Exception as e:`). Instead, catch the generic exception (`except Exception:`) and log a static, generic error message (e.g., `logging.error("Execution failed for task")`).

## 2024-10-01 - Fix Command Injection risk via strict command allowlist
**Vulnerability:** While `shell=False` prevents shell operator chaining, passing untrusted input directly into `shlex.split()` allows the caller to control the target binary (`args[0]`). If input is user-controlled, arbitrary binaries can still be invoked.
**Learning:** `shell=False` + `shlex.split()` is insufficient if the user controls `args[0]`. It still carries a command injection risk by allowing the execution of unauthorized binaries.
**Prevention:** Do not attempt ad-hoc input sanitization or regex filtering. Always use a strict command allowlist to verify the base command (`args[0]`) before executing it via `subprocess`.

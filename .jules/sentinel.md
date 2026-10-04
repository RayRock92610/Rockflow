## 2024-10-23 - Fix Command Injection risk via strict command allowlist
**Vulnerability:** Insufficient input validation allowing arbitrary command execution. An attacker could bypass the `obey_rayrock_decree` denylist ("rm -rf" and "sudo") to run any binary with flags using the `content` field.
**Learning:** Denylists are ineffective against arbitrary execution context like `subprocess.check_output(shlex.split(content))`. Strict tokenization combined with a binary allowlist is required to prevent bypasses and directory traversal attacks. Furthermore, preventing leakage of unhandled Python exception stack traces in logs limits information discovery by an attacker.
**Prevention:** Always use strict explicit allowlisting for executable tokens (`os.path.basename`) and forbid specific abuse vectors (e.g. `python -c` execution arguments).

## 2024-10-23 - Protect Against Unbounded Memory Allocation via External APIs
**Vulnerability:** Invoking `requests.get()` without `stream=True` directly fetches external data (e.g. `r.json()`) leading to unbounded memory allocation if the remote payload is excessively large or infinite, which risks Denial-of-Service (DoS) and potential system crashes.
**Learning:** External API dependencies should be treated as untrusted input. Consuming unbounded network data using `r.json()` or `r.content` is insecure in automated environments.
**Prevention:** For any Python `requests` HTTP calls, use `stream=True` and manually iterate over contents using `iter_content(chunk_size)`. Implement a maximum bounds check on the accumulated byte size, raise errors if exceeded, and then decode bytes securely with `errors='replace'` before JSON processing.

## 2026-10-04 - Fix Swallowed Exceptions and Traceback Leakage Risk
**Vulnerability:** Completely swallowing exceptions hides operational and security-relevant failures (e.g. DoS, unhandled crashes) from system logs. Conversely, naive error handling can inadvertently leak stack traces, paths, and internal variables to logs.
**Learning:** To balance security with observability, do not completely swallow errors or leak full stack traces. Always capture the exception type internally to facilitate monitoring.
**Prevention:** Catch exceptions specifically and log the exception type securely (e.g., `logger.error("Failed due to %s", type(e).__name__)`) without using `exc_info=True`, `logging.exception()`, or directly logging `str(e)`. Add security comments to contextualize this approach.

## 2025-02-23 - Fix Missing Strict Timeout Tuples and Stream Bounding
**Vulnerability:** External requests lacked explicit tuple timeouts and strict size-bounded streaming, exposing workers to Denial of Service (DoS) attacks via TCP read hanging and out-of-memory errors on unvalidated response payloads.
**Learning:** Hardening `requests` requires BOTH explicit timeouts `timeout=(connect, read)` and size-bound streaming iteration of response bytes instead of simply loading `.json()` or `.content()`.
**Prevention:** Always enforce explicit timeout tuples (connect, read) and stream-bound external API payloads to 1MB maximum.

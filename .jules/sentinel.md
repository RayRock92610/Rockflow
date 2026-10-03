## 2024-10-23 - Fix Command Injection risk via strict command allowlist
**Vulnerability:** Insufficient input validation allowing arbitrary command execution. An attacker could bypass the `obey_rayrock_decree` denylist ("rm -rf" and "sudo") to run any binary with flags using the `content` field.
**Learning:** Denylists are ineffective against arbitrary execution context like `subprocess.check_output(shlex.split(content))`. Strict tokenization combined with a binary allowlist is required to prevent bypasses and directory traversal attacks. Furthermore, preventing leakage of unhandled Python exception stack traces in logs limits information discovery by an attacker.
**Prevention:** Always use strict explicit allowlisting for executable tokens (`os.path.basename`) and forbid specific abuse vectors (e.g. `python -c` execution arguments).

## 2024-10-23 - Protect Against Unbounded Memory Allocation via External APIs
**Vulnerability:** Invoking `requests.get()` without `stream=True` directly fetches external data (e.g. `r.json()`) leading to unbounded memory allocation if the remote payload is excessively large or infinite, which risks Denial-of-Service (DoS) and potential system crashes.
**Learning:** External API dependencies should be treated as untrusted input. Consuming unbounded network data using `r.json()` or `r.content` is insecure in automated environments.
**Prevention:** For any Python `requests` HTTP calls, use `stream=True` and manually iterate over contents using `iter_content(chunk_size)`. Implement a maximum bounds check on the accumulated byte size, raise errors if exceeded, and then decode bytes securely with `errors='replace'` before JSON processing.

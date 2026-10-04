import pytest
import os
import sys
from unittest.mock import patch, MagicMock

# Add dags to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'dags'))
from github_repo_monitor import github_repo_monitor

def test_get_repo_info_error_path(caplog):
    """
    Test the error path for get_repo_info to ensure it handles GitHub API failures gracefully
    and logs the exception securely without leaking sensitive information.
    """
    with patch('airflow.models.Variable.get') as mock_var_get:
        # Configure variables to not use DEMO_MODE
        def mock_get(key, default_var=None):
            if key == "GITHUB_TOKEN":
                return "real_fake_token"
            return "apache/airflow"

        mock_var_get.side_effect = mock_get

        # Mock Github API to raise an exception. It's imported locally in the task, so we patch the root module github.Github
        with patch('github.Github') as mock_github_class:
            mock_github_instance = mock_github_class.return_value
            # When get_repo is called, simulate an API failure
            mock_github_instance.get_repo.side_effect = Exception("Simulated API failure")

            # Load the dag and get the task callable
            dag = github_repo_monitor()
            task = dag.get_task('get_repo_info')

            # Extract the actual python function from the task
            # In Airflow 3/TaskFlow, it might be stored under python_callable or function
            func = getattr(task, 'python_callable', getattr(task, 'function', None))
            assert func is not None, "Could not find python callable on task"

            import logging
            with caplog.at_level(logging.ERROR):
                # Execute the function
                result = func()

                # Verify the fallback response
                assert result == {'name': 'error', 'mode': 'error'}

                # Verify secure logging (only logs exception type, not full trace)
                assert "GitHub API request failed due to Exception." in caplog.text
                assert "Simulated API failure" not in caplog.text # Ensure sensitive details aren't leaked in this specific log message

import os
import sys
from unittest.mock import MagicMock, patch

# Mock airflow before importing example_dag_basic
sys.modules['airflow'] = MagicMock()
sys.modules['airflow.operators'] = MagicMock()
sys.modules['airflow.operators.bash'] = MagicMock()
sys.modules['airflow.operators.python'] = MagicMock()

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'dags'))
from example_dag_basic import transform_data  # noqa: E402

def test_transform_data_happy_path():
    """Test that transform_data correctly returns status transformed."""
    # Given
    mock_context = {
        'ds': '2024-01-01',
        'run_id': 'test_run',
        'task_instance': MagicMock()
    }

    # When
    result = transform_data(**mock_context)

    # Then
    assert isinstance(result, dict)
    assert 'status' in result
    assert result['status'] == 'transformed'

def test_transform_data_empty_context():
    """Test transform_data with no context kwargs."""
    # When
    result = transform_data()

    # Then
    assert result == {'status': 'transformed'}

def test_transform_data_unexpected_kwargs():
    """Test transform_data can handle unexpected kwargs safely."""
    # When
    result = transform_data(unexpected_key="unexpected_value", another_key=123)

    # Then
    assert result == {'status': 'transformed'}

@patch('builtins.print')
def test_transform_data_output(mock_print):
    """Test that transform_data prints the expected string."""
    # When
    transform_data()

    # Then
    mock_print.assert_called_once_with("Transforming data...")

import pytest
from unittest.mock import patch, MagicMock
from dags.gemini_ai_pipeline import gemini_ai_pipeline

@patch('airflow.models.Variable.get')
@patch('google.generativeai.configure')
@patch('google.generativeai.GenerativeModel')
def test_analyze_with_gemini_error(mock_model, mock_configure, mock_variable_get):
    # Setup mock for API key
    mock_variable_get.return_value = 'FAKE_API_KEY'

    # Setup mock to raise an exception when generating content
    mock_model_instance = MagicMock()
    mock_model_instance.generate_content.side_effect = Exception("Mocked API Error")
    mock_model.return_value = mock_model_instance

    # We can just extract it from the globals or local scope if needed,
    # but the easiest is to just grab it from the dag's task dictionary.
    dag = gemini_ai_pipeline()

    # In Airflow 2, tasks are stored in dag.task_dict
    task = dag.task_dict['analyze_with_gemini']

    content = {
        'text': 'Apache Airflow is a workflow orchestration platform.',
        'timestamp': '2023-01-01T12:00:00'
    }

    # Call the python_callable
    if hasattr(task, 'python_callable'):
        result = task.python_callable(content)
    elif hasattr(task, 'function'):
        result = task.function(content)
    else:
        # Fallback to call it directly
        result = task(content)

    assert result == {'summary': 'Error occurred', 'mode': 'error'}

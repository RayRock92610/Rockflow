import logging
import os
import sys
from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

import pytest

# Ensure dags directory is in path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'dags'))

import gemini_ai_pipeline


@pytest.fixture
def analyze_func():
    dag = gemini_ai_pipeline.gemini_ai_pipeline()
    task = dag.get_task('analyze_with_gemini')
    return task.python_callable

def test_analyze_with_gemini_demo_mode(analyze_func):
    content = {
        'text': 'Test content',
        'timestamp': datetime.now(timezone.utc).isoformat()
    }
    with patch('dags.gemini_ai_pipeline.Variable.get', return_value='DEMO_MODE'), \
         patch.dict('sys.modules', {'google.generativeai': MagicMock()}):
        result = analyze_func(content)
        assert result['mode'] == 'demo'
        assert result['summary'] == 'Demo summary'

def test_analyze_with_gemini_error_path(analyze_func, caplog):
    content = {
        'text': 'Apache Airflow is a workflow orchestration platform.',
        'timestamp': datetime.now(timezone.utc).isoformat()
    }

    with patch('dags.gemini_ai_pipeline.Variable.get', return_value='fake_api_key'):
        # Mock sys.modules since it's imported locally
        mock_genai = MagicMock()
        mock_genai.configure.side_effect = Exception("API connection timeout")

        with patch.dict('sys.modules', {'google.generativeai': mock_genai}):
            with caplog.at_level(logging.ERROR):
                result = analyze_func(content)

            assert result['mode'] == 'error'
            assert result['summary'] == 'Error occurred'
            assert "Gemini API request failed due to Exception." in caplog.text

def test_analyze_with_gemini_happy_path(analyze_func):
    content = {
        'text': 'Apache Airflow is a workflow orchestration platform.',
        'timestamp': datetime.now(timezone.utc).isoformat()
    }

    with patch('dags.gemini_ai_pipeline.Variable.get', return_value='fake_api_key'):
        mock_genai = MagicMock()
        mock_model = MagicMock()
        mock_response = MagicMock()
        mock_response.text = "Summarized text from gemini-pro."
        mock_model.generate_content.return_value = mock_response
        mock_genai.GenerativeModel.return_value = mock_model

        with patch.dict('sys.modules', {'google.generativeai': mock_genai}):
            result = analyze_func(content)

            assert result['mode'] == 'api'
            assert result['summary'] == 'Summarized text from gemini-pro.'
            mock_genai.configure.assert_called_once_with(api_key='fake_api_key')
            mock_genai.GenerativeModel.assert_called_once_with('gemini-pro')
            mock_model.generate_content.assert_called_once_with("Summarize: Apache Airflow is a workflow orchestration platform.")

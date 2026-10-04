from datetime import datetime
from dags.example_dag_basic import extract_data

# 🛡️ Sentinel: Ensuring test coverage for regression detection.
def test_extract_data():
    result = extract_data()

    assert isinstance(result, dict)
    assert 'records' in result
    assert result['records'] == 100

    assert 'timestamp' in result
    # Check if timestamp is a valid ISO string
    try:
        datetime.fromisoformat(result['timestamp'])
    except ValueError:
        assert False, "timestamp is not a valid ISO 8601 string"

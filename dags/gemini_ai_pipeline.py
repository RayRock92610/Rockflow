"""
Gemini AI Pipeline
Demonstrates Google Gemini API integration
"""
from datetime import datetime

from airflow.decorators import dag, task
from airflow.models import Variable


@dag(
    dag_id='gemini_ai_pipeline',
    default_args={'owner': 'airflow', 'retries': 2},
    description='AI processing using Google Gemini API',
    schedule_interval='@daily',
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=['gemini', 'ai'],
)
def gemini_ai_pipeline():
    
    @task()
    def fetch_content():
        return {
            'text': 'Apache Airflow is a workflow orchestration platform.',
            'timestamp': datetime.now().isoformat()
        }
    
    @task()
    def analyze_with_gemini(content: dict):
        try:
            import google.generativeai as genai
            # 🛡️ Sentinel: Use strictly empty defaults for sensitive tokens instead of fallback strings to prevent accidental leakage or bypasses.
            api_key = Variable.get("GEMINI_API_KEY", default_var="")
            
            if not api_key:
                print("⚠️  DEMO MODE: Set GEMINI_API_KEY variable to use real API")
                return {'summary': 'Demo summary', 'mode': 'demo'}
            
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-pro')
            # 🛡️ Sentinel: Enforce network timeout
            response = model.generate_content(f"Summarize: {content['text']}", request_options={"timeout": 30})
            return {'summary': response.text, 'mode': 'api'}
        except Exception as err:
            import logging
            # 🛡️ Security note: Log the exception type securely without leaking full stack traces to outputs.
            logging.error("Gemini API request failed due to %s", type(err).__name__, exc_info=True)
            return {'summary': 'Error occurred', 'mode': 'error'}
    
    @task()
    def store_results(results: dict):
        print(f"Results: {results}")
        return {'status': 'success'}
    
    content = fetch_content()
    analysis = analyze_with_gemini(content)
    store_results(analysis)

gemini_ai_pipeline()

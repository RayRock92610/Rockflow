"""
Gemini AI Pipeline
Demonstrates Google Gemini API integration
"""
from datetime import datetime, timedelta
from airflow.decorators import dag, task
from airflow.models import Variable
import logging

logger = logging.getLogger(__name__)

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
            api_key = Variable.get("GEMINI_API_KEY", default_var="DEMO_MODE")
            
            if api_key == "DEMO_MODE":
                print("⚠️  DEMO MODE: Set GEMINI_API_KEY variable to use real API")
                return {'summary': 'Demo summary', 'mode': 'demo'}
            
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-pro')
            # Enforce connect and read timeouts (Sentinel 🛡️️)
            response = model.generate_content(
                f"Summarize: {content['text']}",
                request_options={"timeout": 30}
            )
            return {'summary': response.text, 'mode': 'api'}
        except Exception as err:
            logger.exception("Pipeline task execution failed: %s", type(err).__name__)
            raise RuntimeError("Pipeline task execution failed") from err
    
    @task()
    def store_results(results: dict):
        print(f"Results: {results}")
        return {'status': 'success'}
    
    content = fetch_content()
    analysis = analyze_with_gemini(content)
    store_results(analysis)

gemini_ai_pipeline()

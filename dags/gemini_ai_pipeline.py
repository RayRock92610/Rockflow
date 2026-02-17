"""
Gemini AI Pipeline
Demonstrates Google Gemini API integration
"""
from datetime import datetime, timedelta
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
            api_key = Variable.get("GEMINI_API_KEY", default_var="DEMO_MODE")
            
            if api_key == "DEMO_MODE":
                print("⚠️  DEMO MODE: Set GEMINI_API_KEY variable to use real API")
                return {'summary': 'Demo summary', 'mode': 'demo'}
            
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-pro')
            response = model.generate_content(f"Summarize: {content['text']}")
            return {'summary': response.text, 'mode': 'api'}
        except Exception as e:
            print(f"Error: {e}")
            return {'summary': 'Error occurred', 'mode': 'error'}
    
    @task()
    def store_results(results: dict):
        print(f"Results: {results}")
        return {'status': 'success'}
    
    content = fetch_content()
    analysis = analyze_with_gemini(content)
    store_results(analysis)

gemini_ai_pipeline()

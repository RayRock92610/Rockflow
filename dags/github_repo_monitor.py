"""
GitHub Repository Monitor
Demonstrates GitHub API integration
"""
from datetime import datetime, timedelta
from airflow.decorators import dag, task
from airflow.models import Variable

@dag(
    dag_id='github_repo_monitor',
    default_args={'owner': 'airflow', 'retries': 2},
    description='Monitor GitHub repositories',
    schedule_interval='@hourly',
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=['github', 'devops'],
)
def github_repo_monitor():
    
    @task()
    def get_repo_info():
        try:
            from github import Github
            token = Variable.get("GITHUB_TOKEN", default_var="DEMO_MODE")
            repo_name = Variable.get("GITHUB_REPO", default_var="apache/airflow")
            
            if token == "DEMO_MODE":
                print("⚠️  DEMO MODE: Set GITHUB_TOKEN variable to use real API")
                return {'name': repo_name, 'stars': 34500, 'mode': 'demo'}
            
            g = Github(token)
            repo = g.get_repo(repo_name)
            return {
                'name': repo.full_name,
                'stars': repo.stargazers_count,
                'forks': repo.forks_count,
                'open_issues': repo.open_issues_count,
                'mode': 'api'
            }
        except Exception as e:
            print(f"Error: {e}")
            return {'name': 'error', 'mode': 'error'}
    
    @task()
    def analyze_health(repo_info: dict):
        score = 100
        if repo_info.get('open_issues', 0) > 500:
            score -= 20
        print(f"Health score: {score}/100")
        return {'health_score': score, 'repo': repo_info['name']}
    
    @task()
    def send_report(health: dict):
        print(f"Report: {health}")
        return {'status': 'sent'}
    
    repo = get_repo_info()
    health = analyze_health(repo)
    send_report(health)

github_repo_monitor()

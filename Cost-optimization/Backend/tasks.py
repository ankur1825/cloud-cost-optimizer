from celery import Celery

app = Celery('tasks', broker='redis://localhost:6379/0')

@app.task
def scan_costs():
    # You can integrate the cost scanning logic here
    return "Cost scan completed"


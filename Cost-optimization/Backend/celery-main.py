from fastapi import FastAPI
from celery_worker import scan_costs

app = FastAPI()

@app.get("/scan_costs")
def trigger_cost_scan():
    scan_costs.apply_async()
    return {"message": "Cost scan triggered"}


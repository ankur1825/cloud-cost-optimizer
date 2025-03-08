from fastapi import FastAPI
from pydantic import BaseModel
import boto3
from botocore.exceptions import BotoCoreError, ClientError
from datetime import date

app = FastAPI()

# Request model
class CostRequest(BaseModel):
    service: str
    start_date: date
    end_date: date

# Root endpoint
@app.get("/")
def read_root():
    return {"message": "Cloud Cost Optimization API"}

# Function to get cost data from AWS Cost Explorer
def get_cost_data(request: CostRequest):
    client = boto3.client('ce')  # AWS Cost Explorer
    try:
        response = client.get_cost_and_usage(
            TimePeriod={'Start': str(request.start_date), 'End': str(request.end_date)},
            Granularity='MONTHLY',
            Metrics=['BlendedCost'],
            Filter={'Dimensions': {'Key': 'SERVICE', 'Values': [request.service]}}
        )
        
        cost = response['ResultsByTime'][0]['Total']['BlendedCost']['Amount']
        return {"service": request.service, "cost": f"${cost}"}
    
    except (BotoCoreError, ClientError) as e:
        return {"error": str(e)}

# Cost analysis endpoint
@app.post("/cost-analysis/")
def cost_analysis(request: CostRequest):
    return get_cost_data(request)

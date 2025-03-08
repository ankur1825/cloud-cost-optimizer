from fastapi import FastAPI
from pydantic import BaseModel
import boto3

app = FastAPI()

class CostRequest(BaseModel):
    service: str

@app.get("/")
def read_root():
    return {"message": "Cloud Cost Optimization API"}

@app.post("/cost-analysis/")
def cost_analysis(request: CostRequest):
    client = boto3.client('ce')  # AWS Cost Explorer
    response = client.get_cost_and_usage(
        TimePeriod={'Start': '2024-01-01', 'End': '2024-01-31'},
        Granularity='MONTHLY',
        Metrics=['BlendedCost'],
        Filter={'Dimensions': {'Key': 'SERVICE', 'Values': [service]}}
    )
    return {"service": request.service, "cost": "$100"}

#def get_cost_data(service):
#def get_cost_data(request: CostRequest):
#    client = boto3.client('ce')  # AWS Cost Explorer
#    response = client.get_cost_and_usage(
#        TimePeriod={'Start': '2024-01-01', 'End': '2024-01-31'},
#        Granularity='MONTHLY',
#        Metrics=['BlendedCost'],
#        Filter={'Dimensions': {'Key': 'SERVICE', 'Values': [service]}}
#    )
#    #return response['ResultsByTime'][0]['Total']['BlendedCost']['Amount']
#    return {"service": request.service, "cost": "$100"}	

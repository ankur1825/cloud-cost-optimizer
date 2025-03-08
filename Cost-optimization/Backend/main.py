from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import boto3
from botocore.exceptions import BotoCoreError, ClientError
from datetime import date
from typing import List
import datetime

app = FastAPI()

origins = [
    "http://localhost:3000",  # Frontend URL
    # Add other origins if needed
]

# Add CORS middleware to the FastAPI app
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Allow requests from the frontend
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],  # Allow all headers
)

class CostRequest(BaseModel):
    start_date: date
    end_date: date
    service: str = None  # Optional field for specific service

# Define the recommendation model
class Recommendation(BaseModel):
    service: str
    recommendation: str
    reason: str

# Thresholds
CPU_THRESHOLD = 3  # CPU < 3%
MEMORY_THRESHOLD = 3  # Memory < 3%
NETWORK_TRAFFIC_THRESHOLD = 300 * 1024 * 1024  # 300MB in bytes

# Initialize the boto3 clients for EC2 and CloudWatch
ec2_client = boto3.client('ec2', region_name='us-east-1')
sns_client = boto3.client('sns', region_name='us-east-1')
cloudwatch_client = boto3.client('cloudwatch', region_name='us-east-1')
SNS_TOPIC_ARN = 'arn:aws:sns:us-east-1:426946630837:test'

@app.get("/")
def read_root():
    return {"message": "Cloud Cost Optimization API"}

def get_cost_data(request: CostRequest):
    client = boto3.client('ce')  # AWS Cost Explorer

    try:
        if request.service:
            # Get cost for a specific service
            response = client.get_cost_and_usage(
                TimePeriod={'Start': str(request.start_date), 'End': str(request.end_date)},
                Granularity='MONTHLY',
                Metrics=['BlendedCost'],
                Filter={'Dimensions': {'Key': 'SERVICE', 'Values': [request.service]}}
            )
            cost = response['ResultsByTime'][0]['Total']['BlendedCost']['Amount']
            return [{"service": request.service, "cost": float(cost)}]

        else:
            # Get cost for all services
            response = client.get_cost_and_usage(
                TimePeriod={'Start': str(request.start_date), 'End': str(request.end_date)},
                Granularity='MONTHLY',
                Metrics=['BlendedCost'],
                GroupBy=[{'Type': 'DIMENSION', 'Key': 'SERVICE'}]
            )

            services_cost = []
            for result in response['ResultsByTime']:
                for group in result['Groups']:
                    service_name = group['Keys'][0]
                    cost = group['Metrics']['BlendedCost']['Amount']
                    services_cost.append({"service": service_name, "cost": float(cost)})

            return services_cost

    except (BotoCoreError, ClientError) as e:
        return {"error": str(e)}

# Function to fetch CloudWatch metrics
def get_metrics(instance_id, metric_name, period=300, stat='Average'):
    """
    Get the CloudWatch metrics for a given EC2 instance.
    """
    end_time = datetime.datetime.utcnow()
    start_time = end_time - datetime.timedelta(minutes=10)  # Check last 10 minutes

    response = cloudwatch_client.get_metric_statistics(
        Period=period,
        StartTime=start_time,
        EndTime=end_time,
        MetricName=metric_name,
        Namespace='AWS/EC2',
        Statistics=[stat],
        Dimensions=[{'Name': 'InstanceId', 'Value': instance_id}]
    )

    if response['Datapoints']:
        return response['Datapoints'][0][stat]
    return None

# Function to find idle EC2 instances
def get_idle_instances():
    idle_instances = []
    instance_metrics = []
    
    instances = ec2_client.describe_instances()

    for reservation in instances['Reservations']:
        for instance in reservation['Instances']:
            instance_id = instance['InstanceId']

            # Fetch CPU, Memory, and Network metrics
            cpu_utilization = get_metrics(instance_id, 'CPUUtilization')
            memory_utilization = get_metrics(instance_id, 'MemoryUtilization')  # Assuming custom metric
            network_in = get_metrics(instance_id, 'NetworkIn')
            network_out = get_metrics(instance_id, 'NetworkOut')

            # Check if the instance is idle based on thresholds
            if (cpu_utilization is not None and cpu_utilization < CPU_THRESHOLD and
                memory_utilization is not None and memory_utilization < MEMORY_THRESHOLD and
                network_in is not None and network_out is not None and
                (network_in + network_out) < NETWORK_TRAFFIC_THRESHOLD):
                idle_instances.append(instance_id)
                instance_metrics.append({
                    'instance_id': instance_id,
                    'cpu_utilization': cpu_utilization,
                    'memory_utilization': memory_utilization,
                    'network_in': network_in,
                    'network_out': network_out
                })
                print(f"Idle instance found: {instance_id}. Stopping it...")

                # Stop the instance
                ec2_client.stop_instances(InstanceIds=[instance_id])
                print(f"Instance {instance_id} has been stopped.")

    return idle_instances

# Function to setup SNS Notification
def send_sns_notification(message: str):
    try:
        sns_client.publish(
            TopicArn=SNS_TOPIC_ARN,
            Message=message,
            Subject="AWS Cost Alert"
        )
    except Exception as e:
        print(f"Error sending SNS notification: {e}")    

# Simple optimization recommendations
def generate_recommendations(services_cost: List[dict]):
    recommendations = []
    
    for service in services_cost:
        if service['service'] == 'EC2':
            # Example: If EC2 cost is high and usage is low, recommend stopping/downsizing instances
            if service['cost'] > 2:  # Example threshold for high cost
                recommendations.append(Recommendation(
                    service="EC2",
                    recommendation="Consider downsizing EC2 instances.",
                    reason="High cost with potentially underutilized instances."
                ))
                send_sns_notification(f"ALERT: EC2 service cost is high: ${service['cost']}")

                # Check if EC2 instances are idle based on low usage (CPU, memory, network)
                idle_instances = get_idle_instances()
                
                if idle_instances:
                    recommendations.append(Recommendation(
                        service="EC2",
                        recommendation=f"Stop idle EC2 instances: {', '.join(idle_instances)}.",
                        reason="Instances are underutilized with low CPU, memory, and network traffic."
                    ))
                    send_sns_notification(f"ALERT: Instances are underutilized with low CPU, memory, and network traffic: ${service['cost']}")    

        elif service['service'] == 'S3':
            # Example: If S3 cost is high and usage is low, suggest review
            if service['cost'] > 500:  # Example threshold for high cost
                recommendations.append(Recommendation(
                    service="S3",
                    recommendation="Review unused S3 buckets.",
                    reason="High cost with low utilization."
                ))

        # Add more recommendations based on other services (Lambda, RDS, etc.)

    return recommendations

@app.post("/cost-analysis/")
async def cost_analysis(request: CostRequest):
    services_cost = get_cost_data(request)
    recommendations = generate_recommendations(services_cost)
    return {"cost_data": services_cost, "recommendations": recommendations}


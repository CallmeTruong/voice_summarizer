import boto3
from botocore.exceptions import ClientError
from datetime import datetime
import os

# Target DynamoDB specifically in Sydney
DYNAMODB_REGION = os.environ.get("DYNAMODB_REGION", "ap-southeast-2")
dynamodb = boto3.resource("dynamodb", region_name=DYNAMODB_REGION)
USERS_TABLE = "Users"

def lambda_handler(event, context):
    """
    Cognito Post Confirmation Trigger.
    Write record into DynamoDB when a user completes registration and verifies their email.
    """
    print(f"Cognito Event Triggered: {event['triggerSource']}")


    if event["triggerSource"] == "PostConfirmation_ConfirmSignUp":
        user_attributes = event["request"]["userAttributes"]
        user_id = user_attributes.get("sub")
        email = user_attributes.get("email", "")
        
        if not user_id:
            print("Error: No 'sub' found in user attributes.")
            return event
        
        try:
            table = dynamodb.Table(USERS_TABLE)
            table.put_item(
                
                Item={
                    "user_id": user_id,
                    "email": email,
                    "created_at": datetime.utcnow().isoformat() + "Z",
                    "total_files": 0,
                    "storage_used_bytes": 0,
                    "total_audio_duration": 0,
                },
                
                ConditionExpression="attribute_not_exists(user_id)"
            )
            print(f"Successfully provisioned DynamoDB record for user: {user_id}")
        
        except ClientError as e:
            if e.response['Error']['Code'] == 'ConditionalCheckFailedException':
                print(f"User {user_id} already exists in DynamoDB. Skipping insertion.")
            else:
                print(f"Failed to insert user into DynamoDB: {e}")
                

    return event
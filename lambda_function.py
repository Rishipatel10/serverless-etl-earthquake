import json
import os
from datetime import datetime
import boto3

# Initialize AWS clients
s3_client = boto3.client('s3')
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('clean_records') 

def lambda_handler(event, context):
    # Audit tracking metrics
    total_input_records = 0
    inserted_records = 0
    rejected_records = 0
    execution_timestamp = datetime.utcnow().isoformat()
    
    try:
        # 1. EXTRACT: Fetch bucket name and file key from the S3 trigger event
        bucket_name = event['Records'][0]['s3']['bucket']['name']
        file_key = event['Records'][0]['s3']['object']['key']
        print(f"Starting ETL execution for file: s3://{bucket_name}/{file_key}")
        
        # Read file from S3
        response = s3_client.get_object(Bucket=bucket_name, Key=file_key)
        geojson_content = json.loads(response['Body'].read().decode('utf-8'))
        
    except Exception as e:
        print(f"Extraction failed: {str(e)}")
        return {"status": "Error", "message": "Failed to extract file from S3"}

    # 2. TRANSFORM & LOAD
    features = geojson_content.get('features', [])
    total_input_records = len(features)
    
    for feature in features:
        try:
            properties = feature.get('properties', {})
            geometry = feature.get('geometry', {})
            
            # Extract basic data points
            record_id = feature.get('id') or properties.get('ids')
            mag = properties.get('mag')
            place = properties.get('place')
            raw_time = properties.get('time') # Epoch millisecond timestamp
            
            # Rule A: Remove/Reject invalid records (Transform Requirement)
            if not record_id or mag is None or raw_time is None:
                rejected_records += 1
                continue
                
            # Rule B: Standardize Field 1 (Convert epoch millisecond to readable UTC string)
            readable_date = datetime.utcfromtimestamp(raw_time / 1000.0).strftime('%Y-%m-%d %H:%M:%S UTC')
            
            # Rule C: Standardize Field 2 (Clean up whitespace and title-case the location text)
            clean_place = str(place).strip().title() if place else "Unknown Location"
            
            # Rule D: Add Derived Field (Calculate Severity from Magnitude)
            mag_float = float(mag)
            if mag_float >= 6.0:
                severity = "Major"
            elif mag_float >= 4.5:
                severity = "Moderate"
            else:
                severity = "Minor"
                
            # Extract geography details
            coordinates = geometry.get('coordinates', [0.0, 0.0])
            longitude = str(coordinates[0])
            latitude = str(coordinates[1])

            # Prepare structured DynamoDB payload
            item = {
                'record_id': str(record_id),          # Partition Key
                'place': clean_place,                 
                'magnitude': str(mag_float),
                'severity': severity,                 # Derived field
                'event_time': readable_date,          # Standardized field 1
                'longitude': longitude,
                'latitude': latitude,
                'processed_at': execution_timestamp
            }
            
            # 3. LOAD: Write payload to DynamoDB table
            table.put_item(Item=item)
            inserted_records += 1
            
        except Exception as row_error:
            print(f"Skipping row error processing item: {str(row_error)}")
            rejected_records += 1

    # 4. AUDIT: Log data metrics directly into CloudWatch logs
    audit_summary = {
        "timestamp": execution_timestamp,
        "total_input_records": total_input_records,
        "inserted_records": inserted_records,
        "rejected_records": rejected_records
    }
    print(f"AUDIT SUMMARY: {json.dumps(audit_summary)}")
    
    return {
        "statusCode": 200,
        "body": json.dumps(audit_summary)
    }
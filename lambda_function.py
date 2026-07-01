import json
import boto3
import os

# AWS Lambda Client
lambda_client = boto3.client("lambda")

# Dataset -> Lambda Mapping
ROUTES = {
    "earthquake": "EarthquakeLambda",
    "weather": "WeatherLambda",
    "product": "ProductLambda"
}

# Supported File Types
SUPPORTED_FILE_TYPES = {
    "json",
    "csv",
    "xml"
}


def lambda_handler(event, context):

    try:

        record = event["Records"][0]

        bucket = record["s3"]["bucket"]["name"]
        key = record["s3"]["object"]["key"]

        print("=" * 50)
        print(f"Bucket      : {bucket}")
        print(f"Object Key  : {key}")

        # Example:
        # raw/earthquake/data.json

        parts = key.split("/")

        if len(parts) < 3:

            return {
                "statusCode": 400,
                "body": "Invalid Folder Structure. Expected raw/<dataset>/<filename>"
            }

        folder = parts[0]
        dataset = parts[1]
        filename = parts[-1]

        print(f"Folder      : {folder}")
        print(f"Dataset     : {dataset}")
        print(f"Filename    : {filename}")

        # Validate folder
        if folder.lower() != "raw":

            return {
                "statusCode": 400,
                "body": "Files must be uploaded inside the raw/ folder."
            }

        # Validate dataset
        if dataset not in ROUTES:

            return {
                "statusCode": 400,
                "body": f"Unsupported Dataset : {dataset}"
            }

        # Detect extension
        extension = os.path.splitext(filename)[1].lower().replace(".", "")

        print(f"File Type   : {extension}")

        # Validate file type
        if extension not in SUPPORTED_FILE_TYPES:

            return {
                "statusCode": 400,
                "body": f"Unsupported File Type : {extension}"
            }

        lambda_name = ROUTES[dataset]

        print(f"Invoking Lambda : {lambda_name}")

        response = lambda_client.invoke(
            FunctionName=lambda_name,
            InvocationType="Event",
            Payload=json.dumps(event)
        )

        print(response)

        return {

            "statusCode": 200,

            "body": json.dumps({

                "message": "Lambda Invoked Successfully",

                "dataset": dataset,

                "file_type": extension,

                "target_lambda": lambda_name

            })

        }

    except Exception as e:

        print(f"Router Error : {str(e)}")

        return {

            "statusCode": 500,

            "body": json.dumps({

                "error": str(e)

            })

        }
import boto3
import pandas as pd
import io

# Create S3 Client
s3_client = boto3.client("s3")


def read_excel(bucket_name, file_key):
    """
    Read Excel file from S3 and return standardized records.
    Supports both .xlsx and .xls files.
    """

    try:

        response = s3_client.get_object(
            Bucket=bucket_name,
            Key=file_key
        )

        excel_data = response["Body"].read()

        df = pd.read_excel(io.BytesIO(excel_data))

        # Remove spaces from column names
        df.columns = [str(col).strip() for col in df.columns]

        # Replace NaN values with empty strings
        df = df.fillna("")

        records = df.to_dict(orient="records")

        print(f"Loaded {len(records)} records from Excel")

        return records

    except Exception as e:

        print(f"Excel Parser Error : {str(e)}")

        raise
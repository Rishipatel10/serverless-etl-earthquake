import csv
import boto3
import io

# Create S3 Client
s3_client = boto3.client("s3")


def read_csv(bucket_name, file_key):
    """
    Read CSV file from S3 and return standardized records.
    """

    try:

        response = s3_client.get_object(
            Bucket=bucket_name,
            Key=file_key
        )

        csv_content = response["Body"].read().decode("utf-8")

        reader = csv.DictReader(io.StringIO(csv_content))

        records = []

        for row in reader:

            # Remove leading/trailing spaces from column names
            clean_row = {
                str(key).strip(): value
                for key, value in row.items()
            }

            records.append(clean_row)

        print(f"Loaded {len(records)} records from CSV")

        return records

    except Exception as e:

        print(f"CSV Parser Error : {str(e)}")
        raise
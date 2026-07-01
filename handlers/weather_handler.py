import json

from parsers.json_parser import read_json
from parsers.csv_parser import read_csv
from parsers.xml_parser import read_xml

from utils.helper import get_file_extension
from utils.dynamodb import save_item


def lambda_handler(event, context):

    try:

        bucket_name = event["Records"][0]["s3"]["bucket"]["name"]
        file_key = event["Records"][0]["s3"]["object"]["key"]

        print(f"Processing Weather File : {file_key}")

        extension = get_file_extension(file_key)

        print(f"Detected File Type : {extension}")

        if extension == "json":
            records = read_json(bucket_name, file_key)

        elif extension == "csv":
            records = read_csv(bucket_name, file_key)

        elif extension == "xml":
            records = read_xml(bucket_name, file_key)

        else:
            raise Exception(f"Unsupported File Type : {extension}")

    except Exception as e:

        print(str(e))

        return {
            "statusCode": 500,
            "body": str(e)
        }

    inserted = 0
    rejected = 0

    for row in records:

        try:

            item = {

                "record_id": str(
                    row.get("record_id") or row.get("id")
                ),

                "city": str(
                    row.get("city", "")
                ),

                "temperature": str(
                    row.get("temperature", "")
                ),

                "humidity": str(
                    row.get("humidity", "")
                ),

                "processed_at": str(
                    row.get("processed_at", "")
                )

            }

            if save_item(item):

                inserted += 1

            else:

                rejected += 1

        except Exception as e:

            print(f"Weather Error : {str(e)}")

            rejected += 1

    return {

        "statusCode": 200,

        "body": json.dumps({

            "message": "Weather Data Processed",

            "inserted": inserted,

            "rejected": rejected

        })

    }
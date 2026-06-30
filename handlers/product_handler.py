import json

from parsers.json_parser import read_json
from parsers.csv_parser import read_csv
from parsers.excel_parser import read_excel

from utils.helper import get_file_extension
from utils.dynamodb import save_item


def lambda_handler(event, context):

    try:

        bucket_name = event["Records"][0]["s3"]["bucket"]["name"]
        file_key = event["Records"][0]["s3"]["object"]["key"]

        print(f"Processing Product File : {file_key}")

        extension = get_file_extension(file_key)

        print(f"Detected File Type : {extension}")

        if extension == "json":
            records = read_json(bucket_name, file_key)

        elif extension == "csv":
            records = read_csv(bucket_name, file_key)

        elif extension in ["xlsx", "xls"]:
            records = read_excel(bucket_name, file_key)

        else:
            raise Exception(f"Unsupported File Type : {extension}")

    except Exception as e:

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

                "product_name": str(
                    row.get("product_name", "")
                ),

                "category": str(
                    row.get("category", "")
                ),

                "price": str(
                    row.get("price", "")
                )

            }

            if save_item(item):

                inserted += 1

            else:

                rejected += 1

        except Exception as e:

            print(f"Product Error : {str(e)}")

            rejected += 1

    return {

        "statusCode": 200,

        "body": json.dumps({

            "message": "Product Data Processed",

            "inserted": inserted,

            "rejected": rejected

        })

    }
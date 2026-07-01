import json
from datetime import datetime

from parsers.json_parser import read_json
from parsers.csv_parser import read_csv
from parsers.xml_parser import read_xml

from utils.helper import get_file_extension
from utils.dynamodb import save_item
from utils.logger import log_audit


def lambda_handler(event, context):

    total_input_records = 0
    inserted_records = 0
    rejected_records = 0

    execution_timestamp = datetime.utcnow().isoformat()

    try:

        bucket_name = event["Records"][0]["s3"]["bucket"]["name"]
        file_key = event["Records"][0]["s3"]["object"]["key"]

        print(f"Processing Earthquake File : {file_key}")

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

    total_input_records = len(records)

    for record in records:

        try:

            record_id = record.get("record_id")

            magnitude = record.get("magnitude")

            place = record.get("place")

            raw_time = record.get("time")

            longitude = record.get("longitude")

            latitude = record.get("latitude")

            if record_id is None or magnitude is None or raw_time is None:

                rejected_records += 1
                continue

            readable_time = datetime.utcfromtimestamp(
                int(raw_time) / 1000
            ).strftime("%Y-%m-%d %H:%M:%S UTC")

            clean_place = str(place).strip().title() if place else "Unknown"

            magnitude = float(magnitude)

            if magnitude >= 6:
                severity = "Major"
            elif magnitude >= 4.5:
                severity = "Moderate"
            else:
                severity = "Minor"

            item = {

                "record_id": str(record_id),

                "place": clean_place,

                "magnitude": str(magnitude),

                "severity": severity,

                "event_time": readable_time,

                "longitude": str(longitude),

                "latitude": str(latitude),

                "processed_at": execution_timestamp

            }

            if save_item(item):
                inserted_records += 1
            else:
                rejected_records += 1

        except Exception as e:

            print(f"Record Processing Error : {str(e)}")
            rejected_records += 1

    audit = {

        "timestamp": execution_timestamp,

        "total_input_records": total_input_records,

        "inserted_records": inserted_records,

        "rejected_records": rejected_records

    }

    log_audit(audit)

    return {

        "statusCode": 200,

        "body": json.dumps(audit)

    }
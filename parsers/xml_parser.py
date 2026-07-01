import boto3
import xml.etree.ElementTree as ET

s3_client = boto3.client("s3")


def read_xml(bucket_name, file_key):
    response = s3_client.get_object(
        Bucket=bucket_name,
        Key=file_key
    )

    xml_data = response["Body"].read().decode("utf-8")

    root = ET.fromstring(xml_data)

    records = []

    for record in root.findall("record"):

        item = {}

        for child in record:
            item[child.tag] = child.text

        records.append(item)

    print(f"Loaded {len(records)} records from XML")

    return records
import json
import boto3

# Create S3 client
s3_client = boto3.client("s3")


def read_json(bucket_name, file_key):
    """
    Read JSON file from S3 and return standardized records.
    Supports:
    1. USGS Earthquake GeoJSON
    2. Normal JSON array
    """

    try:

        response = s3_client.get_object(
            Bucket=bucket_name,
            Key=file_key
        )

        data = json.loads(
            response["Body"].read().decode("utf-8")
        )

        records = []

        # -------------------------------
        # CASE 1 : Earthquake GeoJSON
        # -------------------------------
        if "features" in data:

            for feature in data["features"]:

                properties = feature.get("properties", {})
                geometry = feature.get("geometry", {})

                coordinates = geometry.get("coordinates", [None, None])

                records.append({

                    "record_id": feature.get("id"),

                    "magnitude": properties.get("mag"),

                    "place": properties.get("place"),

                    "time": properties.get("time"),

                    "longitude": coordinates[0],

                    "latitude": coordinates[1]

                })

        # -------------------------------
        # CASE 2 : JSON Array
        # -------------------------------
        elif isinstance(data, list):

            records = data

        # -------------------------------
        # CASE 3 : Single JSON Object
        # -------------------------------
        elif isinstance(data, dict):

            records = [data]

        else:

            raise Exception("Unsupported JSON Structure")

        print(f"Loaded {len(records)} records from JSON")

        return records

    except Exception as e:

        print(f"JSON Parser Error : {str(e)}")

        raise
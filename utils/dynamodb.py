import os
import boto3

# Initialize DynamoDB Resource
dynamodb = boto3.resource("dynamodb")

# Read table name from Lambda Environment Variable
TABLE_NAME = os.getenv("DYNAMODB_TABLE", "clean_records")

table = dynamodb.Table(TABLE_NAME)


def save_item(item):
    """
    Save one record into DynamoDB.
    """

    try:

        table.put_item(Item=item)

        print(f"Successfully inserted record : {item.get('record_id', 'Unknown')}")

        return True

    except Exception as e:

        print(f"DynamoDB Error : {str(e)}")

        return False


def save_items(items):
    """
    Save multiple records using batch_writer.
    """

    inserted = 0

    try:

        with table.batch_writer() as batch:

            for item in items:

                batch.put_item(Item=item)

                inserted += 1

        print(f"Successfully inserted {inserted} records.")

        return inserted

    except Exception as e:

        print(f"Batch Insert Error : {str(e)}")

        return 0


def get_table_name():
    """
    Return current DynamoDB table name.
    """

    return TABLE_NAME
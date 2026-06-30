import os


# Supported Datasets
SUPPORTED_DATASETS = [
    "earthquake",
    "weather",
    "product"
]

# Supported File Types
SUPPORTED_FILE_TYPES = [
    "json",
    "csv",
    "xlsx",
    "xls"
]


def get_dataset(file_key):
    """
    Example:
    raw/earthquake/data.json

    Returns:
    earthquake
    """

    parts = file_key.split("/")

    if len(parts) >= 2:
        return parts[1].lower()

    return None


def get_file_extension(file_key):
    """
    Example:
    data.json

    Returns:
    json
    """

    return os.path.splitext(file_key)[1].replace(".", "").lower()


def get_filename(file_key):
    """
    Example:
    raw/earthquake/data.json

    Returns:
    data.json
    """

    return os.path.basename(file_key)


def validate_dataset(dataset):
    """
    Check whether dataset is supported.
    """

    return dataset in SUPPORTED_DATASETS


def validate_file_type(file_type):
    """
    Check whether file type is supported.
    """

    return file_type in SUPPORTED_FILE_TYPES


def get_parser_name(file_type):
    """
    Returns parser name based on extension.
    """

    parser_map = {
        "json": "JSON Parser",
        "csv": "CSV Parser",
        "xlsx": "Excel Parser",
        "xls": "Excel Parser"
    }

    return parser_map.get(file_type, "Unknown Parser")
"""Extracts the data and returns the root."""

import xml.etree.ElementTree as ET
from xml.etree import ElementTree
from io import BytesIO
from os import environ as ENV
from datetime import datetime

from boto3 import client
import pandas as pd
from dotenv import load_dotenv


def find_latest_filename(filenames: list[str]) -> str:
    """Returns the filepath of the most recently uploaded file."""
    dates = [datetime.strptime(filename.split(
        '_')[-1][:-4], '%d-%m-%y') for filename in filenames]
    recent = max(dates)
    recent = datetime.strftime(recent, '%d-%m-%y')
    return [filename for filename in filenames if recent in filename][0]


def get_object_names(s3_client, bucket_name: str, folder_name: str) -> list[str]:
    """Gets a list of files in the correct folder."""
    objects = s3_client.list_objects(Bucket=bucket_name)

    return [o["Key"] for o in objects["Contents"] if o["Key"]
            .startswith(folder_name) and o["Key"].endswith(".xml")]


def get_articles() -> list[ElementTree.Element]:
    """Returns a list of articles."""
    load_dotenv()
    bucket_name = ENV['INPUT_BUCKET_NAME']
    folder_name = ENV['FOLDER_NAME']
    s3 = client(service_name="s3",
                aws_access_key_id=ENV["AWS_ACCESS_KEY"],
                aws_secret_access_key=ENV["AWS_SECRET_ACCESS_KEY"])
    objects = get_object_names(s3, bucket_name, folder_name)
    filename = find_latest_filename(objects)
    tree_bytes = BytesIO()
    s3.download_fileobj(
        Bucket=bucket_name, Key=filename, Fileobj=tree_bytes)
    tree_bytes.seek(0)
    tree = ET.parse(tree_bytes)
    root = tree.getroot()
    articles = root.findall('PubmedArticle')
    return articles


def get_filepath() -> str:
    """Returns the file path for the file to be saved."""
    load_dotenv()
    bucket_name = ENV['INPUT_BUCKET_NAME']
    folder_name = ENV['FOLDER_NAME']
    s3 = client(service_name="s3",
                aws_access_key_id=ENV["AWS_ACCESS_KEY"],
                aws_secret_access_key=ENV["AWS_SECRET_ACCESS_KEY"])
    objects = get_object_names(s3, bucket_name, folder_name)
    filename = find_latest_filename(objects)
    filename = filename[:-4] + '.csv'
    return filename


def get_institutes() -> pd.DataFrame:
    """Returns a pd of institutes."""
    institutes = pd.read_csv(
        'https://sigma-resources-public.s3.eu-west-2.amazonaws.com/pharmazer/institutes.csv')
    return institutes


if __name__ == "__main__":
    pass

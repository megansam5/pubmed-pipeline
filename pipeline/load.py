"""Loads to dataframe into a csv."""
from io import BytesIO
from os import environ as ENV

from boto3 import client
import pandas as pd
from dotenv import load_dotenv


def load_to_csv(affiliations: pd.DataFrame, file_name: str) -> None:
    """Loads to dataframe to a csv."""
    affiliations.to_csv(f"data/{file_name}.csv", index=False)


def load_to_s3(affiliations: pd.DataFrame, file_name: str) -> None:
    """Uploads dataframe to s3 bucket."""
    affiliations_csv = BytesIO()
    affiliations.to_csv(affiliations_csv, index=False)
    affiliations_csv.seek(0)
    load_dotenv()
    bucket_name = ENV['OUTPUT_BUCKET_NAME']
    s3 = client(service_name="s3",
                aws_access_key_id=ENV["AWS_ACCESS_KEY"],
                aws_secret_access_key=ENV["AWS_SECRET_ACCESS_KEY"])
    s3.upload_fileobj(Fileobj=affiliations_csv,
                      Bucket=bucket_name, Key=file_name)


if __name__ == "__main__":
    pass

from io import BytesIO
from os import environ as ENV

from boto3 import client
import pandas as pd
from dotenv import load_dotenv


def load_to_s3() -> None:
    """Uploads dataframe to s3 bucket."""
    load_dotenv()
    bucket_name = ENV['INPUT_BUCKET_NAME']
    s3 = client(service_name="s3",
                aws_access_key_id=ENV["AWS_ACCESS_KEY"],
                aws_secret_access_key=ENV["AWS_SECRET_ACCESS_KEY"])
    s3.upload_file(Filename="../data/22-09-24_sjogren_syndrome.xml",
                   Bucket=bucket_name, Key='c13/megan/sjogren_syndrome_26-09-24.xml')


if __name__ == "__main__":
    load_to_s3()

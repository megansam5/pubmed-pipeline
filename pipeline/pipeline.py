"""The pipeline to extract, transform and load the data."""
from extract import get_articles, get_filepath
from transform import create_affiliations_dataframe, process_dataframe
from load import load_to_s3

if __name__ == "__main__":

    articles = get_articles()
    filename = get_filepath()
    df = create_affiliations_dataframe(articles)
    df = process_dataframe(df)
    load_to_s3(df, filename)

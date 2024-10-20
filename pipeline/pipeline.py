"""The pipeline to extract, transform and load the data."""
from time import perf_counter

from extract import get_articles, get_filepath
from transform import create_affiliations_dataframe, process_dataframe
from load import load_to_csv, load_to_s3

if __name__ == "__main__":
    step1 = perf_counter()
    articles = get_articles()
    filename = get_filepath()
    step2 = perf_counter()
    print(f'Time to extract: {step2 - step1}')
    df = create_affiliations_dataframe(articles)
    step3 = perf_counter()
    print(f'Time to create df: {step3 - step2}')
    df = process_dataframe(df)
    step4 = perf_counter()
    print(f'Time to process df: {step4 - step3}')
    # load_to_csv(df, 'clean_data_short')
    load_to_s3(df, filename)
    step5 = perf_counter()
    print(f'Time to load data: {step5 - step4}')
    print(f'Pipeline time: {step5 - step1}')

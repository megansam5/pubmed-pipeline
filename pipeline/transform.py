"""Transforms the data into a dataframe."""

import xml.etree.ElementTree as ET
import re
from functools import cache

import pandas as pd
import spacy
from pycountry import countries
import spacy.tokens
from rapidfuzz.process import extractOne
from rapidfuzz.fuzz import partial_ratio
from pandarallel import pandarallel

from extract import get_articles, get_institutes


def get_keywords(keyword_list: ET.Element) -> list[str] | None:
    """If there are keywords, returns a list of keywords."""
    if keyword_list is None:
        return None
    return [keyword.text for keyword in keyword_list.findall('Keyword')]


def get_meshes(mesh_list: ET.Element) -> list[str] | None:
    """If there are meshes, returns a list of meshes."""
    if mesh_list is None:
        return None
    return [mesh.get('UI') for mesh in mesh_list.findall("MeshHeading/DescriptorName")]


def get_article_details(article: ET.Element) -> dict:
    """Returns the details from the article."""
    article_details = {}
    article_details['title'] = article.findtext('.//ArticleTitle')
    article_details['year'] = article.findtext('.//PubDate/Year')
    article_details['pmid'] = article.findtext('.//PMID')
    article_details['keyword_list'] = get_keywords(
        article.find(".//KeywordList"))
    article_details['mesh_list'] = get_meshes(
        article.find(".//MeshHeadingList"))
    return article_details


def get_author_details(author: ET.Element) -> dict:
    """Returns the details from the author."""
    author_details = {}
    author_details['forename'] = author.findtext('ForeName')
    author_details['lastname'] = author.findtext('LastName')
    author_details['initials'] = author.findtext('Initials')

    return author_details


def get_email(affiliation: str) -> str | None:
    """Returns the email if there is one."""
    email_pattern = r"[\d\w]+\.?[\w\d]*\.?[\w\d]*@.*(?:\.)"
    match = re.search(email_pattern, affiliation)
    return match[0] if match is not None else None


def get_zipcode(affiliation: str) -> str | None:
    """Returns the zipcode if there is one."""
    american_pattern = r'\b\d{5}(?:[-\s]\d{4})?\b'
    canadian_pattern = r'\b[A-Za-z]\d[A-Za-z][ -]?\d[A-Za-z]\d\b'
    uk_pattern = r'\b[A-Z]{1,2}\d[A-Z\d]? ?\d[A-Z]{2}\b'
    match = re.search(
        f'{american_pattern}|{canadian_pattern}|{uk_pattern}', affiliation)

    return match[0] if match is not None else None


def get_affiliation_details(affiliation: str) -> dict:
    """Returns the details from the affiliation."""
    affiliation_details = {}
    affiliation_details['affiliation'] = affiliation
    affiliation_details['email'] = get_email(affiliation)
    affiliation_details['zipcode'] = get_zipcode(affiliation)

    return affiliation_details


def create_affiliations_dataframe(articles: list[ET.Element]) -> pd.DataFrame:
    """Creates a dataframe of affiliations."""
    result = []
    for article in articles:
        article_details = get_article_details(article)
        authors = article.findall(".//AuthorList/Author")
        for author in authors:
            author_details = get_author_details(author)
            affiliations = author.findall('AffiliationInfo/Affiliation')
            for affiliation in affiliations:
                affiliation_details = get_affiliation_details(
                    affiliation.text)
                full_details = article_details | author_details | affiliation_details
                result.append(full_details)

    df = pd.DataFrame(result)
    return df


@cache
def get_country(affiliation: str, nlp_model) -> str | None:
    """Returns the name of the country if found in pycountries.
    Here, it is more time to use fuzzy_search that get, but means more countries are found."""
    doc = nlp_model(affiliation)
    for e in reversed(doc.ents):
        if e.label_ == 'GPE':
            text = e.text
            if text == 'UK':
                text = 'GB'
            try:
                result = countries.search_fuzzy(text)
                return result[0].name
            except LookupError:
                continue
    return None


@cache
def get_institute(affiliation: str, institutes_tuples: tuple, nlp_model) -> str | None:
    """Returns the instutute if it is found in the grid dataframe."""
    doc = nlp_model(affiliation)
    for e in reversed(doc.ents):
        if e.label_ == 'ORG' or e.label_ == 'FAC':
            if e.text in institutes_tuples:
                return e.text
            fuzzyfound = extractOne(
                e.text, institutes_tuples, scorer=partial_ratio, score_cutoff=90)
            if fuzzyfound:
                return fuzzyfound[0]
    return None


@cache
def get_grid_identifier(institute: str, grid_tuple: tuple) -> str | None:
    """If there is an institute, returns the grid identifier."""
    if institute is None:
        return None
    for name, grid_id in grid_tuple:
        if name == institute:
            return grid_id
    return None


def process_dataframe(affiliations: pd.DataFrame) -> pd.DataFrame:
    """Adds country, institute and grid identifier."""
    pandarallel.initialize()
    nlp = spacy.load('en_core_web_sm')
    institutes = get_institutes()
    institutes_tuple = tuple(institutes['name'].to_list())
    grid_tuple = tuple(
        institutes[['name', 'grid_id']].itertuples(index=False, name=None))

    affiliations['country'] = affiliations['affiliation'].parallel_apply(
        lambda x: get_country(x, nlp))

    affiliations['institute'] = affiliations['affiliation'].parallel_apply(
        lambda x: get_institute(x, institutes_tuple, nlp))

    affiliations['grid_identifier'] = affiliations['institute'].parallel_apply(
        lambda x: get_grid_identifier(x, grid_tuple))

    return affiliations


if __name__ == '__main__':
    pass

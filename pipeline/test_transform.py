"""Tests for the transform.py file."""
import unittest
from unittest.mock import patch, MagicMock
import xml.etree.ElementTree as ET

import pandas as pd

from transform import (
    get_keywords,
    get_meshes,
    get_article_details,
    get_author_details,
    get_email,
    get_zipcode,
    get_affiliation_details,
    create_affiliations_dataframe,
    get_country,
    get_institute,
    get_grid_identifier,
    process_dataframe
)


class TestTransform(unittest.TestCase):
    def setUp(self):
        # Sample XML structure for testing
        self.article_xml = """<?xml version="1.0" encoding="UTF-8"?>
        <PubmedArticle>
            <ArticleTitle>Sample Article</ArticleTitle>
            <PubDate>
                <Year>2023</Year>
            </PubDate>
            <PMID>123456</PMID>
            <KeywordList>
                <Keyword>Keyword1</Keyword>
                <Keyword>Keyword2</Keyword>
            </KeywordList>
            <MeshHeadingList>
                <MeshHeading>
                    <DescriptorName UI="D001">
                        MeshTerm
                    </DescriptorName>
                </MeshHeading>
            </MeshHeadingList>
            <AuthorList>
                <Author>
                    <ForeName>John</ForeName>
                    <LastName>Doe</LastName>
                    <Initials>JD</Initials>
                    <AffiliationInfo>
                        <Affiliation>University of Sample, sample@university.edu</Affiliation>
                    </AffiliationInfo>
                </Author>
            </AuthorList>
        </PubmedArticle>"""
        self.article = ET.fromstring(self.article_xml)

    def test_get_keywords(self):
        keyword_list = self.article.find(".//KeywordList")
        keywords = get_keywords(keyword_list)
        self.assertEqual(keywords, ['Keyword1', 'Keyword2'])

    def test_get_meshes(self):
        mesh_list = self.article.find(".//MeshHeadingList")
        meshes = get_meshes(mesh_list)
        self.assertEqual(meshes, ['D001'])

    def test_get_article_details(self):
        article_details = get_article_details(self.article)
        expected_details = {
            'title': 'Sample Article',
            'year': '2023',
            'pmid': '123456',
            'keyword_list': ['Keyword1', 'Keyword2'],
            'mesh_list': ['D001']
        }
        self.assertEqual(article_details, expected_details)

    def test_get_author_details(self):
        author = self.article.find(".//Author")
        author_details = get_author_details(author)
        expected_details = {
            'forename': 'John',
            'lastname': 'Doe',
            'initials': 'JD'
        }
        self.assertEqual(author_details, expected_details)

    def test_get_email(self):
        affiliation = "University of Sample, sample@university.edu"
        email = get_email(affiliation)
        self.assertEqual(email, 'sample@university.edu')

    def test_get_zipcode(self):
        # Tests for various patterns
        us_zip = "12345"
        canadian_zip = "K1A 0B1"
        uk_zip = "W1A 1AA"
        self.assertEqual(get_zipcode(us_zip), '12345')
        self.assertEqual(get_zipcode(canadian_zip), 'K1A 0B1')
        self.assertEqual(get_zipcode(uk_zip), 'W1A 1AA')

    def test_get_affiliation_details(self):
        affiliation = "University of Sample, sample@university.edu"
        affiliation_details = get_affiliation_details(affiliation)
        expected_details = {
            'affiliation': affiliation,
            'email': 'sample@university.edu',
            'zipcode': None  # No zipcode in the test string
        }
        self.assertEqual(affiliation_details, expected_details)

    @patch('transform.get_article_details')
    @patch('transform.get_author_details')
    @patch('transform.get_affiliation_details')
    def test_create_affiliations_dataframe(self, mock_get_affiliation_details, mock_get_author_details, mock_get_article_details):
        mock_get_article_details.return_value = {
            'title': 'Sample Article',
            'year': '2023',
            'pmid': '123456',
            'keyword_list': ['Keyword1'],
            'mesh_list': ['D001']
        }
        mock_get_author_details.return_value = {
            'forename': 'John',
            'lastname': 'Doe',
            'initials': 'JD'
        }
        mock_get_affiliation_details.return_value = {
            'affiliation': 'University of Sample, sample@university.edu',
            'email': 'sample@university.edu',
            'zipcode': None
        }

        df = create_affiliations_dataframe([self.article])
        self.assertEqual(len(df), 1)
        self.assertIn('title', df.columns)
        self.assertIn('affiliation', df.columns)

    @patch('transform.spacy.load')
    def test_get_country(self, mock_spacy_load):
        mock_nlp = MagicMock()
        mock_spacy_load.return_value = mock_nlp
        mock_nlp.return_value.ents = [
            MagicMock(label_='GPE', text='Sample Country')]

        with patch('pycountry.countries.search_fuzzy') as mock_search_fuzzy:
            mock_country = MagicMock()
            mock_country.name = 'Sample Country'
            mock_search_fuzzy.return_value = [mock_country]
            country = get_country(
                "Some affiliation in Sample Country", mock_nlp)
            self.assertEqual(country, 'Sample Country')

    @patch('transform.spacy.load')
    def test_get_institute(self, mock_spacy_load):
        mock_nlp = MagicMock()
        mock_spacy_load.return_value = mock_nlp
        mock_nlp.return_value.ents = [
            MagicMock(label_='ORG', text='Sample Institute')]

        institutes_tuples = ('Sample Institute',)
        institute = get_institute(
            "Some affiliation at Sample Institute", institutes_tuples, mock_nlp)
        self.assertEqual(institute, 'Sample Institute')

    @patch('transform.get_institutes')
    def test_process_dataframe(self, mock_get_institutes):
        # Mocking the institute dataframe
        mock_get_institutes.return_value = pd.DataFrame(
            {'name': ['Sample Institute'], 'grid_id': ['GRID1234']})

        df = pd.DataFrame({
            'affiliation': ['University of Sample, sample@university.edu']
        })
        processed_df = process_dataframe(df)

        self.assertIn('country', processed_df.columns)
        self.assertIn('institute', processed_df.columns)
        self.assertIn('grid_identifier', processed_df.columns)


if __name__ == '__main__':
    unittest.main()

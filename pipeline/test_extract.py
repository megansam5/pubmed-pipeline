"""Tests for extract.py file."""
import unittest
from unittest.mock import patch, MagicMock
import xml.etree.ElementTree as ET

import pandas as pd

from extract import (
    find_latest_filename,
    get_object_names,
    get_articles,
    get_filepath,
    get_institutes,
)


class TestExtract(unittest.TestCase):
    @patch('extract.client')
    def test_get_object_names(self, mock_client):
        mock_s3 = MagicMock()
        mock_s3.list_objects.return_value = {
            'Contents': [
                {'Key': 'folder_name/file1.xml'},
                {'Key': 'folder_name/file2.xml'},
                {'Key': 'folder_name/file3.txt'},
            ]
        }
        mock_client.return_value = mock_s3

        bucket_name = "test_bucket"
        folder_name = "folder_name"

        result = get_object_names(mock_client(), bucket_name, folder_name)

        self.assertEqual(
            result, ['folder_name/file1.xml', 'folder_name/file2.xml'])

    def test_find_latest_filename(self):
        filenames = [
            'file_01-01-23.xml',
            'file_01-02-23.xml',
            'file_01-03-23.xml',
        ]
        result = find_latest_filename(filenames)
        self.assertEqual(result, 'file_01-03-23.xml')

    @patch('extract.client')
    @patch('extract.get_object_names')
    @patch('extract.find_latest_filename')
    def test_get_articles(self, mock_find_latest_filename, mock_get_object_names, mock_client):
        mock_s3 = MagicMock()
        mock_client.return_value = mock_s3

        mock_get_object_names.return_value = ['folder_name/file_01-01-23.xml']
        mock_find_latest_filename.return_value = 'folder_name/file_01-01-23.xml'

        xml_content = """<?xml version="1.0" encoding="UTF-8"?>
        <PubmedArticleSet>
            <PubmedArticle>
                <MedlineCitation>
                    <Article>
                        <Journal>
                            <Title>Journal Title</Title>
                        </Journal>
                        <ArticleTitle>Article Title</ArticleTitle>
                    </Article>
                </MedlineCitation>
            </PubmedArticle>
        </PubmedArticleSet>"""

        from io import BytesIO
        tree_bytes = BytesIO(xml_content.encode('utf-8'))

        mock_s3.download_fileobj.side_effect = lambda Bucket, Key, Fileobj: Fileobj.write(
            tree_bytes.getvalue())

        articles = get_articles()

        self.assertEqual(len(articles), 1)
        self.assertIsInstance(articles[0], ET.Element)

    @patch('extract.load_dotenv')
    @patch('extract.get_object_names')
    @patch('extract.find_latest_filename')
    def test_get_filepath(self, mock_find_latest_filename, mock_get_object_names, mock_load_dotenv):
        mock_get_object_names.return_value = ['folder_name/file_01-01-23.xml']
        mock_find_latest_filename.return_value = 'folder_name/file_01-01-23.xml'

        result = get_filepath()
        self.assertEqual(result, 'folder_name/file_01-01-23.csv')

    @patch('extract.pd.read_csv')
    def test_get_institutes(self, mock_read_csv):
        mock_read_csv.return_value = pd.DataFrame(
            {'Institute': ['Institute1', 'Institute2']})

        result = get_institutes()
        self.assertEqual(len(result), 2)
        self.assertIn('Institute', result.columns)


if __name__ == '__main__':
    unittest.main()

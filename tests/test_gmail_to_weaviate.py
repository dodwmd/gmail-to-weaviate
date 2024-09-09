import pytest
import weaviate
from unittest.mock import Mock, patch
from gmail_to_weaviate import (
    get_gmail_service,
    create_weaviate_schema,
    fetch_emails,
    add_to_weaviate,
    get_subject,
    get_body,
    get_sender,
    get_date
)


@pytest.fixture(scope="module")
def weaviate_client():
    return weaviate.Client("http://localhost:8080")


@pytest.fixture
def mock_gmail_service():
    return Mock()


def test_get_gmail_service():
    with patch('gmail_to_weaviate.Credentials') as mock_credentials, \
         patch('gmail_to_weaviate.build') as mock_build:
        mock_credentials.from_authorized_user_file.return_value = Mock()
        mock_build.return_value = Mock()

        service = get_gmail_service()

        assert service is not None
        mock_credentials.from_authorized_user_file.assert_called_once()
        mock_build.assert_called_once_with('gmail', 'v1', credentials=mock_credentials.from_authorized_user_file.return_value)


def test_create_weaviate_schema(weaviate_client):
    create_weaviate_schema()
    schema = weaviate_client.schema.get()
    assert any(class_obj['class'] == 'Email' for class_obj in schema['classes'])


def test_fetch_emails(mock_gmail_service, weaviate_client):
    mock_gmail_service.users().messages().list().execute.return_value = {
        'messages': [{'id': '123'}, {'id': '456'}]
    }
    mock_gmail_service.users().messages().get().execute.return_value = {
        'id': '123',
        'payload': {
            'headers': [
                {'name': 'Subject', 'value': 'Test Subject'},
                {'name': 'From', 'value': 'sender@example.com'},
                {'name': 'Date', 'value': 'Mon, 1 Jan 2023 12:00:00 +0000'}
            ],
            'body': {'data': 'VGVzdCBCb2R5'}  # Base64 encoded "Test Body"
        }
    }

    fetch_emails(mock_gmail_service, max_results=2)

    # Check if emails were added to Weaviate
    results = weaviate_client.query.get('Email', ['subject', 'sender']).do()
    assert len(results['data']['Get']['Email']) == 2


def test_add_to_weaviate(weaviate_client):
    email = {
        'id': '123',
        'payload': {
            'headers': [
                {'name': 'Subject', 'value': 'Test Subject'},
                {'name': 'From', 'value': 'sender@example.com'},
                {'name': 'Date', 'value': 'Mon, 1 Jan 2023 12:00:00 +0000'}
            ],
            'body': {'data': 'VGVzdCBCb2R5'}  # Base64 encoded "Test Body"
        }
    }

    add_to_weaviate(email)

    results = weaviate_client.query.get('Email', ['subject', 'sender']).with_where({
        'path': ['gmail_id'],
        'operator': 'Equal',
        'valueString': '123'
    }).do()
    assert len(results['data']['Get']['Email']) == 1
    assert results['data']['Get']['Email'][0]['subject'] == 'Test Subject'
    assert results['data']['Get']['Email'][0]['sender'] == 'sender@example.com'


def test_get_subject():
    email = {
        'payload': {
            'headers': [
                {'name': 'Subject', 'value': 'Test Subject'}
            ]
        }
    }
    assert get_subject(email) == 'Test Subject'


def test_get_body():
    email = {
        'payload': {
            'body': {'data': 'VGVzdCBCb2R5'}  # Base64 encoded "Test Body"
        }
    }
    assert get_body(email) == 'Test Body'


def test_get_sender():
    email = {
        'payload': {
            'headers': [
                {'name': 'From', 'value': 'Sender Name <sender@example.com>'}
            ]
        }
    }
    assert get_sender(email) == 'sender@example.com'


def test_get_date():
    email = {
        'payload': {
            'headers': [
                {'name': 'Date', 'value': 'Mon, 1 Jan 2023 12:00:00 +0000'}
            ]
        }
    }
    assert get_date(email) == '2023-01-01T12:00:00+00:00'

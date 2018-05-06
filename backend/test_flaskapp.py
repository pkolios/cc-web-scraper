from unittest import mock
from urllib.error import HTTPError

import pytest

from flaskapp import create_app


@pytest.fixture
def app():
    app = create_app()
    yield app


@pytest.fixture
def client(app):
    app.config['TESTING'] = True
    client = app.test_client()
    return client


def test_scraper_post_success(client):
    with mock.patch('scraper.scrape') as scrape_mock:
        scrape_mock.return_value = mock.Mock(
            html_version='<!doctype html>',
            title='test title',
            headings={'h1': ['H1'], 'h2': ['H2'], 'h3': [],
                      'h4': [], 'h5': ['H5'], 'h6': ['H6']},
            external_links=[],
            internal_links=[],
            inaccessible_links=[],
            login_form=True,
        )
        response = client.post('/scraper', json={'url': 'example.org'})
        assert response.status_code == 200
        scrape_mock.assert_called_once_with('http://example.org',
                                            loop=mock.ANY)
        assert response.json == {
            'external_links': [],
            'headings': {'h1': ['H1'],
                         'h2': ['H2'],
                         'h3': [],
                         'h4': [],
                         'h5': ['H5'],
                         'h6': ['H6']},
            'html_version': '<!doctype html>',
            'inaccessible_links': [],
            'internal_links': [],
            'login_form': True,
            'title': 'test title'
        }


def test_scraper_post_payload_errors(client):
    response = client.post('/scraper', json={})
    assert response.status_code == 400
    assert response.json == {'message': {'url': 'url cannot be blank'}}


@pytest.mark.parametrize("exception, code, message", [
    (HTTPError('http://example.org', 404, 'Not found', {}, mock.Mock()),
     404, 'Not found'),
    (HTTPError('http://example.org', 500, 'Server error', {}, mock.Mock()),
     500, 'Server error'),
    (ValueError(),
     'bad_url', 'Bad url'),
])
def test_scraper_post_request_errors(client, exception, code, message):
    with mock.patch('scraper.scrape') as scrape_mock:
        scrape_mock.side_effect = exception
        response = client.post('/scraper', json={'url': 'http://example.org'})
        assert response.status_code == 400
        assert response.json == {'code': code, 'message': message}

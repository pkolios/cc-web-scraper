import pytest
from socket import gaierror
from unittest import mock
from urllib.error import HTTPError, URLError

import scraper


# scraper.scrape unittests
def test_scrape_raises_bad_url():
    with pytest.raises(ValueError):
        scraper.scrape('bad_url')


def test_scrape_raises_http_error():
    with mock.patch('scraper.urlopen') as urlopen_mock:
        urlopen_mock.side_effect = HTTPError(
            'http://example.org', 404, 'Not found', {}, mock.Mock())
        with pytest.raises(HTTPError) as exc:
            scraper.scrape('http://example.org')
        assert exc.value.code == 404
        assert exc.value.msg == 'Not found'


def test_scrape_calls_page():
    with mock.patch('scraper.urlopen'):
        with mock.patch('scraper.Page') as page_mock:
            scraper.scrape('http://example.org')
            assert page_mock.called


# scraper.Page unittests
class MockResponse(object):
    def __init__(self, resp_data, code=200, msg='OK'):
        self.resp_data = resp_data
        self.code = code
        self.msg = msg
        self.headers = {'content-type': 'text/plain; charset=utf-8'}

    def read(self):
        return self.resp_data

    def getcode(self):
        return self.code


@pytest.fixture
def faulty_page_fixture():
    text = """
<html>
  <head>
  </head>
  <a>bad link 1</a>
  <form>
  </form>
</html>"""
    return MockResponse(text)


@pytest.fixture
def html5_page_fixture():
    text = """<!DOCTYPE html>
<html>
  <head>
    <title>Page title</title>
  </head>
  <h1>H1</h1>
  <h2>H2</h2>
  <h5>H5</h5>
  <h6>H6</h6>
  <a href="/test">test</a>
  <a href="http://example.org">test</a>
  <a href="#">test</a>
  <form>
    <input type="text" placeholder="Enter Username" name="uname" required>
    <input type="password" placeholder="Enter Password" name="psw" required>
    <button type="submit">Login</button>
  </form>
</html>"""
    return MockResponse(text)


@pytest.mark.parametrize("property, expected, page_fixture", [
    ('html_version', 'HTML', html5_page_fixture()),
    ('html_version', None, faulty_page_fixture()),
    ('title', 'Page title', html5_page_fixture()),
    ('title', None, faulty_page_fixture()),
    ('headings', {'h1': ['H1'], 'h2': ['H2'], 'h3': [],
                  'h4': [], 'h5': ['H5'], 'h6': ['H6']},
     html5_page_fixture()),
    ('headings', {'h1': [], 'h2': [], 'h3': [], 'h4': [], 'h5': [], 'h6': []},
     faulty_page_fixture()),
    ('external_links', ['http://example.org'], html5_page_fixture()),
    ('external_links', [], faulty_page_fixture()),
    ('internal_links', ['/test', '#'], html5_page_fixture()),
    ('internal_links', [], faulty_page_fixture()),
    ('login_form', True, html5_page_fixture()),
    ('login_form', False, faulty_page_fixture()),
])
def test_page_properties(property, expected, page_fixture):
    with mock.patch('scraper.urlopen'):
        page = scraper.Page('http://test.com/', page_fixture)
    assert getattr(page, property) == expected


def test_page_inaccessible_links(faulty_page_fixture):
    with mock.patch('scraper.urlopen'):
        page = scraper.Page('http://example.org/', faulty_page_fixture)

    with mock.patch('scraper.Page.external_links',
                    new_callable=mock.PropertyMock) as ex_links_mock:
        ex_links_mock.return_value = [
            'bad_url',
            'http://bad_url',
            'http://example.org',
            'http://example.org']  # To test removal of duplicates
        with mock.patch('scraper.urlopen') as urlopen_mock:
            errors = [
                ValueError("unknown url type: 'bad_url'",),
                URLError(gaierror(-2, 'Name does not resolve')),
                HTTPError('http://example.org', 404, 'Not found', {},
                          mock.Mock()),
            ]
            urlopen_mock.side_effect = errors
            inaccessible_links = page.inaccessible_links
            assert len(inaccessible_links) == 3
            for link in inaccessible_links:
                assert link['error'] in [str(error) for error in errors]

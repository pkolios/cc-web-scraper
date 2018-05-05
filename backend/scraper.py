import asyncio
import concurrent.futures
from urllib.parse import urljoin
from urllib.request import urlopen

import bs4


def _urlopen(url, timeout):
    """
    Extend urlopen to return a tuple of requested url and response
    or exception to use in futures
    """
    try:
        return (url, urlopen(url, timeout=timeout))
    except Exception as exc:
        return (url, exc)


async def fetch_links(links, max_workers, timeout, loop):
    responses = []
    with concurrent.futures.ThreadPoolExecutor(
            max_workers=max_workers) as executor:
        futures = [loop.run_in_executor(executor, _urlopen, link, timeout)
                   for link in links]
        for response in await asyncio.gather(*futures, return_exceptions=True):
            responses.append(response)

    return responses


class Page:
    """Wrap the BeautifulSoup object in a more convenient API"""
    def __init__(self, url, text, max_workers=20, timeout=5, loop=None):
        if loop:
            self._loop = loop
        else:
            self._loop = asyncio.get_event_loop()
        self.url = url
        self._max_workers = max_workers
        self._timeout = 5
        self._soup = bs4.BeautifulSoup(text, 'html.parser')

    @property
    def html_version(self):
        # TODO Return something nicer than just the doctype
        items = [item for item in self._soup.contents
                 if isinstance(item, bs4.Doctype)]
        try:
            return items[0].upper()
        except (AttributeError, IndexError):
            return None

    @property
    def title(self):
        try:
            return self._soup.title.string
        except AttributeError:
            return None

    @property
    def headings(self):
        """Return dict of headings count per heading tag"""
        heading_tags = ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']
        headings = {tag: self._soup.find_all(tag) for tag in heading_tags}
        for key in headings:
            headings[key] = [h.get_text() for h in headings[key]]
        return headings

    def _get_links(self):
        return self._soup.find_all('a')

    @property
    def external_links(self):
        """Return list of all links starting with 'http'"""
        return [link.get('href') for link in self._get_links()
                if isinstance(link.get('href'), str) and
                link.get('href').startswith('http')]

    @property
    def internal_links(self):
        """Return list of all links not starting with 'http'"""
        return [link.get('href') for link in self._get_links()
                if isinstance(link.get('href'), str) and
                link.get('href').startswith('http') is False]

    @property
    def inaccessible_links(self):
        """
        Merge internal and external links, fetch and check http code.
        Return list of dicts of links with erronous responses
        """
        links = self.external_links
        links.extend([urljoin(self.url, link) for link in self.internal_links])
        links = set(links)  # To avoid multiple checks of same url

        responses = self._loop.run_until_complete(fetch_links(
            links, self._max_workers, self._timeout, self._loop))
        errors = []
        for url, resp in responses:
            if isinstance(resp, Exception):
                errors.append({'url': url, 'error': str(resp)})

        return errors

    @property
    def login_form(self):
        """Return True if a login form with password input is found"""
        for form in self._soup.find_all('form'):
            for input_ in form.find_all('input'):
                if input_.get('type').lower() == 'password':
                    return True
        return False


def scrape(url, max_workers=20, timeout=5, loop=None):
    """
    Scrape the given url and return a Page object or raise HTTPError

    :param max_workers: Number of workers used when fetching inaccessible links
    :param timeout: Timeout in seconds when fetching links
    """
    text = urlopen(url, timeout=timeout)
    return Page(url, text, max_workers, timeout, loop)

import asyncio
import os
from urllib.error import HTTPError
from urllib.parse import urlparse

import envdir
from flask import Flask, current_app
from flask_restful import Resource, Api, abort, fields, marshal, reqparse
from werkzeug.contrib.cache import MemcachedCache

import scraper

loop = asyncio.get_event_loop()

parser = reqparse.RequestParser()
parser.add_argument('url', location='json', required=True,
                    help='url cannot be blank')

headings_fields = {
    'h1': fields.List(fields.String),
    'h2': fields.List(fields.String),
    'h3': fields.List(fields.String),
    'h4': fields.List(fields.String),
    'h5': fields.List(fields.String),
    'h6': fields.List(fields.String),
}
inaccessible_links_fields = {
    'url': fields.String,
    'error': fields.String,
}
page_fields = {
    'html_version': fields.String,
    'title': fields.String,
    'headings': fields.Nested(headings_fields),
    'external_links': fields.List(fields.String),
    'internal_links': fields.List(fields.String),
    'inaccessible_links': fields.List(fields.Nested(
        inaccessible_links_fields)),
    'login_form': fields.Boolean,
}


class Scraper(Resource):
    def _get_page(self, url):
        """Try cache before scraping url"""
        parsed_url = urlparse(url)
        if not parsed_url.scheme:
            url = f'http://{url}'
        cache = current_app.cache
        timeout = current_app.config.get('CACHE_TIMEOUT', '86400')
        if cache is None:
            page = scraper.scrape(url, loop=loop)
            return marshal(page, page_fields)

        cached_page = cache.get(url)
        if cached_page is None:
            page = scraper.scrape(url, loop=loop)
            cached_page = marshal(page, page_fields)
            cache.set(url, cached_page, timeout=int(timeout))
        return cached_page

    def post(self):
        args = parser.parse_args()
        try:
            return self._get_page(args['url'])
        except ValueError as exc:
            abort(400, code='bad_url', message='Bad url')
        except HTTPError as exc:
            abort(400, code=exc.code, message=exc.msg)


def setup_cache(app):
    app.cache = None
    servers = app.config.get('MEMCACHED_SERVERS')
    key_prefix = app.config.get('MEMCACHED_PREFIX')
    if servers:
        app.cache = MemcachedCache(servers=[servers], key_prefix=key_prefix)
        app.cache.set('sc-test', 'sc-value')


def create_app():
    app = Flask(__name__, instance_relative_config=True)
    with envdir.open(os.environ.get('ENVDIR')) as env:
        for key in env:
            app.config[key] = env[key]

    setup_cache(app)
    api = Api(app)
    api.add_resource(Scraper, '/scraper')
    return app

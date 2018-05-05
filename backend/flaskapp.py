import asyncio
from urllib.error import HTTPError

from flask import Flask
from flask_restful import Resource, Api, abort, fields, marshal, reqparse

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
    def post(self):
        args = parser.parse_args()
        try:
            page = scraper.scrape(args['url'], loop=loop)
        except ValueError as exc:
            abort(400, code='bad_url', message='Bad url')
        except HTTPError as exc:
            abort(400, code=exc.code, message=exc.msg)
        return marshal(page, page_fields)


def create_app():
    app = Flask(__name__, instance_relative_config=True)
    api = Api(app)
    api.add_resource(Scraper, '/scraper')
    return app

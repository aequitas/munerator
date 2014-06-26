"""Run HTTP REST API with live game data

Usage:
  munerator [options] restapi

Options:
  -v --verbose            Verbose logging
  -d --debug              Run in debug mode (autoreload)
  --http-listen ip:port   Host and port to have the HTTP server listen on [default: 0.0.0.0:8081]
  --database ip:port      Host and port for mongo database [default: 127.0.0.1:27017]

"""
import logging
import os

from docopt import docopt
from eve import Eve
from eve_mongoengine import EveMongoengine
from flask import current_app
from munerator.common.models import Games, Players, Votes

log = logging.getLogger(__name__)


def root():
    return current_app.send_static_file('index.html')


def main(argv):
    args = docopt(__doc__, argv=argv)

    host, port = args['--database'].split(':')

    # app settings
    my_settings = {
        'MONGO_HOST': host,
        'MONGO_PORT': int(port),
        'MONGO_DBNAME': 'munerator',
        'DOMAIN': {'eve-mongoengine': {}},
        'X_DOMAINS': '*',
        'X_HEADERS': '*',
        'API_VERSION': 1,
        'URL_PREFIX': 'api'
    }

    # setup flask app
    static_folder = os.path.join(os.path.dirname(__file__), 'static')
    app = Eve(static_folder=static_folder, static_url_path='', settings=my_settings)

    # setup eve mongodb database
    ext = EveMongoengine(app)

    # add models
    ext.add_model(Players, resource_methods=['GET'])
    ext.add_model(Games, resource_methods=['GET'])
    ext.add_model(Votes, resource_methods=['GET'])

    # register other urls
    app.route('/')(root)

    # run the app
    host, port = args['--http-listen'].split(':')
    app.run(host=host, port=int(port), debug=args['--debug'])

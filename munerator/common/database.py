from eve import Eve
from eve_mongoengine import EveMongoengine
from .models import Players, Games, Votes, Gamemaps


def setup_eve_mongoengine(host, port):
    # app settings
    my_settings = {
        'MONGO_HOST': host,
        'MONGO_PORT': int(port),
        'MONGO_PASSWORD': None,
        'MONGO_USERNAME': None,
        'MONGO_DBNAME': 'munerator',
        'DOMAIN': {'eve-mongoengine': {}},
    }
    app = Eve(settings=my_settings)

    # setup eve mongodb database
    ext = EveMongoengine(app)

    # add models
    ext.add_model([Players, Games, Votes, Gamemaps])

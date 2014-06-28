import mongomock
import mongoengine
import eve.io.mongo.mongo
import pytest


con = mongomock.Connection()
_db = con['default']


@pytest.fixture(scope='function')
def uuid():
    """
    Random id to be used in database tests.
    """
    import uuid
    return str(uuid.uuid4())


@pytest.yield_fixture(scope='function')
def db(monkeypatch):
    """
    Sets mongoengine db to mongomock db, drop all current documents.
    """
    monkeypatch.setitem(mongoengine.connection._dbs, 'default', _db)
    monkeypatch.setitem(mongoengine.connection._connections, 'default', con)

    def init_app(self, app):
        self.driver = {'db': _db}

    monkeypatch.setattr(eve.io.mongo.mongo.Mongo, 'init_app', init_app)

    for name, collection in _db._collections.items():
        collection.drop()

    yield _db

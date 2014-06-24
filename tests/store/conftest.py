import mongomock
import mongoengine
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

    for name, collection in _db._collections.items():
        collection.drop()

    yield _db

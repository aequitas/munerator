from munerator.store import handle_event, setup_eve_mongoengine


def test_add_player(db, uuid):
    data = {
        'id': uuid,
        'guid': uuid,
        'name': 'test'
    }
    handle_event('clientuserinfochanged', {'client_info': data}, None)

    player = db.players.find_one()
    assert player['name'] == data['name']
    assert data['guid'] in player['guids']


def test_update_player(db, uuid):
    data = {
        'id': uuid,
        'guid': uuid,
        'name': 'test'
    }
    handle_event('clientuserinfochanged', {'client_info': data}, None)

    player = db.players.find_one()
    assert player['name'] == data['name']

    data2 = {
        'id': uuid,
        'guid': uuid,
        'name': 'test2'
    }
    handle_event('clientuserinfochanged', {'client_info': data2}, None)

    player = db.players.find_one()

    assert player['name'] == data2['name']
    assert data['name'] in player['names']


def test_updated_created_fields(db, uuid):
    setup_eve_mongoengine('', 0)

    data = {
        'name': 'test'
    }
    handle_event('clientuserinfochanged', {'client_info': data}, None)

    player = db.players.find_one()

    assert player['_updated']
    assert player['_created']

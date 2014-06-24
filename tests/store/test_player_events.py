from munerator.store import handle_event


def test_add_player(db, uuid):
    data = {
        'id': uuid,
        'guid': uuid,
        'name': 'test'
    }
    handle_event('clientuserinfochanged', {'client_info': data})

    player = db.players.find_one()
    assert player['name'] == data['name']
    assert player['guid'] == data['guid']


def test_update_player(db, uuid):
    data = {
        'id': uuid,
        'guid': uuid,
        'name': 'test'
    }
    handle_event('clientuserinfochanged', {'client_info': data})

    player = db.players.find_one()
    assert player['name'] == data['name']

    data2 = {
        'id': uuid,
        'guid': uuid,
        'name': 'test2'
    }
    handle_event('clientuserinfochanged', {'client_info': data2})

    print list(db.players.find())
    player = db.players.find_one()

    assert player['name'] == data2['name']
    assert data['name'] in player['names']

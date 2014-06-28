import pytest
from munerator.context import GameContext
from mock import Mock


@pytest.fixture
def gc():
    gc = GameContext(Mock(), Mock(), Mock())
    return gc


def test_player_name_client_id_translation(gc):
    client_id = '1'
    player_name = 'testplayer'

    gc.clients = {
        client_id: {
            'name': player_name,
            'client_id': client_id
        }
    }

    data = {
        'kind': 'say',
        'player_name': player_name
    }

    contexted_data = gc.handle_event(data)

    assert contexted_data['client_id'] == client_id

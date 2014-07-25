from munerator.changer import Changer
from mock import Mock


def test_fraglimit_increase():
    in_socket = Mock()
    rcon_socket = Mock()

    data = {
        'game_info': {
            'fraglimit': 8,
            'num_players': 4
        }
    }

    c = Changer(in_socket, rcon_socket=rcon_socket)
    c.handle_event('clientbegin', data)
    c.handle_actions()
    rcon_socket.send_string.assert_called_once_with('set fraglimit 16')


def test_fraglimit_nochange():
    in_socket = Mock()
    rcon_socket = Mock()

    data = {
        'game_info': {
            'fraglimit': 16,
            'num_players': 4
        }
    }

    c = Changer(in_socket, rcon_socket=rcon_socket)
    c.handle_event('clientbegin', data)
    assert not rcon_socket.send_string.called


def test_fraglimit_nodegrade():
    in_socket = Mock()
    rcon_socket = Mock()

    data = {
        'game_info': {
            'fraglimit': 16,
            'num_players': 2
        }
    }

    c = Changer(in_socket, rcon_socket=rcon_socket)
    c.handle_event('clientbegin', data)
    assert not rcon_socket.send_string.called

import os
import time
import mock
from munerator.wrap import wrap


def test_event_sending(monkeypatch):
    monkeypatch.setattr(time, 'time', lambda: 123)

    in_socket = mock.Mock()

    game_output = os.path.join(os.path.dirname(__file__), 'game_output.txt')
    wrap(in_socket, 'cat %s' % game_output)

    with open(game_output) as f:
        logline = f.readline().strip()

    assert '123 ' + logline == in_socket.send_string.call_args_list[0][0][0]

import os
import time
import munerator.gamewrapper


def test_event_sending(monkeypatch):
    def timestamp():
        return 123

    monkeypatch.setattr(time, 'time', timestamp)

    game_output = os.path.join(os.path.dirname(__file__), 'game_output.txt')
    data = list()

    def emitter(line, timestamp):
        data.append((line.decode('utf-8'), timestamp))

    munerator.gamewrapper.wrap(emitter, 'cat %s' % game_output)
    with open(game_output) as f:
        logline = f.readline().strip()
    assert (logline, 123) in data

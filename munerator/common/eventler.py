import json
import logging

log = logging.getLogger(__name__)


class Eventler(object):
    """listen for events on zmq in socket"""
    def __init__(self, in_socket, **kwargs):
        self.in_socket = in_socket

        # set additional arguments
        for name, value in kwargs.items():
            setattr(self, name, value)

    def handle_events(self):
        while True:
            kind, data = self.in_socket.recv_string().split(' ', 1)
            log.debug('got %s: %s' % (kind, data))
            data = json.loads(data)

            self.handle_event(kind, data)

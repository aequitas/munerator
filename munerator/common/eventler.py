import json
import logging
import zmq
import time

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


class ThrottleEventler(Eventler):
    """like an eventler but keeps a register of actions to perform
    which it will execute at a set interval to allow throttling.
    """

    timeout = 5
    lastrun = 0
    actions = None

    def __init__(self, *args, **kwargs):
        super(ThrottleEventler, self).__init__(*args, **kwargs)

        self.actions = {}

    def handle_actions(self):
        """Run every action once"""
        for action, args in self.actions.items():
            log.debug('running action %s' % action)
            if hasattr(self, action):
                getattr(self, action)(*args[0], **args[1])
            else:
                log.warning('invalid action %s' % action)

        self.actions = {}

    def handle_events(self):
        while True:
            try:
                data = self.in_socket.recv_string(flags=zmq.NOBLOCK)
            except zmq.error.ZMQError:
                time.sleep(1)
                if time.time() > self.lastrun + self.timeout:
                    log.debug('handling actions')
                    self.lastrun = time.time()
                    self.handle_actions()
                continue

            kind, data = data.split(' ', 1)
            log.debug('got %s: %s' % (kind, data))
            data = json.loads(data)

            self.handle_event(kind, data)

"""Wrap game output

Usage:
  munerator [options] wrap <cmd>

Options:
  -v --verbose      Verbose logging
  --raw-socket url  ZMQ socket for raw logline [default: tcp://127.0.0.1:9000]

"""
from docopt import docopt
import zmq
import logging
log = logging.getLogger(__name__)

import time
from subprocess import Popen, PIPE


def wrap(socket, command):
    args = command.split()
    p = Popen(args, stdout=PIPE)

    while True:
        line = p.stdout.readline().decode('ascii')

        if line:
            msg = "%s %s" % (time.time(), line.strip())
            log.debug('sending: ' + msg)
            socket.send_string(msg)

        if not p.poll() is None:
            break


def main(argv):
    args = docopt(__doc__, argv=argv)

    context = zmq.Context()
    socket = context.socket(zmq.PUSH)
    socket.connect(args['--raw-socket'])

    wrap(socket, args['<cmd>'])

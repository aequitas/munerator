"""Send rcon commands to server

Usage:
  munerator [options] rcon

Options:
  -v --verbose         Verbose logging
  --rcon-socket url    ZMQ socket for rcon commands [default: tcp://127.0.0.1:9005]
  --oa-addr host       Host or ip where openarena runs [default: quake.brensen.com]
  --oa-port port       Port which openarena runs on [default: 1200]
  --rcon-passwd pass   Rcon password
  --raw-socket url     ZMQ socket for raw responses [default: tcp://127.0.0.1:9000]

"""
from docopt import docopt
import zmq
import json
import logging
log = logging.getLogger(__name__)
from vendor.pyquake3 import Administrator


def eventstream(zmq_socket, rcon_send_cmd, raw_socket):
    while True:
        cmd = zmq_socket.recv_string()
        response = rcon_send_cmd(str(cmd))
        log.debug('cmd:%s, response:%s' % (cmd, response))
        raw_socket.send_string(json.dumps(response))


def main(argv):
    args = docopt(__doc__, argv=argv)

    context = zmq.Context()
    zmq_socket = context.socket(zmq.PULL)
    zmq_socket.bind(args['--rcon-socket'])

    raw_socket = context.socket(zmq.PUSH)
    raw_socket.connect(args['--raw-socket'])

    rcon_connection = Administrator(args['--oa-addr'], int(args['--oa-port']), args['--rcon-passwd'])

    eventstream(zmq_socket, rcon_connection.rcon_command, raw_socket)

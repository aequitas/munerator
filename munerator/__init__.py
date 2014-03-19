"""Munerator

Usage:
  munerator [options] <command> [<args>...]

Commands:
    wrap <cmd>
    trans
    context
    ledbar
    old
    voting
    listen
    rcon
    help

Options:
  -v --verbose  Verbose logging
  -h --help     Show this screen.
  --version     Show version.

"""
from docopt import docopt

import pkg_resources
import logging
import importlib

version = pkg_resources.get_distribution("munerator").version


def main():
    args = docopt(__doc__, version=version, options_first=True)
    argv = [args['<command>']] + args['<args>']

    logging.basicConfig(level=logging.INFO)

    if '-v' in argv or '--verbose' in argv or args.get('--verbose'):
        logging.getLogger().setLevel(logging.DEBUG)
        logging.debug('debug logging enabled')

    module_name = 'munerator.' + args['<command>']
    app = importlib.import_module(module_name)
    app.main(argv)

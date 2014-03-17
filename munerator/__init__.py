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

    if '-v' in argv or '--verbose' in argv or args.get('--verbose'):
        logging.basicConfig(level=logging.DEBUG)
        logging.debug('debug logging enabled')

    module_name = 'munerator.' + args['<command>']
    app = importlib.import_module(module_name)
    app.main(argv)

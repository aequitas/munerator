"""Find assets (levelshot, images, etc)

Usage:
  munerator [options] assets

Options:
  -v --verbose          Verbose logging
  -f --force            Force refresh of all assets
  --database ip:port    Host and port for mongo database [default: 127.0.0.1:27017]

"""
import logging
import urllib2
import hashlib

from docopt import docopt
from munerator.common.database import setup_eve_mongoengine
from munerator.common.models import Gamemaps

log = logging.getLogger(__name__)


sources = {
    'levelshot': [
        'http://ws.q3df.org/images/levelshots/128x96/{mapname}.jpg',
        'http://gsdata.furver.se/thumbnails_quake3/{mapname}.jpg',
        'http://openarena.ws/svn/levelshots/{mapname}.jpg',
        'http://oa-community.com/map-manager/all/thumbnails/{mapname}.jpg',
    ],
    'images': [
        'http://ws.q3df.org/topview/{mapname}.jpg',
        'http://ws.q3df.org/images/levelshots/512x384/{mapname}.jpg',
        'http://gsdata.furver.se/levelshots_idtech3/{mapname}.jpg',
        'http://lvlworld.com/levels/{mapname}/{mapname}lg.jpg',
        'http://lvlworld.com/levels/map-{mapname}/map-{mapname}lg.jpg',
        'http://lvlworld.com/levels/{mapname}/{mapname}pan.jpg',

    ]
}

# hashes returned by server for not found images
notfoundhashes = [
    'dd2265645ae69a3c0f7b2f2340af18f0',
    '8d510c4aafcbf0238d56d84dfdad7a20',
    'b78ded5fb173185205e837ffa56c43e6',
]

default = 'http://ws.q3df.org/images/levelshots/512x384/'


def valid_asset(url):
    log.debug('url: %s' % url)
    try:
        response = urllib2.urlopen(url)
    except urllib2.HTTPError as e:
        response = e
        log.debug(response)

    if not response.code == 200:
        return False
    content = response.read()

    if not content:
        return False

    m = hashlib.md5()
    m.update(content)
    md5 = m.hexdigest()

    log.debug('hash: %s' % md5)

    if md5 in notfoundhashes:
        return False

    return True


def find_assets(force):
    if force:
        gamemaps = Gamemaps.objects()
    else:
        gamemaps = Gamemaps.objects(levelshot=None)

    for gamemap in gamemaps:
        log.debug('searching levelshot for %s' % gamemap.name)
        for source in sources['levelshot']:
            url = source.format(mapname=gamemap.name)
            if valid_asset(url):
                log.info('url %s, is valid, storing' % url)
                gamemap.update(set__levelshot=url)
                break
            else:
                log.debug('url %s is invalid' % url)
        else:
            # in case no levelshot is found
            gamemap.update(set__levelshot=default)

        for source in sources['images']:
            url = source.format(mapname=gamemap.name)
            if valid_asset(url):
                log.info('url %s, is valid, storing' % url)
                gamemap.update(add_to_set__images=url)
            else:
                log.debug('url %s is invalid' % url)


def main(argv):
    args = docopt(__doc__, argv=argv)

    # setup database
    host, port = args['--database'].split(':')
    setup_eve_mongoengine(host, port)

    # start search
    find_assets(force=args['--force'])

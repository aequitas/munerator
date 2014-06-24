===============================
munerator
===============================

.. image:: https://badge.fury.io/py/munerator.png
    :target: http://badge.fury.io/py/munerator

.. image:: https://travis-ci.org/aequitas/munerator.png?branch=master
        :target: https://travis-ci.org/aequitas/munerator

.. image:: https://pypip.in/d/munerator/badge.png
        :target: https://crate.io/packages/munerator


Munerator: Organizer of gladiatorial fights. (http://www.unrv.com/culture/gladiator.php)

Installing/Running
------------------

    pip install -e .

    munerator -h

To run the minimal stack:

    munerator trans &

    munerator context &
    
    munerator wrap "cat tests/game_output.txt"

Add -v for verbose output.


Modules
-------

Module overview: http://auth-83051f68-ec6c-44e0-afe5-bd8902acff57.cdn.spilcloud.com/10/1395159542_munerator.png

Event producers:
    - wrap: wrap game/command, capture output, send to translator
    - trans: translator, match incoming lines to regex, create event, send to context
    - context: add context to events, eg mapname, players, and broadcast events to subscribers

Listeners:
    - ledbar: subscribe to game events, show status on ledbar
    - old: subscribe to game events, proxy events to old api http://quake.ijohan.nl
    - listen: listen to all events sent out, for debugging etc.

Other:
    - rcon: interact with running game through rcon commands (change maps, say stuff)

Planned:
    - changer: change current game (fraglimit, gametype, instagib, restart) based on game info
    - voting: store player votes on maps/gameoption in db
    - rotate: rotate maps based on player preferences

Requirements
------------

- Python 2.7
- ZMQ
- OpenArena
- MongoDB

License
-------

MIT licensed. See the bundled `LICENSE <https://github.com/aequitas/munerator/blob/master/LICENSE>`_ file for more details.

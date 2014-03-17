===============================
munerator
===============================

.. image:: https://badge.fury.io/py/munerator.png
    :target: http://badge.fury.io/py/munerator

.. image:: https://travis-ci.org/aequitas/munerator.png?branch=master
        :target: https://travis-ci.org/aequitas/munerator

.. image:: https://pypip.in/d/munerator/badge.png
        :target: https://crate.io/packages/munerator?version=latest


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

- wrap: wrap game/command, capture output, send to translator
- trans: translator, match incoming lines to regex, create event, send to context
- context: add context to events, eg mapname, players, and broadcast events to subscribers

- ledbar: subscribe to game events, show status on ledbar
- old: subscribe to game events, proxy events to old api http://quake.ijohan.nl


Features
--------

* TODO

Requirements
------------

- Python >= 2.6 or >= 3.3

License
-------

MIT licensed. See the bundled `LICENSE <https://github.com/aequitas/munerator/blob/master/LICENSE>`_ file for more details.

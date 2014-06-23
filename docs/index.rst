.. munerator documentation master file, created by
   sphinx-quickstart on Fri Mar 21 22:51:53 2014.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to munerator's documentation!
=====================================

Contents:

.. toctree::
   :maxdepth: 2


Module overview
===============

.. blockdiag::

   diagram {
    openarena;
    logfiles [stacked];
    wrap [stacked];
    db [shape = flowchart.database];
    ember [ color = '#f23818', label = "EmberJS\nfrontend" ];
    theledbar [ label = 'Teh Ledbar'];

    openarena -> logfiles;

    logfiles -> wrap;

    wrap -> trans;
    trans -> context;
    context -> old, ledbar, listen, changer, store, restapi;

    group {
        ledbar -> theledbar;
    }
    
    group {
        old -> quake.ijohan.nl;    
    }

    store -> db [dir = both];

    restapi -> ember [ label = http ];

    changer -> rcon;



    rcon -> openarena;
   }

Ledbar
======
    .. automodule:: munerator.ledbar
        :members:


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`


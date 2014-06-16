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
    store [shape = flowchart.database];

    openarena -> wrap -> trans -> context -> ledbar;
    context -> old;
    context -> listen;
    context -> changer;
    context -> voting;
    context -> rotate;
    rcon -> openarena;

    changer -> rcon;
    rotate -> rcon;

    voting -> store [dir = both];
    rotate -> store [dir = both];

    context -> restapi;

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


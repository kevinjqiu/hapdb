hapdb
=====

.. image:: https://img.shields.io/pypi/v/hapdb.svg
    :target: https://pypi.python.org/pypi/hapdb
    :alt: Latest PyPI version

.. image:: https://travis-ci.org/kevinjqiu/hapdb.png
   :target: https://travis-ci.org/kevinjqiu/hapdb
   :alt: Latest Travis CI build status

Build a database table from haproxy logs

Usage
-----

``hapdb`` is a command line tool to convert your haproxy logs to a sqlite database so you can run sql queries against them.


To import haproxy logs:

    hapdb new /path/to/haproxy.log

A sqlite database will be created at /path/to/haproxy.log.sqlite. You can use the sqlite shell to interact with it::

    sqlite3 /path/to/haproxy.log.sqlite


Installation
------------

To install::

    pip install hapdb

Requirements
^^^^^^^^^^^^

- sqlite3
- python (2 or 3)

Compatibility
-------------

Licence
-------

MIT

Authors
-------

`hapdb` was written by `Kevin J. Qiu <kevin@idempotent.ca>`_.

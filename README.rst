ng
==

.. image:: https://img.shields.io/pypi/l/ng.svg
    :target: https://pypi.python.org/pypi/ng

.. image:: https://img.shields.io/pypi/v/ng.svg
    :target: https://pypi.python.org/pypi/ng

.. image:: https://img.shields.io/pypi/pyversions/ng.svg
    :target: https://pypi.python.org/pypi/ng

.. image:: https://travis-ci.org/cls1991/ng.svg?branch=master
    :target: https://travis-ci.org/cls1991/ng

Get password of the wifi you're connected, and your current ip address.

☤ Quickstart
------------

Get your ip address:

::

    $ ng ip
    `
    local_ip: 192.168.1.114
    public_ip: 49.4.160.250
    `

Get wifi password:

::

    $ ng wp
    $ ng wp flyfish_5g
    `
    flyfish_5g:hitflyfish123456
    `

☤ Installation
--------------

You can install "ng" via pip from `PyPI <https://pypi.python.org/pypi/ng>`_:

::

    $ pip install ng
	
☤ Usage
-------

::

    $ ng --help
    Usage: ng [OPTIONS] COMMAND [ARGS]...

      Get password of the wifi you're connected, and your current ip address.

    Options:
      --help  Show this message and exit.

    Commands:
      ip  Show ip address.
      wp  Show wifi password.

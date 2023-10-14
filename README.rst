*************************
xdgpspconf
*************************

**XDG** **P**\ latform **S**\ uited **P**\ roject **CONF**\ iguration

Gist
==========

Source Code Repository
---------------------------

|source| `Repository <https://gitlab.com/pradyparanjpe/xdgpspconf.git>`__

|pages| `Documentation <https://pradyparanjpe.gitlab.io/xdgpspconf>`__

Badges
---------

|Pipeline|  |Coverage|  |PyPi Version|  |PyPi Format|  |PyPi Pyversion|


Description
==============

Handle platform suited xdg-base to

- Read configuration from standard locations.

   - supported formats:
      - yaml
      - json
      - toml
      - conf (`ini <https://setuptools.pypa.io/en/latest/userguide/declarative_config.html#specifying-values>`__)

- Write configuration to most general, writable xdg-location
- Locate standard directories:
   - xdg_cache
   - xdg_config
   - xdg_data
   - xdg_state

XDG Specification
---------------------

View xdg specifications `here <https://specifications.freedesktop.org/basedir-spec/latest/ar01s03.html>`__.


What does it do
--------------------

- Lists possible xdg-locations (existing and prospective)

CACHE
~~~~~~~~~

``XDG_CACHE_HOME``

DATA
~~~~~~~
- ``XDG_DATA_HOME``
- ``XDG_DATA_DIRS``

STATE
~~~~~~~~
- ``XDG_STATE_HOME``
- ``XDG_STATE_DIRS``

CONFIG
~~~~~~~~

- Reads configuration files from standard Windows/POSIX locations, current folder and optionally all ancestors and custom locations.

Platform-specific 
^^^^^^^^^^^^^^^^^^^

Windows
""""""""""
- ``%LOCALAPPDATA%\<PROJECT>\config``
- ``%USERPROFILE%\AppData\Local\<PROJECT>\config``

POSIX
""""""""""

[Linux/MacOS]

- ``${XDG_CONFIG_HOME:-${HOME}/.config}/<PROJECT>/config``
- ``${XDG_CONFIG_HOME:-${HOME}/.config}/<PROJECT>``
- ``${XDG_CONFIG_HOME:-${HOME}/.config}/<PROJECT>rc``
- ``$DIR/<PROJECT>/config`` for each ``$DIR`` in ``$XDG_CONFIG_DIRS``

.. tip::

   Configuration file name 'config' is customizable.

Environment
-------------

- declared variable: ``%<PROJECT>RC%`` for Windows or ``$<PROJECT>`` for POSIX

Improper
-----------

- ``${HOME}/.<PROJECT>rc``

.. warning::

   This is disabled by default and deprecated, since it does not conform to XDG standards.

Custom
---------

- configuration path: supplied in function

Relative
---------

``./.<PROJECT>rc``

Ancestors
~~~~~~~~~~~

Any of the parents, till project root or mountpoint, that contains ``__init__.py``, where,

- project root is the directory that contains ``setup.cfg`` or ``setup.py``
- mountpoint is checked using ``pathlib.Path.drive`` on windows or ``pathlib.Path.is_mount()`` on POSIX


TODO
===========
- Implementation for following variables:
   - XDG_RUNTIME_DIR
   - `Other <https://www.freedesktop.org/software/systemd/man/pam_systemd.html>`__ XDG specifications.
   - Arbitrarily defined **XDG_.*** environment variables


.. |Pipeline| image:: https://gitlab.com/pradyparanjpe/xdgpspconf/badges/master/pipeline.svg

.. |source| image:: https://about.gitlab.com/images/press/logo/svg/gitlab-icon-rgb.svg
   :width: 50
   :target: https://gitlab.com/pradyparanjpe/xdgpspconf.git

.. |pages| image:: https://about.gitlab.com/images/press/logo/svg/gitlab-logo-gray-stacked-rgb.svg
   :width: 50
   :target: https://pradyparanjpe.gitlab.io/xdgpspconf

.. |PyPi Version| image:: https://img.shields.io/pypi/v/xdgpspconf
   :target: https://pypi.org/project/xdgpspconf/
   :alt: PyPI - version

.. |PyPi Format| image:: https://img.shields.io/pypi/format/xdgpspconf
   :target: https://pypi.org/project/xdgpspconf/
   :alt: PyPI - format

.. |PyPi Pyversion| image:: https://img.shields.io/pypi/pyversions/xdgpspconf
   :target: https://pypi.org/project/xdgpspconf/
   :alt: PyPi - pyversion

.. |Coverage| image:: https://gitlab.com/pradyparanjpe/xdgpspconf/badges/master/coverage.svg?skip_ignored=true

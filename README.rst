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
         - toml
         - conf (ini)
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

- Reads standard Windows/POSIX locations, current folder and optionally all ancestors and custom locations for xdg-configuration

   - Platform-specific locations:
      - Windows Locations: Environment Variable ``%LOCALAPPDATA%\<PROJECT>`` or ``%USERPROFILE%\AppData\Local\<PROJECT>``
      - POSIX [Linux/MacOS] Locations: Environment Variable ``$XDG_CONFIG_HOME/<PROJECT>`` or ``$HOME/.config/<PROJECT>``

   - Environment-declared variable: ``%<PROJECT>RC%`` for Windows or ``$<PROJECT>`` for POSIX
   - Custom configuration path: supplied in function
   - Relative path: ``$PWD/.<PROJECT>rc``

      - **Ancestors**: Any of the parents, till project root or mountpoint, that contains ``__init__.py``, where,

         - project root is the directory that contains ``setup.cfg`` or ``setup.py``
         - mountpoint is checked using ``pathlib.Path.drive`` on windows or ``pathlib.Path.is_mount()`` on POSIX

- Lists possible xdg-locations (existing and prospective)

   - ``XDG_CACHE_HOME`` is supported for cache locations
   - ``XDG_CONFIG_HOME``, ``XDG_CONFIG_DIRS`` are supported for configuration locations
   - ``XDG_DATA_HOME``, ``XDG_DATA_DIRS`` are supported for data locations
   - ``XDG_STATE_HOME``, ``XDG_STATE_DIRS`` are supported for state locations

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

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
   - Locate standard data directories


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

- Lists all possible data-locations (existing and prospective)

.. note::

   - ``XDG_CONFIG_HOME``, ``XDG_CONFIG_DIRS`` are supported for configuration locations
   - ``XDG_DATA_HOME``, ``XDG_DATA_DIRS`` are supported for data locations

.. warning::

   - ``XDG_STATE_HOME``, ``XDG_CACHE_HOME`` are **NOT** currently supported, and should be added in future.



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

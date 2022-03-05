#######
USAGE
#######

**********
SYNOPSIS
**********

.. argparse::
   :ref: xdgpspconf.command_line._cli
   :prog: xdgpspconf

**************
Module import
**************

Configuration
=================

Read/Write Configurations.

   - Read configurations declared at various locations by root (ADMIN), user (global, local), project (python only)

   - Write to the most global, yet **writable** location.


.. tabbed:: read

   .. code-block:: python
      :caption: read_config.py

      from pathlib import Path
      from xdgpspconf import ConfDisc
      from xdgpspconf.config_io import write_rc


      _NAME = Path(__file__).parent.name


      def parse_config(config):
          """Place-holder parser."""
          print(config)


      def read_std_config():
          """Read configuration from standard locations."""
          discoverer = ConfDisc(project=_NAME, shipped=__file__)
          for conf_file, config in discoverer.read_config(trace_pwd=True, cname='pref.yml').items():
              print(f'file: {conf_file}')
              parse_config(config)



.. tabbed:: write

   .. code-block:: python
      :caption: write_config.py

      from pathlib import Path
      from xdgpspconf import ConfDisc
      from xdgpspconf.config_io import write_rc


      _NAME = Path(__file__).parent.name

      def create_std_config(data: dict = {}):
          """Save configuraion at standard location"""
          discoverer = ConfDisc(project=_NAME, shipped=__file__)
          discoverer.write_config(data=data, force='overwrite')


.. tabbed:: write manually

   .. code-block:: python
      :caption: manual_config.py

      from pathlib import Path
      from xdgpspconf import ConfDisc
      from xdgpspconf.config_io import write_rc


      _NAME = Path(__file__).parent.name

      def update_std_config_manual(data: dict = {}):
          """Save configuraion at standard location"""
          discoverer = ConfDisc(project=_NAME, shipped=__file__)
          most_global = discoverer.safe_config(ext='yml', cname='pref')[-1]
          most_global.write_rc(data=data, config=conf_file, force='update')


DATA
==========

Access data folders.

.. tabbed:: readable

   .. code-block:: python
      :caption: readable_data_loc.py

      from pathlib import Path
      from xdgpspconf import DataDisc


      _NAME = Path(__file__).parent.name


      def readable_data():
          """
          Locate readable standard data locations

          allow discouraged ~/. locations
          """
          discoverer = DataDisc(project=_NAME, mode='r')
          discoverer.get_loc(improper=True)
          print('Readable data locations:')
          for loc in data_loc:
              print('-', loc)

.. tabbed:: writable

   .. code-block:: python
      :caption: writable_data.py

      from pathlib import Path
      from xdgpspconf import DataDisc


      _NAME = Path(__file__).parent.name


      def writable_data():
          """
          Locate writable standard data locations
          """
          discoverer = DataDisc(project=_NAME, mode='w')
          data_loc = discoverer.get_loc()
          print('Writable data locations:')
          for loc in data_loc:
              print('-', loc)


.. note::
   - Similarly, use for pre-defined bases:
      - cache
      - state


Other bases may be declared in ``~/.config/xdgpspconf/xdg.yml``
similar to ``<xdgpspconf>/xdg.yml``, where `<xdgpspconf>`
is the installation location of `xdgpspconf`: typically located at
``${HOME}/.local/lib/python<major>.<minor>/site-packages/xdgpspconf``.

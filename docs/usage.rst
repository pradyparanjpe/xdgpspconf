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

.. code-block:: python
   :caption: config.py

   from pathlib import Path
   from xdgpspconf import read_config


   _NAME = Path(__file__).parent.name


   def parse_config(config):
       """Place-holder parser."""
       print(config)


   def read_std_config():
       """Read configuration from standard locations."""
       for conf_file, config in read_config(_NAME, ancestors=True).items():
           print(f'file: {conf_file}')
           parse_config(config)

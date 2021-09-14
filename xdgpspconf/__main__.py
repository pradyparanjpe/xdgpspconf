#!/usr/bin/env python3
# -*- coding: utf-8; mode: python; -*-
# Copyright © 2020-2021 Pradyumna Paranjape
#
# This file is part of xdgpspconf.
#
# xdgpspconf is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# xdgpspconf is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with xdgpspconf. If not, see <https://www.gnu.org/licenses/>.
#
"""
Command-line Callable.

module executable script: python3 -m xdgpspconf
"""

from xdgpspconf import read_config
from xdgpspconf.command_line import cli


def main():
    """
    Execute.

    This executable is meant for useless testing.
    The main utility of this module is to use configurations
    which are returned by ``config.read_config``.
    """
    cli_args = cli()
    for conf_file, config in read_config(**cli_args).items():
        print(f'config file: {conf_file}')
        print('config:')
        print(config)
    return 0


if __name__ == '__main__':
    main()

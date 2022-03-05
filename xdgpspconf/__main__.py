#!/usr/bin/env python3
# -*- coding: utf-8; mode: python; -*-
# Copyright © 2021, 2022 Pradyumna Paranjape
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

from xdgpspconf import ConfDisc, BaseDisc
from xdgpspconf.command_line import cli


def main():
    """
    Execute.

    This executable is meant for useless testing.
    The main utility of this module is to use configurations
    which are returned by ``config.read_config``.
    """
    cli_args = cli()
    if cli_args['base'] != 'config':
        discoverer = BaseDisc(project=cli_args['project'],
                            base=cli_args['base'],
                            shipped=cli_args['shipped'],
                            mode=cli_args['mode'])
        for path in discoverer.get_loc(
                custom=cli_args.get('custom', None),
                trace_pwd=cli_args.get('trace_pwd', False),
                improper=cli_args.get('improper', False),
                mode=cli_args.get('mode', 0)):
            print('Path:', path)
    else:
        discoverer = ConfDisc(project=cli_args['project'],
                              shipped=cli_args['shipped'],
                              mode=cli_args['mode'])
        for config_file, config in discoverer.read_config(
                custom=cli_args.get('custom', None),
                trace_pwd=cli_args.get('trace_pwd', False),
                cname=cli_args.get('cname', 'config'),
                mode=cli_args.get('mode', 0)).items():
            print(f'{config_file = }')
            for key, value in config.items():
                print(f'{key}: {value}')

    return 0


if __name__ == '__main__':
    main()

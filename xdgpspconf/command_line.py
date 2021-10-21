#!/usr/bin/env python3
# -*- coding: utf-8; mode: python; -*-
# Copyright © 2021 Pradyumna Paranjape
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
Command line inputs
"""

from argparse import ArgumentParser, RawDescriptionHelpFormatter

from argcomplete import autocomplete


def _cli() -> ArgumentParser:
    """
    Parser for autodoc
    """
    parser = ArgumentParser(formatter_class=RawDescriptionHelpFormatter)
    # python bash/zsh completion
    parser.add_argument('-b',
                        '--base',
                        type=str,
                        default='config',
                        help='base-type sought',
                        choices=('cache', 'config', 'data', 'state'))
    parser.add_argument('-c',
                        '--custom',
                        type=str,
                        help='custom configuration path')
    parser.add_argument('-m',
                        '--mode',
                        type=str,
                        default='',
                        help='filter by permission mode',
                        choices=('', 'x', 'w', 'wx', 'r', 'rx', 'rw', 'rwx'))
    parser.add_argument('-n',
                        '--cname',
                        type=str,
                        default='config',
                        help='''Name of config file [default: config]
                        XDG_CONFIG_HOME/PROJECT/CNAME.(yml|toml|cfg)''')
    parser.add_argument('-e', '--ext', type=str, help='restrict to extensions')
    parser.add_argument('-t',
                        '--trace-pwd',
                        action='store_true',
                        help='inherit ancestoral path configurations')
    parser.add_argument('project',
                        type=str,
                        help='project whose configuration is sought')
    autocomplete(parser)
    return parser


def cli() -> dict:
    """
    Command line arguments
    """
    parser = _cli()
    return vars(parser.parse_args())

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
Test data locations
"""
import os
import sys
from pathlib import Path
from unittest import TestCase

from xdgpspconf.data import ancestral_data, locate_data, xdg_data


class TestData(TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_locations(self):
        proj = 'test'
        self.assertNotIn(Path('__file__/../..').resolve(), locate_data(proj))
        self.assertIn(
            Path('__file__/../..').resolve(),
            locate_data('test', ancestors=True))
        if sys.platform.startswith('win'):
            home = Path(os.environ['USER'])
            xdgconfig = Path(os.environ.get('APPDATA', home / 'AppData'))
        else:
            home = Path(os.environ['HOME'])
            xdgconfig = Path(os.environ.get('APPDATA', home / '.local/share'))
        self.assertIn(xdgconfig / proj, locate_data('test', ancestors=True))

    def test_ancestors(self):
        self.assertIn(
            Path(f'{__file__}/..').resolve(),
            ancestral_data(Path('.').resolve()))

    def test_local(self):
        if sys.platform.startswith('win'):
            home = Path(os.environ['USER'])
            xdgconfig = Path(os.environ.get('APPDATA', home / 'AppData'))
        else:
            home = Path(os.environ['HOME'])
            xdgconfig = Path(os.environ.get('APPDATA', home / '.local/share'))
        self.assertIn(xdgconfig, xdg_data())

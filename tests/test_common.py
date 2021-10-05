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
Test config locations
"""

import os
import sys
from pathlib import Path
from unittest import TestCase

from xdgpspconf.common import is_mount, locate_base, walk_ancestors


class TestMount(TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_root(self):
        self.assertTrue(is_mount(Path('/').resolve()))

    def test_nonroot(self):
        self.assertFalse(is_mount(Path('.').resolve()))


class TestAncestors(TestCase):
    ancestors = walk_ancestors(Path('.').resolve())

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_projroot(self):
        self.assertNotIn(Path(__file__).resolve().parent, self.ancestors)

    def test_projparent(self):
        self.assertIn(Path(__file__).resolve().parent.parent, self.ancestors)


class TestBase(TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_config(self):
        proj = 'test'
        self.assertNotIn(
            Path(__file__).resolve().parent.parent,
            locate_base(proj, base_type='config'))
        self.assertIn(
            Path(__file__).resolve().parent.parent,
            locate_base('test', ancestors=True, base_type='config'))
        if sys.platform.startswith('win'):
            home = Path(os.environ['USER'])
            xdgconfig = Path(os.environ.get('APPDATA', home / 'AppData'))
        else:
            home = Path(os.environ['HOME'])
            xdgconfig = Path(os.environ.get('APPDATA', home / '.config'))
        self.assertIn(xdgconfig / proj,
                      locate_base('test', ancestors=True, base_type='config'))

    def test_custom(self):
        proj = 'test'
        self.assertIn(
            Path(__file__).resolve().parent.parent,
            locate_base(proj,
                        custom=Path(__file__).resolve().parent.parent,
                        base_type='config'))
        self.assertRaises(FileNotFoundError,
                          locate_base,
                          proj,
                          custom=Path(__file__).resolve().parent / 'nofile',
                          base_type='config')

    def test_cache(self):
        proj = 'test'
        self.assertNotIn(
            Path('..').resolve(), locate_base(proj, base_type='cache'))
        self.assertIn(
            Path('..').resolve(),
            locate_base('test', ancestors=True, base_type='cache'))
        if sys.platform.startswith('win'):
            home = Path(os.environ['USERPROFILE'])
            xdgcache = Path(
                os.environ.get('APPDATA', home / 'AppData/Local/Temp'))
        else:
            home = Path(os.environ['HOME'])
            xdgcache = Path(os.environ.get('APPDATA', home / '.cache'))
        self.assertIn(xdgcache / proj,
                      locate_base('test', ancestors=True, base_type='cache'))

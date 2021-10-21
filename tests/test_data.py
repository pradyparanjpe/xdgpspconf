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
Test data locations
"""
import os
import sys
from pathlib import Path
from unittest import TestCase

from xdgpspconf import FsDisc


class TestData(TestCase):
    data_disc = FsDisc(project='test', base='data', shipped=Path(__file__))

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_locations(self):
        proj = 'test'
        self.assertNotIn(
            Path(__file__).resolve().parent.parent, self.data_disc.get_loc())
        self.assertIn(
            Path(__file__).resolve().parent.parent,
            self.data_disc.get_loc(trace_pwd=True))
        if sys.platform.startswith('win'):
            home = Path(os.environ['USER'])
            xdgconfig = Path(os.environ.get('APPDATA', home / 'AppData'))
        else:
            home = Path(os.environ['HOME'])
            xdgconfig = Path(os.environ.get('APPDATA', home / '.local/share'))
        self.assertIn(xdgconfig / proj, self.data_disc.get_loc(trace_pwd=True))

    def test_ancestors(self):
        self.assertIn(
            Path(__file__).resolve().parent,
            self.data_disc.trace_ancestors(Path('.').resolve()))
        self.assertIn(
            Path(__file__).resolve().parent.parent,
            self.data_disc.trace_ancestors(Path('.').resolve()))

    def test_local(self):
        if sys.platform.startswith('win'):
            home = Path(os.environ['USER'])
            xdgconfig = Path(os.environ.get('APPDATA', home / 'AppData'))
        else:
            home = Path(os.environ['HOME'])
            xdgconfig = Path(
                os.environ.get('APPDATA', home / '.local/share/test'))
        self.assertIn(xdgconfig, self.data_disc.user_xdg_loc())

    def test_custom(self):
        self.assertIn(
            Path(__file__).resolve().parent.parent,
            self.data_disc.get_loc(
                custom=Path(__file__).resolve().parent.parent))


class TestBase(TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_cache(self):
        FsDisc('test', base='cache', shipped=Path(__file__))

    def test_state(self):
        FsDisc('test', 'state', shipped=Path(__file__))

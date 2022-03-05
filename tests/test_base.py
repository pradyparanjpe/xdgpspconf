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

from xdgpspconf import CacheDisc, DataDisc, FsDisc, StateDisc
from xdgpspconf.base import XdgVar


class TestData(TestCase):

    def setUp(self):
        self.data_disc = DataDisc(project='test', shipped=Path(__file__))
        print(self.data_disc)

    def tearDown(self):
        pass

    def test_locations(self):
        proj = 'test'
        self.assertNotIn(
            Path(__file__).resolve().parent.parent, self.data_disc.get_loc())
        self.assertIn(
            Path(__file__).resolve().parent.parent,
            self.data_disc.get_loc(trace_pwd=True))
        self.assertEqual(self.data_disc.get_loc()[0],
                         self.data_disc.get_loc(dom_start=False)[-1])
        self.assertIn(Path().home() / '.test',
                      self.data_disc.get_loc(trace_pwd=True, improper=True))
        if sys.platform.startswith('win'):
            home = Path.home()
            xdgconfig = Path(os.environ.get('APPDATA', home / 'AppData'))
        else:
            home = Path.home()
            xdgconfig = Path(os.environ.get('APPDATA', home / '.local/share'))
        self.assertIn(xdgconfig / proj, self.data_disc.get_loc(trace_pwd=True))

    def test_ancestors(self):
        self.assertIn(
            Path(__file__).resolve().parent,
            self.data_disc.trace_ancestors(Path.cwd()))
        self.assertIn(
            Path(__file__).resolve().parent.parent,
            self.data_disc.trace_ancestors(Path.cwd()))

    def test_local(self):
        if sys.platform.startswith('win'):
            home = Path.home()
            xdgconfig = Path(os.environ.get('APPDATA', home / 'AppData'))
        else:
            home = Path.home()
            xdgconfig = Path(
                os.environ.get('APPDATA', home / '.local/share/test'))
        self.assertIn(xdgconfig, self.data_disc.user_xdg_loc())

    def test_custom(self):
        self.assertIn(
            Path(__file__).resolve().parent.parent,
            self.data_disc.get_loc(
                custom=Path(__file__).resolve().parent.parent))

    def test_safe_loc_w_trace(self):
        """
        check that locations are returned
        """
        self.data_disc.shipped = None
        data_locs = self.data_disc.safe_loc(trace_pwd=True)
        print(Path.cwd())
        print(data_locs)
        self.assertIn(Path.cwd(), data_locs)
        self.assertNotIn(Path('../setup.cfg').resolve(), data_locs)

    def test_safe_wo_trace(self):
        """
        check that locations are returned
        """
        data_locs = self.data_disc.safe_loc()
        self.assertNotIn(Path.cwd(), data_locs)
        self.assertNotIn(Path('../setup.cfg').resolve(), data_locs)


class TestBase(TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_cache(self):
        CacheDisc('test', shipped=Path(__file__))

    def test_state(self):
        StateDisc('test', shipped=Path(__file__))

    def test_setter_Xdg(self):
        disc = StateDisc('test', shipped=Path(__file__))
        _xdg = disc.xdg
        disc.xdg = _xdg


class TestErrors(TestCase):

    def test_xdg_nokey(self):
        """Handle non-recognised key"""
        with self.assertRaisesRegex(KeyError, 'is not a recognised key'):
            test_var = XdgVar(var='data')
            test_var.update({'my_data': 'some_data'})


class TestDeprecated(TestCase):

    def test_fsdisc_deprecated(self):
        with self.assertWarnsRegex(DeprecationWarning, 'FsDisc'):
            FsDisc(project='test')

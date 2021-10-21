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
Test config locations
"""

from pathlib import Path
from unittest import TestCase

from xdgpspconf import ConfDisc


class TestRead(TestCase):
    conf_disc = ConfDisc('test', Path(__file__), mode='w')

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_ancestors(self):
        """
        check that locations are returned
        """
        configs = self.conf_disc.read_config(trace_pwd=True)
        print(configs)
        self.assertIn(Path('./.testrc').resolve(), configs)

    def test_wo_ancestors(self):
        """
        check that locations are returned
        """
        configs = self.conf_disc.read_config()
        self.assertNotIn(Path('../setup.cfg').resolve(), configs)


class TestSafeConfig(TestCase):
    conf_disc = ConfDisc('test', Path(__file__), mode='w')

    def test_ancestors(self):
        """
        check that locations are returned
        """
        data_locs = self.conf_disc.safe_config(ext='.yml', trace_pwd=True)
        print(data_locs)
        self.assertIn(Path('./.testrc').resolve(), data_locs)
        self.assertNotIn(Path('../setup.cfg').resolve(), data_locs)

    def test_wo_ancestors(self):
        """
        check that locations are returned
        """
        data_locs = self.conf_disc.safe_config(ext='.yml')
        self.assertNotIn(Path('../setup.cfg').resolve(), data_locs)

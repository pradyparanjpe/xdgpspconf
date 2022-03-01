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


class TestConfig(TestCase):

    def setUp(self):
        self.conf_disc = ConfDisc('test', mode='w', shipped=__file__)
        print(self.conf_disc)

    def test_order(self):
        self.assertEqual(
            self.conf_disc.get_conf(dom_start=False)[0],
            self.conf_disc.get_conf()[-1])

    def test_conf(self):
        self.assertIn(
            Path('./.testrc').resolve(),
            self.conf_disc.get_conf(trace_pwd=True))
        self.assertNotIn(Path.home() / '.test/config.yml',
                         self.conf_disc.get_conf())
        self.assertIn(Path.home() / '.test/config.yml',
                      self.conf_disc.get_conf(improper=True))
        custom = Path('customconf.yml').resolve()
        self.assertIn(custom, self.conf_disc.get_conf(custom=custom))
        self.assertNotIn(custom, self.conf_disc.get_conf())

    def test_safe_w_trace(self):
        """
        check that locations are returned
        """
        self.conf_disc.shipped = None
        data_locs = self.conf_disc.safe_config(trace_pwd=True)
        print(Path('.').resolve())
        print(data_locs)
        self.assertIn(Path('./.testrc').resolve(), data_locs)
        self.assertNotIn(Path('../setup.cfg').resolve(), data_locs)

    def test_safe_wo_ancestors(self):
        """
        check that locations are returned
        """
        data_locs = self.conf_disc.safe_config(ext='.yml')
        self.assertNotIn(Path('../setup.cfg').resolve(), data_locs)


class TestRead(TestCase):

    def setUp(self):
        self.conf_disc = ConfDisc('test', __file__, mode='w')
        print(self.conf_disc)

    def tearDown(self):
        pass

    def test_ancestors(self):
        """
        check that locations are returned
        """
        configs = self.conf_disc.read_config(trace_pwd=True)
        print(configs)
        self.assertIn(Path('./.testrc').resolve(), configs)
        configs = self.conf_disc.read_config(trace_pwd=True, flatten=True)

    def test_wo_ancestors(self):
        """
        check that locations are returned
        """
        configs = self.conf_disc.read_config()
        self.assertNotIn(Path('../setup.cfg').resolve(), configs)


class TestWrite(TestCase):

    def setUp(self):
        self.conf_disc = ConfDisc('test', mode='w', shipped=__file__)
        print(self.conf_disc)

    def tearDown(self):
        pass

    def test_write(self):
        # permission error
        for ext in '.yml', '.toml', '.conf', None:
            conf_file = self.conf_disc.write_config({},
                                                    'update',
                                                    dom_start=True,
                                                    trace_pwd=True,
                                                    ext=ext)
            self.assertIsNotNone(conf_file)
            assert conf_file is not None
            try:
                # NEXT 3.8: missing_ok=``True``
                conf_file.unlink()
            except FileNotFoundError:
                pass

        self.conf_disc.shipped = None
        conf_file = self.conf_disc.write_config({},
                                                'update',
                                                dom_start=False,
                                                custom=Path.cwd())
        self.assertIsNotNone(conf_file)
        assert conf_file is not None
        try:
            # NEXT 3.8: missing_ok=``True``
            conf_file.unlink()
        except FileNotFoundError:
            pass

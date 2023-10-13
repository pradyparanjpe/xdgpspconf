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
"""Test config locations."""

from pathlib import Path
from unittest import TestCase

from xdgpspconf import ConfDisc
from xdgpspconf.config_io import parse_rc


class TestConfig(TestCase):

    def setUp(self):
        self.conf_disc = ConfDisc('test', mode='w', form=[], shipped=__file__)

    def test_order(self):
        self.assertEqual(
            self.conf_disc.get_conf(dom_start=False)[0],
            self.conf_disc.get_conf()[-1])

    def test_cname(self):
        """Custom config name."""
        self.assertEqual(
            self.conf_disc.get_conf(dom_start=False, cname='style')[0],
            self.conf_disc.get_conf(cname='style')[-1])

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
        """check that locations are returned."""
        self.conf_disc.shipped = None
        data_locs = self.conf_disc.safe_config(trace_pwd=True)
        print(Path('.').resolve())
        print(data_locs)
        self.assertIn(Path('./.testrc').resolve(), data_locs)
        self.assertNotIn(Path('../setup.cfg').resolve(), data_locs)

    def test_safe_wo_ancestors(self):
        """check that locations are returned."""
        data_locs = self.conf_disc.safe_config(ext='.yml')
        self.assertNotIn(Path('../setup.cfg').resolve(), data_locs)


class TestRead(TestCase):

    def setUp(self):
        self.conf_disc = ConfDisc('test', __file__, form=[], mode='w')
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
        config = self.conf_disc.flat_config(trace_pwd=True)
        print(configs)
        print(config)

    def test_wo_ancestors(self):
        """
        check that locations are returned
        """
        configs = self.conf_disc.read_config()
        self.assertNotIn(Path('../setup.cfg').resolve(), configs)


class TestWrite(TestCase):

    def setUp(self):
        self.conf_disc = ConfDisc('test', mode='w', form=[], shipped=__file__)
        self.data = self.conf_disc.flat_config(dom_start=True, trace_pwd=True)
        print(self.conf_disc)

    def tearDown(self):
        pass

    def test_write(self):
        # permission error
        for ext in '.yml', '.json', '.toml', None:  # , '.conf'
            print(ext)
            conf_file = self.conf_disc.write_config(self.data,
                                                    'update',
                                                    dom_start=True,
                                                    trace_pwd=True,
                                                    ext=ext)
            # retrieved = self.conf_disc.flat_config(trace_pwd=True, ext=ext)
            print(conf_file)
            print(conf_file.read_text())
            retrieved, _ = parse_rc(config=conf_file)
            self.assertEqual(self.data, retrieved)
            conf_file.unlink(missing_ok=True)

        self.conf_disc.shipped = None
        conf_file = self.conf_disc.write_config({},
                                                'update',
                                                dom_start=False,
                                                custom=Path.cwd())
        conf_file.unlink(missing_ok=True)

    def test_write_form(self):
        # permission error
        for form in 'yaml', 'json', 'toml', None:  # , 'ini'
            print(form)
            self.conf_disc.form = form
            conf_file = self.conf_disc.write_config(self.data,
                                                    'update',
                                                    dom_start=True,
                                                    trace_pwd=True)
            print(conf_file)
            print(conf_file.read_text())
            retrieved, _ = parse_rc(config=conf_file, form=form)
            conf_file.unlink(missing_ok=True)
            self.assertEqual(self.data, retrieved)


class TestIni(TestCase):

    def setUp(self):
        self.conf_disc = ConfDisc('test',
                                  mode='w',
                                  form='ini',
                                  shipped=__file__)
        self.data = {
            'Section': {
                'key-1': 'value1',
                'key-2': 'value2'
            },
            'Section-2': {
                'key-1': 'value3',
                'key-3': 'value1'
            }
        }

    def test_ini(self):
        conf_file = self.conf_disc.write_config(self.data,
                                                'update',
                                                dom_start=True,
                                                trace_pwd=True)
        retrieved, _ = parse_rc(config=conf_file, form=self.conf_disc.form)
        self.assertEqual(self.data, retrieved)
        conf_file.unlink(missing_ok=True)

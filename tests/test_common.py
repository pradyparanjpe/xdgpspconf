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

from xdgpspconf.base import is_mount


class TestMount(TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_root(self):
        self.assertTrue(is_mount(Path('/').resolve()))

    def test_nonroot(self):
        self.assertFalse(is_mount(Path('.').resolve()))

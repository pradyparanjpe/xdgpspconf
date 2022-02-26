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
XDG Platform Suited Project CONFiguration.

- Read project configurationn from standard locations

"""

from xdgpspconf.base import FsDisc
from xdgpspconf.config import ConfDisc

__version__ = '0!0.1.4'

__all__ = ['ConfDisc', 'FsDisc']

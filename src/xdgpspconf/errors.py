#!/usr/bin/env python3
# -*- coding: utf-8; mode: python; -*-
# Copyright © 2021-2023 Pradyumna Paranjape
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
"""xdgpspconf's defined errors."""

from pathlib import Path


class XdgpspConfError(Exception):
    """Base error for XdgpspConf(Exception)."""


class BadConf(XdgpspConfError):
    """Bad configuration format."""

    def __init__(self, config_file: Path, *args):
        super().__init__(f'Bad configuration in {config_file}\n', *args)


class FailedWriteError(XdgpspConfError):
    """
    Failed to write configuration.

    Either a safe configuration file path couldn't be determined OR
    All write-attempts failed.

    This error is be raised `from` the last failed attempt.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

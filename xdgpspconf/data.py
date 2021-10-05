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
# along with xdgpspconf. If not, see <https://www.gnu.org/licenses/>. #
"""
Locate standard data.

Read:
   - standard xdg-base locations
   - current directory and ancestors
   - custom location

"""

import os
from pathlib import Path
from typing import List

from xdgpspconf.common import locate_base, walk_ancestors, xdg_base


def ancestral_data(child_dir: Path) -> List[Path]:
    """
    Walk up to nearest mountpoint or project root.

       - collect all directories containing __init__.py
         (assumed to be source directories)
       - project root is directory that contains ``setup.cfg`` or ``setup.py``
       - mountpoint is a unix mountpoint or windows drive root
       - I am **NOT** my ancestor

    Args:
        child_dir: walk ancestry of `this`  directory

    Returns:
        List of Paths to ancestral source directories:
            First directory is most dominant
    """
    return walk_ancestors(child_dir)


def xdg_data() -> List[Path]:
    """
    Get XDG_DATA_HOME locations.

    `specifications
    <https://specifications.freedesktop.org/basedir-spec/latest/ar01s03.html>`__

    Returns:
        List of xdg-data Paths
            First directory is most dominant
    """
    return xdg_base('DATA')


def locate_data(project: str,
                custom: os.PathLike = None,
                ancestors: bool = False,
                py_bin: os.PathLike = None) -> List[Path]:
    """
    Locate data at standard locations.

    Args:
        project: name of project whose data is being fetched
        custom: custom location for data
        ancestors: inherit ancestor directories that contain __init__.py
        py_bin: namespace.__file__ that imports this function

    Returns:
        List of all possible data paths:
            Existing and non-existing
            First directory is most dominant

    """
    return locate_base(project, custom, ancestors, 'DATA', py_bin)

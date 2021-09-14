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
import sys
from pathlib import Path
from typing import List


def _is_mount(path: Path):
    """
    Check across platform if path is mountpoint or drive.

    Args:
        path: path to be checked
    """
    try:
        if path.is_mount():
            return True
        return False
    except NotImplementedError:
        if path.resolve().drive + '\\' == str(path):
            return True
        return False


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
    data_heir: List[Path] = []

    while not _is_mount(child_dir):
        if (child_dir / '__init__.py').is_file():
            data_heir.append(child_dir)
        if any((child_dir / setup).is_file()
               for setup in ('setup.cfg', 'setup.py')):
            # project directory
            data_heir.append(child_dir)
            break
        child_dir = child_dir.parent
    return data_heir


def xdg_data() -> List[Path]:
    """
    Get XDG_DATA_HOME locations.

    `specifications
    <https://specifications.freedesktop.org/basedir-spec/latest/ar01s03.html>`__

    Returns:
        List of xdg-data Paths
            First directory is most dominant
    """
    xdg_heir: List[Path] = []
    # environment
    if sys.platform.startswith('win'):  # pragma: no cover
        # windows
        user_home = Path(os.environ['USERPROFILE'])
        root_data = Path(os.environ['APPDATA'])
        xdg_data_home = Path(
            os.environ.get('LOCALAPPDATA', user_home / 'AppData/Local'))
        xdg_heir.append(xdg_data_home)
        xdg_heir.append(root_data)
    else:
        # assume POSIX
        user_home = Path(os.environ['HOME'])
        xdg_data_home = Path(
            os.environ.get('XDG_DATA_HOME', user_home / '.data'))
        xdg_heir.append(xdg_data_home)
        xdg_data_dirs = os.environ.get('XDG_DATA_DIRS',
                                       '/usr/local/share/:/usr/share/')
        for xdg_dirs in xdg_data_dirs.split(':'):
            xdg_heir.append(Path(xdg_dirs))
    return xdg_heir


def locate_data(project: str,
                custom: os.PathLike = None,
                ancestors: bool = False) -> List[Path]:
    """
    Locate data at standard locations.

    Args:
        project: name of project whose data is being fetched
        custom: custom location for data
        ancestors: inherit ancestor directories that contain __init__.py
        dname: name of data file

    Returns:
        List of all possible data paths:
            Existing and non-existing
            First directory is most dominant

    """
    # Preference of data location *Most dominant first*
    data_heir: List[Path] = []

    # custom
    if custom is not None:
        if not Path(custom).is_dir():
            raise FileNotFoundError(
                f'Custom data directory: {custom} not found')
        data_heir.append(Path(custom))

    # environment variable
    env_val = os.environ.get(project.upper() + '_DATA')
    if env_val is not None:
        if not Path(env_val).is_dir():
            raise FileNotFoundError(f'RC data directory: {env_val} not found')
        data_heir.append(Path(env_val))

    # Current directory
    current_dir = Path('.').resolve()
    data_heir.append(current_dir)

    if ancestors:
        # ancestral directories
        data_heir.extend(ancestral_data(current_dir))

    # xdg locations
    xdg_heir = xdg_data()
    for heir in xdg_heir:
        data_heir.append(heir / project)

    # Shipped location
    data_heir.append((Path(__file__).parent))

    return data_heir

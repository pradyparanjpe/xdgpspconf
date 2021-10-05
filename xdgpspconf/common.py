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
Common filesystem discovery functions.
"""

import os
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import List, Union


@dataclass
class XdgVar():
    win_root: str
    win_var: str
    win_default: str
    unix_root: Union[str, None]
    unix_var: str
    unix_vars: Union[str, None]
    unix_default: str


XDG_BASES = {
    'CACHE':
    XdgVar('TEMP', 'TEMP', 'AppData/Local/Temp', None, 'XDG_CACHE_HOME', None,
           '.cache'),
    'CONFIG':
    XdgVar('APPDATA', 'LOCALAPPDATA', 'AppData/Local', '/etc/xdg',
           'XDG_CONFIG_HOME', 'XDG_CONFIG_DIRS', '.config'),
    'DATA':
    XdgVar('APPDATA', 'LOCALAPPDATA', 'AppData/Local', '/local/share',
           'XDG_DATA_HOME', 'XDG_DATA_DIRS', '.local/share'),
    'STATE':
    XdgVar('APPDATA', 'LOCALAPPDATA', 'AppData/Local', '/local/share',
           'XDG_STATE_HOME', 'XDG_STATE_DIRS', '.local/state')
}


def is_mount(path: Path):
    """
    Check across platform if path is mountpoint or drive.

    Args:
        path: path to be checked
    """
    try:
        if path.is_mount():
            return True
        return False
    except NotImplementedError:  # pragma: no cover
        if path.resolve().drive + '\\' == str(path):
            return True
        return False


def walk_ancestors(child_dir: Path) -> List[Path]:
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
        List of Paths to parents of ancestral configurations:
            First directory is most dominant
    """
    config_heir: List[Path] = []

    while not is_mount(child_dir):
        if (child_dir / '__init__.py').is_file():
            config_heir.append(child_dir)
        if any((child_dir / setup).is_file()
               for setup in ('setup.cfg', 'setup.py')):
            # project directory
            config_heir.append(child_dir)
            break
        child_dir = child_dir.parent
    return config_heir


def xdg_base(base: str = 'CONFIG') -> List[Path]:
    """
    Get XDG_<BASE>_HOME locations.

    `specifications
    <https://specifications.freedesktop.org/basedir-spec/latest/ar01s03.html>`__

    Args:
        base: xdg base to fetch {CACHE,CONFIG,DATA,STATE}

    Returns:
        List of xdg-<base> Paths
            First directory is most dominant
    Raises:
        KeyError: bad variable name

    """
    xdgbase = XDG_BASES[base.upper()]
    xdg_heir: List[Path] = []
    # environment
    if sys.platform.startswith('win'):  # pragma: no cover
        # windows
        user_home = Path(os.environ['USERPROFILE'])
        root_var = Path(os.environ[xdgbase.win_root])
        xdg_base_home = Path(
            os.environ.get(xdgbase.win_var, user_home / xdgbase.win_default))
        xdg_heir.append(xdg_base_home)
        xdg_heir.append(root_var)
    else:
        # assume POSIX
        user_home = Path(os.environ['HOME'])
        xdg_base_home = Path(
            os.environ.get(xdgbase.unix_var, user_home / xdgbase.unix_default))
        xdg_heir.append(xdg_base_home)
        if xdgbase.unix_vars:
            xdg_base_dirs = os.environ.get(xdgbase.unix_vars,
                                           xdgbase.unix_root)
        else:
            xdg_base_dirs = xdgbase.unix_root
        if xdg_base_dirs:
            for xdg_dirs in xdg_base_dirs.split(':'):
                xdg_heir.append(Path(xdg_dirs))
    return xdg_heir


def locate_base(project: str,
                custom: os.PathLike = None,
                ancestors: bool = False,
                base_type: str = 'CONFIG',
                py_bin: os.PathLike = None) -> List[Path]:
    """
    Locate base (data/base) directories at standard locations.

    Args:
        project: name of project whose base is being fetched
        custom: custom location (directory)
        ancestors: inherit ancestor directories that contain __init__.py
        base_type: type of xdg base {CACHE,CONFIG,DATA,STATE}
        py_bin: namespace.__file__ that imports this function

    Returns:
        List of all possible base directory paths:
            Existing and non-existing
            First directory is most dominant

    """
    # Preference of base *Most dominant first*
    base_heir: List[Path] = []

    # custom
    if custom is not None:
        if not Path(custom).is_dir():
            raise FileNotFoundError(f'Custom base: {custom} not found')
        base_heir.append(Path(custom))

    # Current directory
    current_dir = Path('.').resolve()
    base_heir.append(current_dir)

    if ancestors:
        # ancestral directories
        ancestor_parents = walk_ancestors(current_dir)
        base_heir.extend(ancestor_parents)

    # xdg locations
    xdg_heir = xdg_base(base_type)
    for heir in xdg_heir:
        base_heir.append(heir / project)

    # Shipped location
    if py_bin:
        base_heir.append(Path(py_bin).parent)
    return base_heir

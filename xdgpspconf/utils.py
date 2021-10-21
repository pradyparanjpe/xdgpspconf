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
Common filesystem discovery functions.

"""

import os
from pathlib import Path
from typing import Union


def fs_perm(path: Path, mode: Union[int, str] = 0, **permargs):
    """
    Check read, write, execute permissions for effective id.

    Args:
        path: check permissions of this location
        mode: permissions to check {[0-7],r,w,x,rw,wx,rx,rwx,}
        **permargs:

            All are passed to :py:meth:`os.access`

            Defaults:

                - effective_ids: ``True``
                - follow_symlinks ``True``

    Returns:
        ``True`` only if permissions are available or if perm is ``0``
    """
    if mode in ('0', 0, ''):
        return True
    mode_letter = {'x': 1, 'w': 2, 'r': 4}
    mode_code = (None, os.X_OK, os.W_OK, os.W_OK | os.X_OK, os.R_OK,
                 os.R_OK | os.X_OK, os.R_OK | os.W_OK,
                 os.R_OK | os.W_OK | os.X_OK)

    # convert mode to octal
    oct_mode = 0
    try:
        if isinstance(mode, str):
            # new in 3.10, use match .. case
            # convert to int
            for p in list(mode):
                oct_mode += mode_letter[p]
        else:
            # permissions as integer
            oct_mode = mode % 8
        _mode = mode_code[oct_mode]
    except KeyError as err:
        raise KeyError(f'{err}\nmode: ([0-7]|r|w|x|rw|wx|rx|rwx|)') from None
    if _mode is None:
        # this should never happen
        # dummy check fallback
        return True
    while not path.exists():
        path = path.parent
    for default in ('follow_symlinks', 'effective_ids'):
        permargs[default] = permargs.get(default, True)
    return os.access(path, _mode, **permargs)


def is_mount(path: Path):
    """
    Check across platform if path is mountpoint (unix) or drive (win).

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

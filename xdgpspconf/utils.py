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
Common filesystem discovery functions.

"""

import os
from functools import reduce
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional, Sequence, Tuple, Union

PERMARGS: Dict[str, Any] = {
    'mode': 0,
    'dir_fd': None,
    'effective_ids': True,
    'follow_symlinks': True
}
"""Keys accepted by :py:meth:`os.access`"""


def fs_perm(path: Path, mode: Union[str, int] = 0, **permargs):
    """
    Check rwx- permissions to the latest existing parent for effective id.

    Args:
        path: check permissions of this location or latest existing ancestor.
        mode: permissions to check {[0-7],-,x,w,wx,r,rx,rw,rwx}
        **permargs:

            All are passed to :py:meth:`os.access`

            Defaults:

                :py:data:`xdgpspconf.utils.PERMARGS`

    Returns:
        ``True`` only if permissions are available
    """
    # convert mode to octal
    # os returns the same ints, yet, we allow os to have changed
    mode_code = {
        0: os.F_OK,
        1: os.X_OK,
        2: os.W_OK,
        3: os.W_OK | os.X_OK,
        4: os.R_OK,
        5: os.R_OK | os.X_OK,
        6: os.R_OK | os.W_OK,
        7: os.R_OK | os.W_OK | os.X_OK,
        '-': os.F_OK,
        'x': os.X_OK,
        'w': os.W_OK,
        'r': os.R_OK,
    }

    if isinstance(mode, str):
        # convert to int
        permargs['mode'] = reduce(lambda x, y: x | mode_code[y], mode, 0)
    else:
        # permissions supplied as integer
        permargs['mode'] = mode_code[mode % 8]

    # walk to latest existing ancestor
    while not path.exists():
        path = path.parent
    try:
        return os.access(path, **permargs)
    except NotImplementedError:  # pragma: no cover
        for not_impl_kw in 'dir_fd', 'follow_symlinks', 'effective_ids':
            del permargs[not_impl_kw]
        return os.access(path, **permargs)


def is_mount(path: Path) -> bool:
    """
    Check across platform if path is mount-point (unix) or drive (win).

    Args:
        path: path to be checked
    """
    # assume POSIX
    try:
        if path.is_mount():
            return True
        return False
    # windows
    except NotImplementedError:  # pragma: no cover
        if path.resolve().drive + '\\' == str(path):
            return True
        return False


def serial_secure_seq(unsafe_seq: Sequence):
    """Resolve Sequence and stringify complex data types for safe dumping"""
    safe_list: List[Optional[Union[bool, int, float, str, Tuple, Dict]]] = []
    for item in unsafe_seq:
        if isinstance(item, (bool, str, int, float)) or item is None:
            safe_list.append(item)
        elif isinstance(item, Sequence):
            safe_list.append(serial_secure_seq(item))
        elif isinstance(item, Mapping):
            safe_list.append(serial_secure_map(item))
        else:
            safe_list.append(str(item))
    return tuple(safe_list)


def serial_secure_map(
    unsafe_map: Mapping
) -> Dict[Optional[Union[bool, int, float, str, Tuple, Dict]],
          Tuple[Optional[Union[bool, int, float, str, Tuple, Dict]]]]:
    """Resolve Mapping and stringify complex data types for safe dumping"""
    safe_map = {}
    for key, value in unsafe_map.items():

        # stringify key
        if isinstance(key, (bool, int, float, str)) or key is None:
            safe_key = key
        elif isinstance(key, Sequence):
            safe_key = serial_secure_seq(key)
        else:
            safe_key = str(key)

        # value
        if isinstance(value, (bool, int, float, str)) or value is None:
            safe_map[safe_key] = value
        elif isinstance(value, Sequence):
            safe_map[safe_key] = serial_secure_seq(value)
        elif isinstance(value, Mapping):
            safe_map[safe_key] = serial_secure_map(value)
        else:
            safe_map[safe_key] = str(value)
    return safe_map

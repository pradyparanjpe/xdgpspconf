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
Discovery base

"""

import os
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

from xdgpspconf.utils import fs_perm, is_mount


@dataclass
class XdgVar():
    """
    xdg-defined variable
    """
    var: str = ''
    dirs: Optional[str] = None
    root: List[str] = field(default_factory=list)
    default: List[str] = field(default_factory=list)

    def update(self, master: Dict[str, Any]):
        """
        Update values
        """
        for key, val in master.items():
            if key not in self.__dict__:
                raise KeyError(f'{key} is not a recognised key')
            setattr(self, key, val)


@dataclass
class PlfmXdg():
    """
    Platform Suited Variables
    """
    win: XdgVar = XdgVar()
    posix: XdgVar = XdgVar()


def extract_xdg():
    """
    Read from 'strict'-standard locations.

    'Strict' locations:
       Posix:
          - ``<shipped_root>/xdg.yml``
          - ``/etc/xdgpspconf/xdg.yml``
          - ``/etc/xdg/xdgpspconf/xdg.yml``
          - ``${XDG_CONFIG_HOME:-${HOME}/.config}/xdgpspconf/xdg.yml``
       Windows:
          - ``%APPDATA%\\xdgpspconf\\xdg.yml``
          - ``%LOCALAPPDATA%\\xdgpspconf\\xdg.yml``
    """
    xdg_info = {}
    pspxdg_locs = [Path(__file__).parent / 'xdg.yml']
    config_tail = 'xdgpspconf/xdg.yml'
    if sys.platform.startswith('win'):
        pspxdg_locs.extend(
            (Path(os.environ['APPDATA']) / config_tail,
             Path(
                 os.environ.get(
                     'LOCALAPPDATA',
                     Path(os.environ['USERPROFILE']) / 'AppData/Local')) /
             config_tail))
    else:
        pspxdg_locs.extend(
            (Path(__file__).parent / 'xdg.yml', Path('/etc') / config_tail,
             Path('/etc/xdg') / config_tail,
             Path(
                 os.environ.get('XDG_CONFIG_HOME',
                                Path(os.environ['HOME']) / '.config')) /
             config_tail))
    for conf_xdg in pspxdg_locs:
        try:
            with open(conf_xdg) as conf:
                xdg_info.update(yaml.safe_load(conf))
        except (FileNotFoundError, IsADirectoryError, PermissionError):
            pass

    xdg: Dict[str, PlfmXdg] = {}
    for var_type, var_info in xdg_info.items():
        win_xdg = XdgVar()
        posix_xdg = XdgVar()
        win_xdg.update(var_info.get('win'))
        posix_xdg.update(var_info.get('posix'))
        xdg[var_type] = PlfmXdg(win=win_xdg, posix=posix_xdg)
    return xdg


XDG = extract_xdg()


class FsDisc():
    """
    File-System DISCovery functions

    Args:
        project: str: project under consideration
        base: str: xdg base to fetch {CACHE,CONFIG,DATA,STATE}
        shipped: Path: namespace: ``__Path__``
        **permargs: all (arguments to :py:meth:`os.access`) are passed to
            :py:meth:`xdgpspconf.utils.fs_perm`

    Attributes:
        project: str: project under consideration
        xdg: PlfmXdg: cross-platform xdg variables
        permargs: Dict[str, Any]: permission arguments

    """
    def __init__(self,
                 project: str,
                 base: str = 'data',
                 shipped: os.PathLike = None,
                 **permargs):
        self.project = project
        self.permargs = permargs
        self.shipped = [Path(shipped).resolve().parent] if shipped else []
        self._xdg: PlfmXdg = XDG[base]

    def locations(self) -> Dict[str, List[Path]]:
        """
        Shipped, root, user, improper locations

        Returns:
            named dictionary containing respective list of Paths
        """
        return {
            'improper': self.improper_loc(),
            'user_loc': self.user_xdg_loc(),
            'root_loc': self.root_xdg_loc(),
            'shipped': self.shipped
        }

    @property
    def xdg(self) -> PlfmXdg:
        return self._xdg

    @xdg.setter
    def xdg(self, value: PlfmXdg):
        self._xdg = value

    def __repr__(self) -> str:
        r_out = []
        for attr in ('project', 'permargs', 'shipped', 'xdg'):
            r_out.append(f'{attr}: {getattr(self, attr)}')
        return '\n'.join(r_out)

    def trace_ancestors(self, child_dir: Path) -> List[Path]:
        """
        Walk up to nearest mountpoint or project root.

           - collect all directories containing ``__init__.py``
             (assumed to be source directories)
           - project root is directory that contains ``setup.cfg``
             or ``setup.py``
           - mountpoint is a unix mountpoint or windows drive root
           - I **AM** my 0th ancestor

        Args:
            child_dir: walk ancestry of `this` directory

        Returns:
            List of Paths to ancestors:
                First directory is most dominant
        """
        pedigree: List[Path] = []

        # I **AM** my 0th ancestor
        while not is_mount(child_dir):
            if (child_dir / '__init__.py').is_file():
                pedigree.append(child_dir)
            if any((child_dir / setup).is_file()
                   for setup in ('setup.cfg', 'setup.py')):
                # project directory
                pedigree.append(child_dir)
                break
            child_dir = child_dir.parent
        return pedigree

    def user_xdg_loc(self) -> List[Path]:
        """
        Get XDG_<BASE>_HOME locations.

        `specifications
        <https://specifications.freedesktop.org/basedir-spec/latest/ar01s03.html>`__

        Returns:
            List of xdg-<base> Paths
                First directory is most dominant
        """
        # environment
        if sys.platform.startswith('win'):  # pragma: no cover
            # windows
            user_home = Path(os.environ['USERPROFILE'])
            os_xdg_loc = os.environ.get(self.xdg.win.var)
            os_default = self.xdg.win.default
        else:
            # assume POSIX
            user_home = Path(os.environ['HOME'])
            os_xdg_loc = os.environ.get(self.xdg.posix.var)
            os_default = self.xdg.posix.default
        if os_xdg_loc is None:
            xdg_base_loc = [Path(user_home / loc) for loc in os_default]
        else:
            xdg_base_loc = [Path(loc) for loc in os_xdg_loc.split(os.pathsep)]
        if not sys.platform.startswith('win'):
            # DONT: combine with previous condition, order is important
            # assume POSIX
            if self.xdg.posix.dirs and self.xdg.posix.dirs in os.environ:
                xdg_base_loc.extend((Path(unix_loc) for unix_loc in os.environ[
                    self.xdg.posix.dirs].split(os.pathsep)))
        return [loc / self.project for loc in xdg_base_loc]

    def root_xdg_loc(self) -> List[Path]:
        """
        Get ROOT's counterparts of XDG_<BASE>_HOME locations.

        `specifications
        <https://specifications.freedesktop.org/basedir-spec/latest/ar01s03.html>`__

        Returns:
            List of root-<base> Paths (parents to project's base)
                First directory is most dominant
        """
        if sys.platform.startswith('win'):  # pragma: no cover
            # windows
            os_root = self.xdg.win.root
        else:
            # assume POSIX
            os_root = self.xdg.posix.root
        if os_root:
            return [Path(root_base) / self.project for root_base in os_root]
        return []

    def improper_loc(self) -> List[Path]:
        """
        Get discouraged improper data locations such as *~/.project*.

        This is strongly discouraged.

        Returns:
            List of xdg-<base> Paths (parents to project's base)
                First directory is most dominant
        """
        # environment
        if sys.platform.startswith('win'):  # pragma: no cover
            # windows
            user_home = Path(os.environ['USERPROFILE'])
        else:
            # assume POSIX
            user_home = Path(os.environ['HOME'])
        return [user_home / (hide + self.project) for hide in ('', '.')]

    def get_loc(self,
                dom_start: bool = True,
                improper: bool = False,
                **kwargs) -> List[Path]:
        """
        Get discovered locations.

        Args:
            dom_start: when ``False``, end with most dominant
            improper: include improper locations such as *~/.project*
            **kwargs:
                - custom: custom location
                - trace_pwd: when supplied, walk up to mountpoint or
                  project-root and inherit all locations that contain
                  ``__init__.py``. Project-root is identified by discovery of
                  ``setup.py`` or ``setup.cfg``. Mountpoint is ``is_mount``
                  in unix or Drive in Windows. If ``True``, walk from ``$PWD``
                - :py:meth:`xdgpspconf.utils.fs_perm` kwargs: passed on
        """
        dom_order: List[Path] = []

        custom = kwargs.get('custom')
        if custom is not None:
            # don't check
            dom_order.append(Path(custom))

        trace_pwd = kwargs.get('trace_pwd')
        if trace_pwd is True:
            trace_pwd = Path('.').resolve()
        if trace_pwd:
            inheritance = self.trace_ancestors(Path(trace_pwd))
            dom_order.extend(inheritance)

        if improper:
            dom_order.extend(self.locations()['improper'])

        dom_order.extend(self.locations()['user_loc'])
        dom_order.extend(self.locations()['root_loc'])
        dom_order.extend(self.locations()['shipped'])
        permargs = {
            key: val
            for key, val in kwargs.items()
            if key in ('mode', 'dir_fs', 'effective_ids', 'follow_symlinks')
        }
        permargs = {**self.permargs, **permargs}
        dom_order = list(filter(lambda x: fs_perm(x, **permargs), dom_order))
        if dom_start:
            return dom_order
        return list(reversed(dom_order))

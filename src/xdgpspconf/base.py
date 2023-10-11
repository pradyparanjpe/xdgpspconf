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
r"""
Base to discover paths.

\*\*kwargs
----------
Following kwargs are defined for some functions as indicated.

trace_pwd : Union[Path, os.PathLike]
    When supplied, walk up to mountpoint or project-root and inherit all
    locations that contain ``__init__.py``. Project-root is identified by
    existence of ``setup.py`` or ``setup.cfg``. Mountpoint returns ``True`` for
    :meth:`Path.is_mount` in unix or is Drive in Windows. If ``True``, walk
    from ``$PWD``.
\*\*kwargs : Dict[str, Any]
    remaining kwargs of :py:meth:`xdgpspconf.utils.fs_perm`: passed on

Order
-----
Most to least- dominant (least to most global) order

- custom supplied [Optional]
- traced ancestry [Optional]
- XDG specification paths
- Paths that are improper according to XDG [Optional]
- root
- shipped

"""

import os
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import yaml

from xdgpspconf.utils import PERMARGS, fs_perm, is_mount


@dataclass
class XdgVar():
    """xdg-defined variable"""

    var: str = ''
    """XDG variable name"""

    dirs: Optional[str] = None
    """XDG variable list"""

    root: List[str] = field(default_factory=list)
    """root locations"""

    default: List[str] = field(default_factory=list)
    """default location"""

    def update(self, master: Dict[str, Any]):
        """
        Update values.

        Parameters
        ----------
        master : Dict[str, Any]
            update with these values

        """
        for key, val in master.items():
            if key not in self.__dict__:
                raise KeyError(f'{key} is not a recognised key')
            setattr(self, key, val)


@dataclass
class PlfmXdg():
    """Platform Suited Variables"""

    win: XdgVar = field(default_factory=XdgVar)
    """Windows variables"""

    posix: XdgVar = field(default_factory=XdgVar)
    """POSIX variables"""


def extract_xdg():
    """
    Read from 'strict'-standard locations.

    locations
    ---------

    POSIX
    ~~~~~
    - <shipped_root>/``xdg.yml``
    - ``/etc/xdgpspconf/xdg.yml``
    - ``/etc/xdg/xdgpspconf/xdg.yml``
    - ``${XDG_CONFIG_HOME:-${HOME}/.config}/xdgpspconf/xdg.yml``

    Windows
    ~~~~~~~
    - ``%APPDATA%\\xdgpspconf\\xdg.yml``
    - ``%LOCALAPPDATA%\\xdgpspconf\\xdg.yml``

    """
    xdg_info = {}
    pspxdg_locs = [Path(__file__).parent / 'xdg.yml']
    config_tail = 'xdgpspconf/xdg.yml'
    if sys.platform.startswith('win'):  # pragma: no cover
        pspxdg_locs.extend(
            (Path(os.environ['APPDATA']) / config_tail,
             Path(os.environ.get('LOCALAPPDATA',
                                 Path.home() / 'AppData/Local')) /
             config_tail))
    else:
        pspxdg_locs.extend(
            (Path(__file__).parent / 'xdg.yml', Path('/etc') / config_tail,
             Path('/etc/xdg') / config_tail,
             Path(os.environ.get('XDG_CONFIG_HOME',
                                 Path.home() / '.config')) / config_tail))
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
"""Configuration of xdgpspconf itself."""


class BaseDisc():
    r"""
    File-System basic DISCovery functions.

    See Also
    --------
    :class:`xdgpspconf.base.DataDisc`
    :class:`xdgpspconf.base.StateDisc`
    :class:`xdgpspconf.config.ConfDisc`

    Parameters
    ----------
    project : str
        project under consideration
    base : str
        xdg base to fetch {CACHE,CONFIG,DATA,STATE}
    shipped : Path
        ``namespace.__file__``
    \*\*permargs : Dict[str, Any]
        all (arguments to :meth:`os.access`) are passed to
        :meth:`xdgpspconf.utils.fs_perm`

    """

    def __init__(self,
                 project: str,
                 base: str = 'data',
                 shipped: Optional[Union[Path, os.PathLike]] = None,
                 **permargs):
        self.project = project
        """project under consideration"""

        self.permargs = {**PERMARGS, **permargs}
        """permission arguments"""

        self.shipped = Path(shipped).resolve().parent if shipped else None
        """location of developer-shipped files"""

        self._xdg: PlfmXdg = XDG[base]

        self._user_xdg_loc: Optional[List[Path]] = None

        self._improper_loc: Optional[List[Path]] = None

        self._root_xdg_loc: Optional[List[Path]] = None

        self._locations: Optional[List[Path]] = None

    @property
    def xdg(self) -> PlfmXdg:
        """
        Cross-platform xdg variables.

        Disable deleter.
        """
        return self._xdg

    @xdg.setter
    def xdg(self, value: PlfmXdg):
        self._xdg = value

    @property
    def user_xdg_loc(self) -> List[Path]:
        """XDG_<BASE>_HOME locations. First directory is most dominant."""
        if self._user_xdg_loc is None:
            user_home = Path.home()
            # environment
            if sys.platform.startswith('win'):  # pragma: no cover
                # windows
                os_xdg_loc = os.environ.get(self.xdg.win.var)
                os_default = self.xdg.win.default
            else:
                # assume POSIX
                os_xdg_loc = os.environ.get(self.xdg.posix.var)
                os_default = self.xdg.posix.default
            if os_xdg_loc is None:  # pragma: no cover
                xdg_base_loc = [(user_home / loc) for loc in os_default]
            else:
                xdg_base_loc = [
                    Path(loc) for loc in os_xdg_loc.split(os.pathsep)
                ]
            if not sys.platform.startswith('win'):
                # DONT: combine with previous condition, order is important
                # assume POSIX
                if self.xdg.posix.dirs and self.xdg.posix.dirs in os.environ:
                    xdg_base_loc.extend(
                        (Path(unix_loc) for unix_loc in os.environ[
                            self.xdg.posix.dirs].split(os.pathsep)))
            self._user_xdg_loc = [loc / self.project for loc in xdg_base_loc]
        return self._user_xdg_loc

    @property
    def improper_loc(self) -> List[Path]:
        """
        Discouraged improper data locations such as *~/.project*.

        First directory is most dominant

        .. deprecated:: 0.0.1
            This is strongly discouraged.
            Deprecated, yet permamently maintained.

        """
        if self._improper_loc is None:
            user_home = Path.home()
            self._improper_loc = [
                user_home / (hide + self.project) for hide in ('', '.')
            ]
        return self._improper_loc

    @property
    def root_xdg_loc(self) -> List[Path]:
        """
        Get ROOT's counterparts of XDG_<BASE>_HOME locations.

        First directory is most dominant.
        """
        if self._root_xdg_loc is None:
            if sys.platform.startswith('win'):  # pragma: no cover
                # windows
                os_root = self.xdg.win.root
            else:
                # assume POSIX
                os_root = self.xdg.posix.root
            self._root_xdg_loc = [
                Path(root_base) / self.project for root_base in os_root
            ]
        return self._root_xdg_loc

    @property
    def locations(self) -> Dict[str, List[Path]]:
        """
        Named dictionary containing respective list of Paths.

        Shipped, root, user, (improper) locations.

        """
        return {
            'user_loc': self.user_xdg_loc,
            'improper': self.improper_loc,
            'root_loc': self.root_xdg_loc,
            'shipped': [self.shipped] if self.shipped else []
        }

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

        Parameters
        ----------
        child_dir : Path
            walk ancestry of `this` directory

        Returns
        -------
        List[Path]
            Paths to ancestors: First directory is most dominant
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

    def get_loc(self,
                custom: Optional[Path] = None,
                dom_start: bool = True,
                improper: bool = False,
                **kwargs) -> List[Path]:
        r"""
        Get discovered locations.

        Parameters
        ----------
        custom : Optional[Path]
            custom location
        dom_start : bool
            When ``False``, end with most dominant
        improper : bool
            include improper locations such as *~/.project*
        **kwargs : Dict[str, Any]
            trace_pwd : Union[Path, os.PathLike, bool]
                When supplied, walk up to mountpoint or project-root and
                inherit all locations that contain ``__init__.py``.
                Project-root is identified by existence of ``setup.py`` or
                ``setup.cfg``. Mountpoint is ``is_mount`` in unix or Drive
                in Windows. If ``True``, walk from ``$PWD``.
            \*\*permargs : Dict[str, Any]
                    passed on to :meth:`xdgpspconf.utils.fs_perm`.

        Returns
        -------
        List[ Path]
            base paths with permissions [dom_start]
        """
        dom_order: List[Path] = []

        if custom is not None:
            # don't check
            dom_order.append(Path(custom))

        trace_pwd = kwargs.get('trace_pwd')
        if trace_pwd is True:
            trace_pwd = Path.cwd()
        if trace_pwd:
            inheritance = self.trace_ancestors(Path(trace_pwd))
            dom_order.extend(inheritance)

        # xdg user locations
        dom_order.extend(self.locations['user_loc'])

        # deprecated locations
        if improper:
            dom_order.extend(self.locations['improper'])

        # read-only locations
        dom_order.extend(self.locations['root_loc'])
        dom_order.extend(self.locations['shipped'])

        permargs = {key: val for key, val in kwargs.items() if key in PERMARGS}
        permargs = {**self.permargs, **permargs}
        dom_order = list(filter(lambda x: fs_perm(x, **permargs), dom_order))
        if dom_start:
            return dom_order
        return list(reversed(dom_order))

    def safe_loc(self,
                 custom: Optional[Path] = None,
                 dom_start: bool = True,
                 **kwargs) -> List[Path]:
        r"""
        Locate safe writeable paths.

        - Doesn't care about accessibility or existence of locations.
        - User must catch:
            - :exc:`PermissionError`
            - :exc:`IsADirectoryError`
            - :exc:`FileNotFoundError`
        - Improper locations (*~/.project*) are deliberately dropped

        .. tip::
            set dom_start = ``False`` for global storage

        Parameters
        ----------
        custom : Optional[Path]
            custom location
        dom_start : bin
            When ``False``, end with most dominant
        **kwargs : Dict[str, Any]
            trace_pwd : Union[Path, os.PathLike, bool]
                When supplied, walk up to mountpoint or project-root and
                inherit all locations that contain ``__init__.py``.
                Project-root is identified by existence of ``setup.py`` or
                ``setup.cfg``. Mountpoint is ``is_mount`` in unix or Drive in
                Windows. If ``True``, walk from ``$PWD``.
            \*\*permargs : Dict[str, Any]
                passed on to :meth:`xdgpspconf.utils.fs_perm`


        Returns
        -------
        List[Path]
            First path is most dominant

        """
        kwargs['mode'] = kwargs.get('mode', 2)

        # filter private locations
        private_locs = ['site-packages', 'venv', '/etc', 'setup', 'pyproject']
        if self.shipped is not None:
            private_locs.append(str(self.shipped))

        safe_paths = filter(
            lambda x: not any(private in str(x) for private in private_locs),
            self.get_loc(custom=custom, dom_start=dom_start, **kwargs))
        return list(safe_paths)


class CacheDisc(BaseDisc):
    """
    Cache Storage discovery functions

    Use for cached data. (may be lost)

    See Also
    --------
    :class:`xdgpspconf.base.DataDisc`
    :class:`xdgpspconf.base.StateDisc`
    :class:`xdgpspconf.config.ConfDisc`
    """

    def __init__(self,
                 project: str,
                 shipped: Optional[Union[Path, os.PathLike]] = None,
                 **permargs):
        super().__init__(project=project,
                         base='cache',
                         shipped=shipped,
                         **permargs)


class DataDisc(BaseDisc):
    """
    Data Storage discovery functions.

    Use for static data.

    See Also
    --------
    :class:`xdgpspconf.base.CacheDisc`
    :class:`xdgpspconf.base.StateDisc`
    :class:`xdgpspconf.config.ConfDisc`
    """

    def __init__(self,
                 project: str,
                 shipped: Optional[Union[Path, os.PathLike]] = None,
                 **permargs):
        super().__init__(project=project,
                         base='data',
                         shipped=shipped,
                         **permargs)


class StateDisc(BaseDisc):
    """
    State Storage discovery functions

    Use for state data: logs, history.

    See Also
    --------
    :class:`xdgpspconf.base.CacheDisc`
    :class:`xdgpspconf.base.DataDisc`
    :class:`xdgpspconf.config.ConfDisc`
    """

    def __init__(self,
                 project: str,
                 shipped: Optional[Union[Path, os.PathLike]] = None,
                 **permargs):
        super().__init__(project=project,
                         base='state',
                         shipped=shipped,
                         **permargs)

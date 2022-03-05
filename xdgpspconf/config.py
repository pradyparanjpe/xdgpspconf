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
# along with xdgpspconf. If not, see <https://www.gnu.org/licenses/>. #
"""
Special case of configuration, where base object is a file

Following kwargs are defined for some functions as indicated:
   - cname: name of config file
   - ext: extension restriction filter(s)
   - trace_pwd: when supplied, walk up to mountpoint or project-root and
     inherit all locations that contain __init__.py. Project-root is
     identified by existence of ``setup.py`` or ``setup.cfg``. Mountpoint is
     ``is_mount`` in unix or Drive in Windows. If ``True``, walk from ``$PWD``
   - kwargs of :py:meth:`xdgpspconf.utils.fs_perm`: passed on

Most to least- dominant (least to most global) order
   - custom supplied [Optional]
   - traced ancestry [Optional]
   - XDG specification paths
   - Paths that are improper according to XDG [Optional]
   - root
   - shipped

"""

import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from xdgpspconf.base import BaseDisc
from xdgpspconf.config_io import parse_rc, write_rc
from xdgpspconf.utils import PERMARGS, fs_perm

CONF_EXT = '.yml', '.yaml', '.toml', '.conf', '.ini'
"""Extensions that are supported (parsed) by this module"""


class ConfDisc(BaseDisc):
    """
    CONF DISCoverer

    Each location is config file, NOT directory as with BaseDisc
    """

    def __init__(self,
                 project: str,
                 shipped: Union[Path, str] = None,
                 **permargs):
        super().__init__(project, base='config', shipped=shipped, **permargs)

    def locations(self, cname: str = None) -> Dict[str, List[Path]]:
        """
        XDG, improper, root, shipped locations

        Args:
            cname: name of configuration file

        Returns:
            named dictionary containing respective list of Paths
        """
        cname = cname or 'config'
        shipped_loc = [(self.shipped / cname).with_suffix(ext)
                       for ext in CONF_EXT] if self.shipped else []
        return {
            'user_loc': self.user_xdg_loc(cname),
            'improper': self.improper_loc(cname),
            'root_loc': self.root_xdg_loc(cname),
            'shipped': shipped_loc
        }

    def trace_ancestors(self, child_dir: Path) -> List[Path]:
        """
        Walk up to nearest mountpoint or project root.

           - collect all directories containing __init__.py \
             (assumed to be source directories)
           - project root is directory that contains ``setup.cfg``
             or ``setup.py``
           - mountpoint is a unix mountpoint or windows drive root
           - I **AM** my 0th ancestor

        Args:
            child_dir: walk ancestry of `this` directory

        Returns:
            List of Paths to ancestor configs:
                First directory is most dominant
        """
        config = []
        pedigree = super().trace_ancestors(child_dir)
        if child_dir not in pedigree:  # pragma: no cover
            pedigree = [child_dir, *pedigree]
        config.extend(
            (config_dir / f'.{self.project}rc' for config_dir in pedigree))

        if pedigree:
            for setup in ('pyproject.toml', 'setup.cfg'):
                if (pedigree[-1] / setup).is_file():
                    config.append(pedigree[-1] / setup)
        return config

    def user_xdg_loc(self, cname: str = 'config') -> List[Path]:
        """
        Get XDG_<BASE>_HOME locations.

        Args:
            cname: name of config file

        Returns:
            List of xdg-<base> Paths
                First directory is most dominant
        Raises:
            KeyError: bad variable name

        """
        user_base_loc = super().user_xdg_loc()
        config = []
        for ext in CONF_EXT:
            for loc in user_base_loc:
                config.append((loc / cname).with_suffix(ext))
                config.append(loc.with_suffix(ext))
        return config

    def root_xdg_loc(self, cname: str = 'config') -> List[Path]:
        """
        Get ROOT's counterparts of XDG_<BASE>_HOME locations.

        Args:
            cname: name of config file

        Returns:
            List of root-<base> Paths (parents to project's base)
                First directory is most dominant
        Raises:
            KeyError: bad variable name

        """
        root_base_loc = super().root_xdg_loc()
        config = []
        for ext in CONF_EXT:
            for loc in root_base_loc:
                config.append((loc / cname).with_suffix(ext))
                config.append(loc.with_suffix(ext))
        return config

    def improper_loc(self, cname: str = 'config') -> List[Path]:
        """
        Get ROOT's counterparts of XDG_<BASE>_HOME locations.

        Args:
            cname: name of config file

        Returns:
            List of root-<base> Paths (parents to project's base)
                First directory is most dominant
        Raises:
            KeyError: bad variable name

        """
        improper_base_loc = super().improper_loc()
        config = []
        for ext in CONF_EXT:
            for loc in improper_base_loc:
                config.append((loc / cname).with_suffix(ext))
                config.append(loc.with_suffix(ext))
        return config

    def get_conf(self,
                 dom_start: bool = True,
                 improper: bool = False,
                 custom: Path = None,
                 **kwargs) -> List[Path]:
        """
        Get discovered configuration files.

        Args:
            custom: custom location
            dom_start: when ``False``, end with most dominant
            improper: include improper locations such as *~/.project*
            **kwargs:
                - cname: name of configuration file. Default: 'config'
                - trace_pwd: when supplied, walk up to mountpoint or
                  project-root and inherit all locations that contain
                  ``__init__.py``. Project-root is identified by existence of
                  ``setup.py`` or ``setup.cfg``. Mountpoint is ``is_mount``
                  in unix or Drive in Windows. If ``True``, walk from ``$PWD``
                - permargs passed on to :py:meth:`xdgpspconf.utils.fs_perm`

        Returns:
            List of configuration paths with permissions [dom_start]
        """
        # NOTE: order of following statements IS important
        dom_order: List[Path] = []

        if custom is not None:
            # assume existence and proceed
            dom_order.append(Path(custom))

        rc_val = os.environ.get(self.project.upper() + 'RC')
        if rc_val is not None:  # pragma: no cover
            if not Path(rc_val).is_file():
                raise FileNotFoundError(
                    f'RC configuration file: {rc_val} not found')
            dom_order.append(Path(rc_val))

        trace_pwd = kwargs.get('trace_pwd')
        if trace_pwd is True:
            trace_pwd = Path.cwd()
        if trace_pwd:
            inheritance = self.trace_ancestors(Path(trace_pwd))
            dom_order.extend(inheritance)

        locations = self.locations(kwargs.get('cname'))

        # xdg user locations
        dom_order.extend(locations['user_loc'])

        # deprecated locations
        if improper:
            dom_order.extend(locations['improper'])

        # read-only locations
        dom_order.extend(locations['root_loc'])
        dom_order.extend(locations['shipped'])

        permargs = {key: val for key, val in kwargs.items() if key in PERMARGS}
        permargs = {**self.permargs, **permargs}
        dom_order = list(filter(lambda x: fs_perm(x, **permargs), dom_order))
        if dom_start:
            return dom_order
        return list(reversed(dom_order))

    def safe_config(self,
                    ext: Union[str, List[str]] = None,
                    dom_start: bool = True,
                    mode: Union[str, int] = 2,
                    **kwargs) -> List[Path]:
        """
        Locate safe writeable paths of configuration files.

           - Doesn't care about accessibility or existence of locations.
           - User must catch:
              - ``PermissionError``
              - ``IsADirectoryError``
              - ``FileNotFoundError``
           - Improper locations (*~/.project*) are deliberately dropped
           - Recommendation: use dom_start=``False`` for global storage

        Args:
            ext: extension filter(s)
            dom_start: when ``False``, end with most dominant
            mode: permission mode to check
            **kwargs:
                - custom: custom location
                - cname: name of configuration file. Default: 'config'
                - trace_pwd: when supplied, walk up to mountpoint or
                  project-root and inherit all locations that contain
                  ``__init__.py``. Project-root is identified by existence of
                  ``setup.py`` or ``setup.cfg``. Mountpoint is ``is_mount``
                  in unix or Drive in Windows. If ``True``, walk from ``$PWD``
                - permargs passed on to :py:meth:`xdgpspconf.utils.fs_perm`


        Returns:
            Safe configuration locations (existing and prospective)

        """
        # filter private locations
        private_locs = ['site-packages', 'venv', '/etc', 'setup', 'pyproject']
        if self.shipped is not None:
            private_locs.append(str(self.shipped))
        safe_paths = filter(
            lambda x: not any(private in str(x) for private in private_locs),
            self.get_conf(dom_start=dom_start, mode=mode, **kwargs))
        if ext is None:
            return list(safe_paths)

        # filter extensions
        if isinstance(ext, str):
            ext = [ext]
        return list(filter(lambda x: x.suffix in ext, safe_paths))

    def read_config(self,
                    flatten: bool = False,
                    dom_start: bool = True,
                    **kwargs) -> Dict[Path, Dict[str, Any]]:
        """
        Locate Paths to standard directories and parse config.

        Args:
            flatten: superimpose configurations to return the final outcome
            dom_start: when ``False``, end with most dominant
            **kwargs:
                - custom: custom location
                - cname: name of configuration file. Default: 'config'
                - trace_pwd: when supplied, walk up to mountpoint or
                  project-root and inherit all locations that contain
                  ``__init__.py``. Project-root is identified by existence of
                  ``setup.py`` or ``setup.cfg``. Mountpoint is ``is_mount``
                  in unix or Drive in Windows. If ``True``, walk from ``$PWD``
                - improper: include improper locations such as *~/.project*
                - permargs passed on to :py:meth:`xdgpspconf.utils.fs_perm`

        Returns:
            parsed configuration from each available file

        Raises:
            BadConf- Bad configuration file format

        """
        kwargs['mode'] = kwargs.get('mode', 4)
        avail_confs: Dict[Path, Dict[str, Any]] = {}
        # load configs from oldest ancestor to current directory
        for config in self.get_conf(dom_start=dom_start, **kwargs):
            try:
                avail_confs[config] = parse_rc(config, project=self.project)
            except (PermissionError, FileNotFoundError, IsADirectoryError):
                pass

        if not flatten:
            return avail_confs

        super_config: Dict[str, Any] = {}
        for config in reversed(list(avail_confs.values())):
            super_config.update(config)
        return {Path.cwd(): super_config}

    def write_config(self,
                     data: Dict[str, Any],
                     force: str = 'fail',
                     dom_start: bool = True,
                     **kwargs) -> Optional[Path]:
        """
        Write data to the most global safe configuration file.

            - Recommendation: use dom_start=``False`` for global storage

        Args:
            data: serial data to save
            dom_start: when ``False``, end with most dominant
            force: force overwrite {'overwrite','update','fail'}
            **kwargs


        Returns: Path to which, configuration was written
        """
        for config in self.safe_config(dom_start=dom_start, **kwargs):
            try:
                if write_rc(data, config, force=force):
                    return config
            except (PermissionError, IsADirectoryError, FileNotFoundError):
                continue
        return None

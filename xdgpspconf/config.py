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
# along with xdgpspconf. If not, see <https://www.gnu.org/licenses/>.
#
"""
Locate and read configurations.

Read:
   - standard xdg-base locations
   - current directory and ancestors
   - custom location

"""

import configparser
import os
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Union

import toml
import yaml

from xdgpspconf.common import locate_base, walk_ancestors, xdg_base
from xdgpspconf.errors import BadConf


def _fs_perm(loc: Path):
    while not loc.exists():
        loc = loc.parent
    return os.access(loc, os.W_OK | os.R_OK, effective_ids=True)


def _parse_yaml(config: Path) -> Dict[str, Any]:
    """
    Read configuration.

    Specified as a yaml file:
        - .rc
        - style.yml
        - *.yml
    """
    with open(config, 'r') as rcfile:
        conf: Dict[str, Any] = yaml.safe_load(rcfile)
    if conf is None:  # pragma: no cover
        raise yaml.YAMLError
    return conf


def _write_yaml(data: Dict[str, Any],
                config: Path,
                force: str = 'fail') -> bool:
    """
    Write data to configuration file.

    Args:
        data: serial data to save
        config: configuration file path
        force: force overwrite {'overwrite', 'update', 'fail'}

    """
    old_data: Dict[str, Any] = {}
    if config.is_file():
        # file already exists
        if force == 'fail':
            return False
        if force == 'update':
            old_data = _parse_yaml(config)
    data = {**old_data, **data}
    with open(config, 'w') as rcfile:
        yaml.dump(data, rcfile)
    return True


def _parse_ini(config: Path, sub_section: bool = False) -> Dict[str, Any]:
    """
    Read configuration.

    Supplied in ``setup.cfg`` OR
        - *.cfg
        - *.conf
        - *.ini
    """
    parser = configparser.ConfigParser()
    parser.read(config)
    if sub_section:
        return {
            pspcfg.replace('.', ''): dict(parser.items(pspcfg))
            for pspcfg in parser.sections() if '' in pspcfg
        }
    return {
        pspcfg: dict(parser.items(pspcfg))
        for pspcfg in parser.sections()
    }  # pragma: no cover


def _write_ini(data: Dict[str, Any],
               config: Path,
               force: str = 'fail') -> bool:
    """
    Write data to configuration file.

    Args:
        data: serial data to save
        config: configuration file path
        force: force overwrite {'overwrite', 'update', 'fail'}

    """
    old_data: Dict[str, Any] = {}
    if config.is_file():
        # file already exists
        if force == 'fail':
            return False
        if force == 'update':
            old_data = _parse_ini(config)
    data = {**old_data, **data}
    parser = configparser.ConfigParser()
    parser.update(data)
    with open(config, 'w') as rcfile:
        parser.write(rcfile)
    return True


def _parse_toml(config: Path, sub_section: bool = False) -> Dict[str, Any]:
    """
    Read configuration.

    Supplied in ``pyproject.toml`` OR
        - *.toml
    """
    if sub_section:
        with open(config, 'r') as rcfile:
            conf: Dict[str, Any] = toml.load(rcfile).get('', {})
        return conf
    with open(config, 'r') as rcfile:
        conf = dict(toml.load(rcfile))
    if conf is None:  # pragma: no cover
        raise toml.TomlDecodeError
    return conf


def _write_toml(data: Dict[str, Any],
                config: Path,
                force: str = 'fail') -> bool:
    """
    Write data to configuration file.

    Args:
        data: serial data to save
        config: configuration file path
        force: force overwrite {'overwrite', 'update', 'fail'}

    """
    old_data: Dict[str, Any] = {}
    if config.is_file():
        # file already exists
        if force == 'fail':
            return False
        if force == 'update':
            old_data = _parse_toml(config)
    data = {**old_data, **data}
    with open(config, 'w') as rcfile:
        toml.dump(data, rcfile)
    return True


def _parse_rc(config: Path) -> Dict[str, Any]:
    """
    Parse rc file.

    Args:
        config: path to configuration file

    Returns:
        configuration sections

    Raises:
        BadConf: Bad configuration

    """
    if config.name == 'setup.cfg':
        # declared inside setup.cfg
        return _parse_ini(config, sub_section=True)
    if config.name == 'pyproject.toml':
        # declared inside pyproject.toml
        return _parse_toml(config, sub_section=True)
    try:
        # yaml configuration format
        return _parse_yaml(config)
    except yaml.YAMLError:
        try:
            # toml configuration format
            return _parse_toml(config)
        except toml.TomlDecodeError:
            try:
                # try generic config-parser
                return _parse_ini(config)
            except configparser.Error:
                raise BadConf(config_file=config) from None


def _write_rc(data: Dict[str, Any], config: Path, force: str = 'fail') -> bool:
    """
    Write data to configuration file.

    Args:
        data: serial data to save
        config: configuration file path
        force: force overwrite {'overwrite', 'update', 'fail'}

    Returns: success
    """
    if config.suffix in ('.conf', '.cfg', '.ini'):
        return _write_ini(data, config, force)
    if config.suffix == '.toml':
        return _write_toml(data, config, force)
    # assume yaml
    return _write_yaml(data, config, force)


def ancestral_config(child_dir: Path, rcfile: str) -> List[Path]:
    """
    Walk up to nearest mountpoint or project root.

       - collect all directories containing __init__.py
         (assumed to be source directories)
       - project root is directory that contains ``setup.cfg`` or ``setup.py``
       - mountpoint is a unix mountpoint or windows drive root
       - I am **NOT** my ancestor

    Args:
        child_dir: walk ancestry of `this`  directory
        rcfile: name of rcfile

    Returns:
        List of Paths to ancestral configurations:
            First directory is most dominant
    """
    config_dirs = walk_ancestors(child_dir)
    # setup.cfg, pyproject.toml are missing

    config_heir: List[Path] = [conf_dir / rcfile for conf_dir in config_dirs]
    for sub_section_file in ('pyproject.toml', 'setup.cfg'):
        config_heir.append(config_dirs[-1] / sub_section_file)
    return config_heir


def xdg_config() -> List[Path]:
    """
    Get XDG_CONFIG_HOME locations.

    `specifications
    <https://specifications.freedesktop.org/basedir-spec/latest/ar01s03.html>`__

    Returns:
        List of xdg-config Paths
            First directory is most dominant
    """
    return xdg_base('CONFIG')


def locate_config(project: str,
                  custom: os.PathLike = None,
                  ancestors: bool = False,
                  cname: str = 'config',
                  py_bin: os.PathLike = None) -> List[Path]:
    """
    Locate configurations at standard locations.

    Args:
        project: name of project whose configuration is being fetched
        custom: custom location for configuration
        ancestors: inherit ancestor directories that contain __init__.py
        cname: name of config file
        py_bin: namespace.__file__ that imports this function

    Returns:
        List of all possible configuration paths:
            Existing and non-existing
            First directory is most dominant

    """
    _custom_p = Path(custom).parent if custom else None
    config_dirs = locate_base(project, _custom_p, ancestors, 'CONFIG', py_bin)
    # missing: filename, .{project}RC /cname config/cname
    # Preference of configurations *Most dominant first*
    config_heir: List[Path] = []
    for conf_dir in config_dirs:
        # config in ancestor files should be an rc file
        if (conf_dir in Path('.').resolve().parents
                or conf_dir == Path('.').resolve()):
            if conf_dir == _custom_p:
                config_heir.append(conf_dir /
                                   Path(custom).name)  # type: ignore
            else:
                config_heir.append(conf_dir / f'.{project}rc')
        else:
            # non-ancestor
            for ext in '.yml', '.yaml', '.toml', '.conf':
                config_heir.append((conf_dir / cname).with_suffix(ext))

    # environment variable
    rc_val = os.environ.get(project.upper() + 'RC')
    if rc_val is not None:
        if not Path(rc_val).is_file():
            raise FileNotFoundError(
                f'RC configuration file: {rc_val} not found')
        insert_pos = 1 if custom else 0
        config_heir.insert(insert_pos, Path(rc_val))

    return config_heir


def safe_config(project: str,
                custom: os.PathLike = None,
                ext: Union[str, List[str]] = None,
                ancestors: bool = False,
                cname: str = 'config') -> List[Path]:
    """
    Locate safe writable paths of configuration files.

       - Doesn't care about accessibility or existance of locations.
       - User must catch:
          - ``PermissionError``
          - ``IsADirectoryError``
          - ``FileNotFoundError``
       - Recommendation: Try saving your configuration in in reversed order.

    Args:
        project: name of project whose configuration is being fetched
        custom: custom location for configuration
        ext: extension filter(s)
        ancestors: inherit ancestor directories that contain ``__init__.py``
        cname: name of config file

    Returns:
        Paths: First path is most dominant

    """
    if isinstance(ext, str):
        ext = [ext]
    safe_paths: List[Path] = []
    for loc in locate_config(project, custom, ancestors, cname):
        if any(private in str(loc)
               for private in ('site-packages', 'venv', '/etc', 'setup',
                               'pyproject')):
            continue
        if ext and loc.suffix and loc.suffix not in list(ext):
            continue
        if _fs_perm(loc):
            safe_paths.append(loc)
    return safe_paths


def read_config(project: str,
                custom: os.PathLike = None,
                ancestors: bool = False,
                cname: str = 'config',
                py_bin: os.PathLike = None) -> Dict[Path, Dict[str, Any]]:
    """
    Locate Paths to standard directories and parse config.

    Args:
        project: name of project whose configuration is being fetched
        custom: custom location for configuration
        ancestors: inherit ancestor directories that contain __init__.py
        cname: name of config file
        py_bin: namespace.__file__ that imports this function

    Returns:
        parsed configuration from each available file:
        first file is most dominant

    Raises:
        BadConf- Bad configuration file format

    """
    avail_confs: Dict[Path, Dict[str, Any]] = {}
    # load configs from oldest ancestor to current directory
    for config in locate_config(project, custom, ancestors, cname, py_bin):
        try:
            avail_confs[config] = _parse_rc(config)
        except (PermissionError, FileNotFoundError, IsADirectoryError):
            pass

    # initialize with config
    return avail_confs


def write_config(data: Dict[str, Any],
                 project: str,
                 ancestors: bool = False,
                 force: str = 'fail',
                 **kwargs) -> bool:
    """
    Write data to a safe configuration file.

    Args:
        data: serial data to save
        project: project name
        ancestors: inherit ancestor directories that contain __init__.py
        force: force overwrite {'overwrite', 'update', 'fail'}
        **kwargs:
            custom: custom configuration file
            ext: extension restriction filter(s)
            cname: custom configuration filename

    Returns: success
    """
    config_l = list(
        reversed(
            safe_config(project,
                        custom=kwargs.get('custom'),
                        ext=kwargs.get('ext'),
                        ancestors=ancestors,
                        cname=kwargs.get('cname', 'config'))))
    for config in config_l:
        try:
            return _write_rc(data, config, force=force)
        except (PermissionError, IsADirectoryError, FileNotFoundError):
            continue
    return False

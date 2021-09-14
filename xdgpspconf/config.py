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
import sys
from pathlib import Path
from typing import Any, Dict, List

import toml
import yaml

from xdgpspconf.errors import BadConf


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


def _parse_yaml(config: Path) -> Dict[str, dict]:
    """
    Read configuration.

    Specified as a yaml file:
        - .rc
        - style.yml
        - *.yml
    """
    with open(config, 'r') as rcfile:
        conf: Dict[str, dict] = yaml.safe_load(rcfile)
    if conf is None:  # pragma: no cover
        raise yaml.YAMLError
    return conf


def _parse_ini(config: Path, sub_section: bool = False) -> Dict[str, dict]:
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


def _parse_toml(config: Path, sub_section: bool = False) -> Dict[str, dict]:
    """
    Read configuration.

    Supplied in ``pyproject.toml`` OR
        - *.toml
    """
    if sub_section:
        with open(config, 'r') as rcfile:
            conf: Dict[str, dict] = toml.load(rcfile).get('', {})
        return conf
    with open(config, 'r') as rcfile:
        conf = dict(toml.load(rcfile))
    if conf is None:  # pragma: no cover
        raise toml.TomlDecodeError
    return conf


def _parse_rc(config: Path) -> Dict[str, dict]:
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
    config_heir: List[Path] = []

    while not _is_mount(child_dir):
        if (child_dir / '__init__.py').is_file():
            config_heir.append((child_dir / rcfile))
        if any((child_dir / setup).is_file()
               for setup in ('setup.cfg', 'setup.py')):
            # project directory
            config_heir.append((child_dir / 'pyproject.toml'))
            config_heir.append((child_dir / 'setup.cfg'))
            break
        child_dir = child_dir.parent
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
    xdg_heir: List[Path] = []
    # environment
    if sys.platform.startswith('win'):  # pragma: no cover
        # windows
        user_home = Path(os.environ['USERPROFILE'])
        root_config = Path(os.environ['APPDATA'])
        xdg_config_home = Path(
            os.environ.get('LOCALAPPDATA', user_home / 'AppData/Local'))
        xdg_heir.append(xdg_config_home)
        xdg_heir.append(root_config)
    else:
        # assume POSIX
        user_home = Path(os.environ['HOME'])
        xdg_config_home = Path(
            os.environ.get('XDG_CONFIG_HOME', user_home / '.config'))
        xdg_heir.append(xdg_config_home)
        xdg_config_dirs = os.environ.get('XDG_CONFIG_DIRS', '/etc/xdg')
        for xdg_dirs in xdg_config_dirs.split(':'):
            xdg_heir.append(Path(xdg_dirs))
    return xdg_heir


def locate_config(project: str,
                  custom: os.PathLike = None,
                  ancestors: bool = False,
                  cname: str = 'config') -> List[Path]:
    """
    Locate configurations at standard locations.

    Args:
        project: name of project whose configuration is being fetched
        custom: custom location for configuration
        ancestors: inherit ancestor directories that contain __init__.py
        cname: name of config file

    Returns:
        List of all possible configuration paths:
            Existing and non-existing
            First directory is most dominant

    """
    # Preference of configurations *Most dominant first*
    config_heir: List[Path] = []

    # custom
    if custom is not None:
        if not Path(custom).is_file():
            raise FileNotFoundError(
                f'Custom configuration file: {custom} not found')
        config_heir.append(Path(custom))

    # environment variable
    rc_val = os.environ.get(project.upper() + 'RC')
    if rc_val is not None:
        if not Path(rc_val).is_file():
            raise FileNotFoundError(
                f'RC configuration file: {rc_val} not found')
        config_heir.append(Path(rc_val))

    # Current directory
    current_dir = Path('.').resolve()
    config_heir.append((current_dir / f'.{project}rc'))

    if ancestors:
        # ancestral directories
        config_heir.extend(ancestral_config(current_dir, f'.{project}rc'))

    # xdg locations
    xdg_heir = xdg_config()
    for heir in xdg_heir:
        for ext in '.yml', '.yaml', '.toml', '.conf':
            config_heir.append((heir / project).with_suffix(ext))
            config_heir.append((heir / f'{project}/{cname}').with_suffix(ext))

    # Shipped location
    for ext in '.yml', '.yaml', '.toml', '.conf':
        config_heir.append((Path(__file__).parent.parent /
                            f'{project}/{cname}').with_suffix(ext))

    return config_heir


def read_config(project: str,
                custom: os.PathLike = None,
                ancestors: bool = False,
                cname: str = 'config') -> Dict[Path, Dict[str, Any]]:
    """
    Locate Paths to standard directories.

    Args:
        project: name of project whose configuration is being fetched
        custom: custom location for configuration
        ancestors: inherit ancestor directories that contain __init__.py
        cname: name of config file

    Returns:
        parsed configuration from each available file

    Raises:
        BadConf- Bad configuration file format

    """
    avail_confs: Dict[Path, Dict[str, Any]] = {}
    # load configs from oldest ancestor to current directory
    for config in reversed(locate_config(project, custom, ancestors, cname)):
        try:
            avail_confs[config] = _parse_rc(config)
        except (PermissionError, FileNotFoundError, IsADirectoryError):
            pass

    # initialize with config
    return avail_confs

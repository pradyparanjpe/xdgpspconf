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
Read/Write configurations.

"""

import configparser
from pathlib import Path
from typing import Any, Dict

import toml
import yaml

from xdgpspconf.errors import BadConf


def parse_yaml(config: Path) -> Dict[str, Any]:
    """
    Read configuration.

    Args:
        config: path to yaml config file

    Returns:
        parsed configuration
    """
    with open(config, 'r') as rcfile:
        conf: Dict[str, Any] = yaml.safe_load(rcfile)
    if conf is None:
        raise yaml.YAMLError
    return conf


def parse_toml(config: Path, section: str = None) -> Dict[str, Any]:
    """
    Read configuration.

    Args:
        config: path to yaml config file
        section: section in ``pyproject.toml`` corresponding to project

    Returns:
        parsed configuration
    """
    if section is not None:
        with open(config, 'r') as rcfile:
            conf: Dict[str, Any] = toml.load(rcfile).get(section, {})
        return conf
    with open(config, 'r') as rcfile:
        conf = dict(toml.load(rcfile))
    if conf is None:  # pragma: no cover
        raise toml.TomlDecodeError
    return conf


def parse_ini(config: Path, section: str = None) -> Dict[str, Any]:
    """
    Read configuration.


    Args:
        config: path to yaml config file
        section: section in ``pyproject.toml`` corresponding to project

    Returns:
        parsed configuration
    """
    parser = configparser.ConfigParser()
    parser.read(config)
    if section is not None:
        return {
            pspcfg.replace(f'{section}.', ''): dict(parser.items(pspcfg))
            for pspcfg in parser.sections() if f'{section}.' in pspcfg
        }
    return {
        pspcfg: dict(parser.items(pspcfg))
        for pspcfg in parser.sections()
    }  # pragma: no cover


def parse_rc(config: Path, project: str = None) -> Dict[str, Any]:
    """
    Parse rc file.

    Args:
        config: path to configuration file
        project: name of project (to locate subsection from pyptoject.toml)

    Returns:
        configuration sections

    Raises:
        BadConf: Bad configuration

    """
    if config.name == 'setup.cfg':
        # declared inside setup.cfg
        return parse_ini(config, section=project)
    if config.name == 'pyproject.toml':
        # declared inside pyproject.toml
        return parse_toml(config, section=project)
    try:
        # yaml configuration format
        return parse_yaml(config)
    except yaml.YAMLError:
        try:
            # toml configuration format
            return parse_toml(config)
        except toml.TomlDecodeError:
            try:
                # try generic config-parser
                return parse_ini(config)
            except configparser.Error:
                raise BadConf(config_file=config) from None


def write_yaml(data: Dict[str, Any],
               config: Path,
               force: str = 'fail') -> bool:
    """
    Write data to configuration file.

    Args:
        data: serial data to save
        config: configuration file path
        force: force overwrite {'overwrite','update','fail'}

    Returns:
        write success

    """
    old_data: Dict[str, Any] = {}
    if config.is_file():
        # file already exists
        if force == 'fail':
            return False
        if force == 'update':
            old_data = parse_yaml(config)
    data = {**old_data, **data}
    config.parent.mkdir(parents=True, exist_ok=True)
    with open(config, 'w') as rcfile:
        yaml.safe_dump(data, rcfile)
    return True


def write_toml(data: Dict[str, Any],
               config: Path,
               force: str = 'fail') -> bool:
    """
    Write data to configuration file.

    Args:
        data: serial data to save
        config: configuration file path
        force: force overwrite {'overwrite', 'update', 'fail'}

    Returns:
        write success

    """
    old_data: Dict[str, Any] = {}
    if config.is_file():
        # file already exists
        if force == 'fail':
            return False
        if force == 'update':
            old_data = parse_toml(config)
    data = {**old_data, **data}
    config.parent.mkdir(parents=True, exist_ok=True)
    with open(config, 'w') as rcfile:
        toml.dump(data, rcfile)
    return True


def write_ini(data: Dict[str, Any], config: Path, force: str = 'fail') -> bool:
    """
    Write data to configuration file.

    Args:
        data: serial data to save
        config: configuration file path
        force: force overwrite {'overwrite', 'update', 'fail'}

    Returns:
        write success

    """
    old_data: Dict[str, Any] = {}
    if config.is_file():
        # file already exists
        if force == 'fail':
            return False
        if force == 'update':
            old_data = parse_ini(config)
    data = {**old_data, **data}
    parser = configparser.ConfigParser()
    parser.update(data)
    config.parent.mkdir(parents=True, exist_ok=True)
    with open(config, 'w') as rcfile:
        parser.write(rcfile)
    return True


def write_rc(data: Dict[str, Any], config: Path, force: str = 'fail') -> bool:
    """
    Write data to configuration file.

    Args:
        data: serial data: user to confirm serialization safety
        config: configuration file path
        force: force overwrite {'overwrite', 'update', 'fail'}

    See also:
        :meth:`xdgpspconf.utils.serial_secure_seq`
        :meth:`xdgpspconf.utils.serial_secure_map`

    Returns:
        write success

    """
    if config.suffix in ('.conf', '.cfg', '.ini'):
        return write_ini(data, config, force)
    if config.suffix == '.toml':
        return write_toml(data, config, force)
    # assume yaml
    return write_yaml(data, config, force)

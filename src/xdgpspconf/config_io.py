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
"""Read/Write configurations."""

import configparser
import json
from pathlib import Path
from typing import Any, Dict, Optional

import pyjson5
import toml
import yaml

from xdgpspconf.errors import BadConf


def parse_yaml(config: Path) -> Dict[str, Any]:
    """
    Read yaml configuration.

    Parameters
    ----------
    config : Path
        path to yaml config file

    Returns
    -------
    Dict[str, Any]
        parsed configuration

    Raises
    ------
    BadConf
        Configuration is not in yaml format
    """
    with open(config, 'r') as rcfile:
        conf: Dict[str, Any] = yaml.safe_load(rcfile)
    if conf is None:
        raise BadConf(config_file=config)
    return conf


def parse_json(config: Path) -> Dict[str, Any]:
    """
    Read configuration

    Parameters
    ----------
    config : Path
        path to yaml config file

    Returns
    -------
    Dict[str, Any]
        parsed configuration
    """
    conf: Dict[str, Any] = {}
    with open(config, 'r') as rcfile:
        try:
            conf = pyjson5.load(rcfile)
        except pyjson5.pyjson5.Json5EOF:
            pass
    return conf


def parse_toml(config: Path, section: Optional[str] = None) -> Dict[str, Any]:
    """
    Read toml configuration.

    Parameters
    ----------
    config : Path
        path to toml config file
    section : Optional[str]
        section in ``pyproject.toml`` corresponding to project

    Returns
    -------
    Dict[str, Any]
        parsed configuration
    """
    with open(config, 'r') as rcfile:
        conf: Dict[str, Any] = toml.load(rcfile)
    return conf.get(section, {}) if section else conf


def parse_ini(config: Path, section: Optional[str] = None) -> Dict[str, Any]:
    """
    Read ini configuration.


    Parameters
    ----------
    config : Path
        path to .ini/.conf config file
    section : Optional[str]
        section in ``pyproject.toml`` corresponding to project

    Returns
    -------
    Dict[str, Any]
        parsed configuration
    """
    parser = configparser.ConfigParser()
    parser.read(config)
    if section is None:
        return {
            pspcfg: dict(parser.items(pspcfg))
            for pspcfg in parser.sections()
        }  # pragma: no cover
    return {
        pspcfg.replace(f'{section}.', ''): dict(parser.items(pspcfg))
        for pspcfg in parser.sections() if f'{section}.' in pspcfg
    }


def parse_rc(config: Path, project: Optional[str] = None) -> Dict[str, Any]:
    """
    Parse rc file.

    Parameters
    ----------
    config : Path
        path to configuration file
    project : str
        name of project (to locate subsection from pyptoject.toml)

    Returns
    -------
    Dict[str, Any]
        configuration sections

    Raises
    ------
    BadConf
        Bad configuration

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
    except (BadConf, yaml.YAMLError):
        try:
            # JSON object
            return parse_json(config)
        except pyjson5.Json5Exception:
            try:
                # toml configuration format
                return parse_toml(config)
            except toml.TomlDecodeError:
                try:
                    # try generic config-parser
                    return parse_ini(config)
                except configparser.Error:
                    raise BadConf(config_file=config)


def write_yaml(data: Dict[str, Any],
               config: Path,
               force: str = 'fail') -> bool:
    """
    Write data to configuration file.

    Parameters
    ----------
    data : Dict[str, Any]
        serial data to save
    config : Path
        configuration file path
    force : {'overwrite','update','fail'}
        force overwrite

    Returns
    -------
    bool
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


def write_json(data: Dict[str, Any],
               config: Path,
               force: str = 'fail') -> bool:
    """
    Write data to configuration file.

    Parameters
    ----------
    data : Dict[str, Any]
        serial data to save
    config : Path
        configuration file path
    force : {'overwrite','update','fail'}
        force overwrite

    Returns
    -------
    bool
        write success

    """
    old_data: Dict[str, Any] = {}
    if config.is_file():
        # file already exists
        if force == 'fail':
            return False
        if force == 'update':
            old_data = parse_json(config)
    data = {**old_data, **data}
    config.parent.mkdir(parents=True, exist_ok=True)
    with open(config, 'w') as rcfile:
        json.dump(data, rcfile)
    return True


def write_toml(data: Dict[str, Any],
               config: Path,
               force: str = 'fail') -> bool:
    """
    Write data to configuration file.

    Parameters
    ----------
    data : Dict[str, Any]
        serial data to save
    config : Path
        configuration file path
    force : {'overwrite', 'update', 'fail'}
        force overwrite

    Returns
    -------
    bool
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

    Parameters
    ----------
    data : Dict[str, Any]
        serial data to save
    config : Path
        configuration file path
    force : {'overwrite', 'update', 'fail'}
        force overwrite
    Returns
    -------
    bool
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


def write_rc(data: Dict[str, Any],
             config: Path,
             form: str = 'yaml',
             force: str = 'fail') -> bool:
    """
    Write data to configuration file.

    Configuration file format, if not provided, is guessed from extension
    and defaults to 'yaml'.

    Parameters
    ----------
    data : Dict[str, Any]
        serial data (user must confirm serialization safety)
    config : Path
        configuration file path
    form : {'yaml', 'json', 'toml', 'ini', 'conf', 'cfg'}
        configuration format (skip extension guess.)
    force : {'overwrite', 'update', 'fail'}
        force overwrite

    See Also
    --------
    :meth:`xdgpspconf.utils.serial_secure_seq`
    :meth:`xdgpspconf.utils.serial_secure_map`

    Returns
    -------
    bool
        write success

    """

    if ((config.suffix in ('.conf', '.cfg', '.ini'))
            or (form in ('conf', 'cfg', 'ini'))):
        return write_ini(data, config, force)
    if config.suffix == '.toml' or form == 'toml':
        return write_toml(data, config, force)
    if config.suffix == '.json' or form == 'json':
        return write_json(data, config, force)
    # assume yaml
    return write_yaml(data, config, force)

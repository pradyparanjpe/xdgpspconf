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
from pathlib import Path
from typing import Any

import pyjson5 as json
import toml
import yaml

from xdgpspconf.errors import BadConf


def parse_yaml(config: Path) -> dict[str, Any]:
    """
    Read yaml configuration.

    Parameters
    ----------
    config : Path
        path to yaml config file

    Returns
    -------
    dict[str, Any]
        parsed configuration
    """
    with open(config, 'r') as rcfile:
        conf: dict[str, Any] = yaml.safe_load(rcfile)
    if conf is None:
        raise yaml.YAMLError
    return conf


def parse_json(config: Path) -> dict[str, Any]:
    """
    Read configuration

    Parameters
    ----------
    config : Path
        path to yaml config file

    Returns
    -------
    dict[str, Any]
        parsed configuration
    """
    with open(config, 'r') as rcfile:
        conf: dict[str, Any] = json.load(rcfile)
    if conf is None:
        raise json.Json5Exception
    return conf


def parse_toml(config: Path, section: str | None = None) -> dict[str, Any]:
    """
    Read toml configuration.

    Parameters
    ----------
    config : Path
        path to toml config file
    section : str | None
        section in ``pyproject.toml`` corresponding to project

    Returns
    -------
    dict[str, Any]
        parsed configuration
    """
    with open(config, 'r') as rcfile:
        conf: dict[str, Any] = toml.load(rcfile)
    return conf.get(section, {}) if section else conf


def parse_ini(config: Path, section: str | None = None) -> dict[str, Any]:
    """
    Read ini configuration.


    Parameters
    ----------
    config : Path
        path to .ini/.conf config file
    section : str | None
        section in ``pyproject.toml`` corresponding to project

    Returns
    -------
    dict[str, Any]
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


def parse_rc(config: Path, project: str | None = None) -> dict[str, Any]:
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
    dict[str, Any]
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
    except yaml.YAMLError:
        try:
            # JSON object
            return parse_json(config)
        except json.Json5Exception:
            try:
                # toml configuration format
                return parse_toml(config)
            except toml.TomlDecodeError:
                try:
                    # try generic config-parser
                    return parse_ini(config)
                except configparser.Error:
                    raise BadConf(config_file=config) from None


def write_yaml(data: dict[str, Any],
               config: Path,
               force: str = 'fail') -> bool:
    """
    Write data to configuration file.

    Parameters
    ----------
    data : dict[str, Any]
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
    old_data: dict[str, Any] = {}
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


def write_json(data: dict[str, Any],
               config: Path,
               force: str = 'fail') -> bool:
    """
    Write data to configuration file.

    Parameters
    ----------
    data : dict[str, Any]
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
    old_data: dict[str, Any] = {}
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


def write_toml(data: dict[str, Any],
               config: Path,
               force: str = 'fail') -> bool:
    """
    Write data to configuration file.

    Parameters
    ----------
    data : dict[str, Any]
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
    old_data: dict[str, Any] = {}
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


def write_ini(data: dict[str, Any], config: Path, force: str = 'fail') -> bool:
    """
    Write data to configuration file.

    Parameters
    ----------
    data : dict[str, Any]
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
    old_data: dict[str, Any] = {}
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


def write_rc(data: dict[str, Any],
             config: Path,
             form: str = 'yaml',
             force: str = 'fail') -> bool:
    """
    Write data to configuration file.

    Configuration file format, if not provided, is guessed from extension
    and defaults to 'yaml'.

    Parameters
    ----------
    data : dict[str, Any]
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

    print(form)
    if ((config.suffix in ('.conf', '.cfg', '.ini'))
            or (form in ('conf', 'cfg', 'ini'))):
        return write_ini(data, config, force)
    if config.suffix == '.toml' or form == 'toml':
        return write_toml(data, config, force)
    if config.suffix == '.json' or form == 'json':
        return write_json(data, config, force)
    # assume yaml
    return write_yaml(data, config, force)

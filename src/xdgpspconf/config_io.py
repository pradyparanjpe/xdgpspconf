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
from collections.abc import Callable
from pathlib import Path
from typing import IO, Any, Dict, List, Optional, Tuple, Union

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
    with open(config, 'r') as rcfile:
        try:
            return pyjson5.load(rcfile)
        except pyjson5.Json5EOF:
            return {}


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
    try:
        return parse_toml(config, section=section)
    except toml.TomlDecodeError:
        pass
    parser = configparser.ConfigParser()
    parser.read(config)
    if section is None:
        return {
            pspcfg: dict(parser.items(pspcfg))
            for pspcfg in parser.sections()
        }
    return {
        pspcfg.replace(f'{section}.', ''): dict(parser.items(pspcfg))
        for pspcfg in parser.sections() if f'{section}.' in pspcfg
    }


def parse_rc(
    config: Path,
    *,
    project: Optional[str] = None,
    form: Optional[Union[List[str], str]] = None
) -> Tuple[Dict[str, Any], Optional[str]]:
    """
    Parse rc file.

    Parameters
    ----------
    config : Path
        path to configuration file
    project : str
        name of project (to locate subsection from pyptoject.toml)
    form : Optional[Union[List[str], str]]
        Expect file in this format. {'yaml', 'json', 'toml', 'ini'}

    Returns
    -------
    Tuple[Dict[str, Any], str]
        configuration sections, type of configuration

    Raises
    ------
    BadConf
        Bad configuration

    """
    if config.name == 'setup.cfg':
        # declared inside setup.cfg
        return parse_ini(config, section=project), None
    if config.name == 'pyproject.toml':
        # declared inside pyproject.toml
        return parse_toml(config, section=project), None
    if form:
        try:
            if 'yaml' in form:
                return parse_yaml(config), 'yaml'
            elif 'json' in form:
                return parse_json(config), 'json'
            elif 'toml' in form:
                return parse_toml(config), 'toml'
            elif 'ini' in form:
                return parse_ini(config), 'ini'
        except (yaml.YAMLError, pyjson5.Json5Exception, toml.TomlDecodeError,
                configparser.Error) as err:
            raise BadConf(config_file=config) from err
    try:
        # yaml configuration format
        return parse_yaml(config), 'yaml'
    except (BadConf, yaml.YAMLError):
        try:
            # JSON object
            return parse_json(config), 'json'
        except pyjson5.Json5Exception:
            try:
                # toml configuration format
                return parse_toml(config), 'toml'
            except toml.TomlDecodeError:
                try:
                    # try generic config-parser
                    return parse_ini(config), 'ini'
                except configparser.Error:
                    raise BadConf(config_file=config)


def ini_dump(data: Dict[str, Any], stream: IO):
    parser = configparser.ConfigParser()
    parser.update(data)
    parser.write(stream)


def write_rc(data: Dict[str, Any],
             config: Path,
             form: Optional[str] = None,
             force: str = 'fail') -> bool:
    """
    Write data to configuration file.

    Configuration file format is guessed from extension. If file name extension
    doesn't match any format, specified format [default: 'yaml'] is used.

    Parameters
    ----------
    data : Dict[str, Any]
        serial data (user must confirm serialization safety)
    config : Path
        configuration file path
    form : {'yaml', 'json', 'toml', 'ini', 'conf', 'cfg'}
        configuration format when extension doesn't match
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
    handles: Optional[Tuple[Callable, Callable]] = None
    ext_dict = {
        '.conf': (parse_ini, ini_dump),
        '.cfg': (parse_ini, ini_dump),
        '.ini': (parse_ini, ini_dump),
        '.toml': (parse_toml, toml.dump),
        '.json': (parse_json, json.dump)
    }
    handles = ext_dict.get(config.suffix) or ext_dict.get(f'.{form}')

    if not handles:
        # fallback
        handles = parse_yaml, yaml.dump

    old_data: Dict[str, Any] = {}
    if config.is_file():
        # file already exists
        if force == 'fail':
            return False
        if force == 'update':
            old_data = handles[0](config)
    data = {**old_data, **data}
    config.parent.mkdir(parents=True, exist_ok=True)
    with open(config, 'w') as rcfile:
        handles[1](data, rcfile)
    return True

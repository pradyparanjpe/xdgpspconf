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
from typing import (IO, Any, Dict, List, Mapping, Optional, Sequence, Tuple,
                    Union)

import pyjson5
import toml
import yaml

from xdgpspconf.errors import BadConf


class ConfStructParser(configparser.ConfigParser):
    r"""
    Extension to parse structures from :class:`configparser.ConfigParser`.

    Datatypes
    ---------

    bool
    ~~~~
    Convert keys of :attr:`configparser.ConfigParser.BOOLEAN_STATES` to
    corresponding boolean values.

    int
    ~~~
    Convert numbers `N` such that ``N % 1 = 0`` to int.

    float
    ~~~~~
    Return numbers which cannot be converted to int as floats.

    List
    ~~~~
    Configuration lists may be specified in any of the following formats.

    - **dangling** : indented deeper
    - **List-semi**: delimited by ``;`` optionally wrapped with space(s).
    - **List-comma**: delimited by ``,`` optionally wrapped with space(s).

    Return them as lists. Further, if possible, convert elements to
    suitable data-types.

    Dict
    ~~~~
    Configuration dicts are lists, which contain 'key=value' pairs.
    The spacer may be any of :attr:`configparser.ConfigParser._delimiter`,
    which is ``[':', '=']`` by default, or may be specified using the keyword
    `delimiter` provided to init.

    Return them as dicts. Further, if possible, convert values to
    suitable data-types.

    """

    def parsed_val(
            self,
            val: str) -> Optional[Union[bool, int, float, List, Dict, str]]:
        """
        Parse value string to nested python datatypes.

        Parameters
        ----------
        val : str
            string representation of structure

        Returns
        -------
        Optional[Union[bool, int, float, List, Dict, str]]
            Python datatype
        """
        if val in self.BOOLEAN_STATES:
            return self.BOOLEAN_STATES[val]
        # not a boolean
        try:
            float_val = float(val)
            if float_val % 1:
                return float_val
            return int(float_val)
        except ValueError:
            pass
        # NaN
        if any((sep in val for sep in ('\n', ',', ';'))):
            # dangling, `,` or ';' separated
            if '\n' in val:
                sep = '\n'
            elif ';' in val:
                sep = ';'
            else:
                sep = ','
            list_val = [
                self.parsed_val(line) for line in val.strip().rstrip().replace(
                    '\\\n', ' ').split(sep)
            ]
            if all(isinstance(subval, str) for subval in list_val):
                str_list: List[str] = list_val  # type: ignore [assignment]
                delims = [
                    delim for delim in
                    self._delimiters  # type: ignore [attr-defined]
                    if all((delim in subval for subval in str_list))
                ]
                delims.sort(key=lambda x: sum(
                    (subval.index(x) for subval in str_list)))
                if delims:
                    delim = delims[0]
                    return {
                        key_value[0].strip().rstrip():
                        self.parsed_val(key_value[1].strip().rstrip())
                        for key_value in
                        [subval.split(delim, 1) for subval in str_list]
                    }
            return list_val
        # fallback: return as received
        return val

    def built_val(self,
                  val: Optional[Union[bool, int, float, Sequence, Mapping,
                                      str]],
                  indent: int = 0,
                  delimiter: str = '=') -> str:
        """
        Build a string representation of value structure.

        Parameters
        ----------
        val : Optional[Union[bool, int, float, List, Dict, str]]
            Value structure of given datatypes
        indent : int
            Indentation level of parent (sub)section or value. Lists and dicts
            are indented 1 level deeper than this value.
        delimiter : str
            delimiter that separates keys from values
        """
        indent_ = indent + 1
        if isinstance(val, bool):
            return str([
                key for key, value in self.BOOLEAN_STATES.items()
                if value == val
            ][0])
        if isinstance(val, (int, float)):
            return str(val)
        dangle = ('\n' + '\t' * indent_)
        if not isinstance(val, str) and isinstance(val, Sequence):
            print(val)
            return dangle.join(
                (self.built_val(subval, indent_, delimiter) for subval in val))
        if isinstance(val, Mapping):
            return dangle.join((str(key) + delimiter +
                                self.built_val(subval, indent_, delimiter)
                                for key, subval in val.items()))
        return str(val).replace('\n', dangle)

    def items(self, *args, **kwargs):
        """
        Extension of :meth:`config.ConfigParser.items` to datatypes.

        Interpret formatted strings as datatype structures.

        Parameters
        ----------
        *args : Any
            passed to :meth:`config.ConfigParser.items`
        **kwargs : Dict[str, Any]
            passed to :meth:`config.ConfigParser.items`
        """
        return {
            key: self.parsed_val(val)
            for key, val in super().items(*args, **kwargs)
        }

    def _write_section(self, fp, section_name, section_items, delimiter):
        """Write a single section to the specified `fp`."""
        fp.write("[{}]\n".format(section_name))
        for key, value in section_items:
            value = self._interpolation.before_write(self, section_name, key,
                                                     value)
            if value is not None or not self._allow_no_value:
                value = delimiter + self.built_val(value, 0, delimiter)
            else:
                value = ""
            fp.write("{}{}\n".format(key, value))
        fp.write("\n")


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
    r"""
    Read ini configuration.

    .. warning::
        INI doesn't have a standard format.

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
    parser = ConfStructParser()
    parser.read(config)
    if section is None:
        return {pspcfg: dict(parser.items(pspcfg)) for pspcfg in parser}
    section_config: Dict[str, Any] = {}
    for pspcfg in parser:
        if pspcfg == section:
            section_config = {**section_config, **parser.items(pspcfg)}
        elif section in pspcfg:
            section_config[pspcfg.replace(f'{section}.',
                                          '')] = dict(parser.items(pspcfg))
    return section_config


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
    parser = ConfStructParser()
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
    handles = ext_dict.get(config.suffix) or ext_dict.get(
        f'.{form}')  # type: ignore [assignment]

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

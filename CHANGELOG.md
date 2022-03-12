# Changes in v0.2.1

  - yaml safe_dump is used to dump configuration to correspond to safe_load.
    - user must ensure serial nature of safe_dump.
    - utils ``xdgpspconf.utils.serial_secure_seq`` and ``xdgpspconf.utils.serial_secure_map`` may help.
  - Deprecated ``FsDisc``, use ``BaseDisc`` instead.
    - ``DataDisc``, ``StateDisc``, ``CacheDisc`` are pre-configured.
  - Corresponding tests and documentation updates.

# Changes in v0.2.0

  - Reordered dominance order.
    - XDG locations dominant over improper.
  - Standard ``PERMARGS`` can be imported from ``xdgpspconf.utils``.
  - some `**kwargs` from ``xdgpspconf.base`` and ``xdgpspconf.config`` are handled as optional parameters.
  - **BUGFIX**: make parent directory for config writing if absent. 

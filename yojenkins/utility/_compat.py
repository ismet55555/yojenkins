"""Compatibility shim for TOML read/write across Python versions."""

try:
    import tomllib
except ModuleNotFoundError:
    import tomli as tomllib

import tomli_w

__all__ = ['tomli_w', 'tomllib']

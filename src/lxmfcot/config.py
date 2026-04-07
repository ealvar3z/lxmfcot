"""Configuration helpers for lxmfcot."""

from __future__ import annotations

from configparser import ConfigParser, SectionProxy


DEFAULT_SECTION_NAME = "lxmfcot"


def default_config() -> ConfigParser:
    """Create the default config tree for the bridge."""
    parser = ConfigParser()
    parser[DEFAULT_SECTION_NAME] = {
        "COT_URL": "",
        "BRIDGE_MODE": "maintenance",
    }
    return parser


def default_section() -> SectionProxy:
    """Return the default config section."""
    parser = default_config()
    return parser[DEFAULT_SECTION_NAME]


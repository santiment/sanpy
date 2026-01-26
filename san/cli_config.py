"""
Cross-platform configuration management for sanpy CLI.

Stores API key and other settings in a platform-appropriate location:
- Linux/Mac: ~/.config/sanpy/config.json
- Windows: %APPDATA%/sanpy/config.json
"""

import json
import os
from pathlib import Path
from typing import Optional


def get_config_dir() -> Path:
    """Get the platform-appropriate config directory."""
    if os.name == "nt":  # Windows
        base = os.environ.get("APPDATA", Path.home())
    else:  # Linux/Mac
        base = os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config")

    config_dir = Path(base) / "sanpy"
    return config_dir


def get_config_path() -> Path:
    """Get the path to the config file."""
    return get_config_dir() / "config.json"


def _ensure_config_dir() -> None:
    """Create config directory if it doesn't exist."""
    config_dir = get_config_dir()
    config_dir.mkdir(parents=True, exist_ok=True)


def _load_config() -> dict:
    """Load config from file, return empty dict if doesn't exist."""
    config_path = get_config_path()
    if config_path.exists():
        try:
            with open(config_path, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return {}
    return {}


def _save_config(config: dict) -> None:
    """Save config to file."""
    _ensure_config_dir()
    config_path = get_config_path()
    with open(config_path, "w") as f:
        json.dump(config, f, indent=2)


def get_api_key() -> Optional[str]:
    """
    Get API key from config file.

    Note: Environment variable SANPY_APIKEY takes precedence,
    but that's handled in cli.py at the app level.
    """
    config = _load_config()
    return config.get("api_key")


def set_api_key(api_key: str) -> None:
    """Store API key in config file."""
    config = _load_config()
    config["api_key"] = api_key
    _save_config(config)


def clear_api_key() -> None:
    """Remove API key from config file."""
    config = _load_config()
    if "api_key" in config:
        del config["api_key"]
        _save_config(config)


def mask_api_key(api_key: Optional[str]) -> str:
    """Mask API key for display, showing only first/last 4 chars."""
    if not api_key:
        return "(not set)"
    if len(api_key) <= 8:
        return "*" * len(api_key)
    return f"{api_key[:4]}...{api_key[-4:]}"

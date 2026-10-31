"""Configuration management for dash-ai."""

import os
from pathlib import Path
from typing import Any, Dict

import yaml
from dotenv import load_dotenv

from dash_ai.core.errors import ConfigurationError


class Config:
    """Load and manage configuration from YAML and environment variables."""

    def __init__(self, config_file: str = "config/settings.yaml"):
        """Initialize configuration.

        Args:
            config_file: Path to YAML config file

        Raises:
            ConfigurationError: If config file not found or invalid
        """
        # Load environment variables first
        load_dotenv()

        # Load YAML config
        config_path = Path(config_file)
        if not config_path.exists():
            raise ConfigurationError(
                f"Configuration file not found: {config_file}",
                suggestion=f"Create {config_file} or check the path",
            )

        try:
            with open(config_path) as f:
                self._config = yaml.safe_load(f) or {}
        except yaml.YAMLError as e:
            raise ConfigurationError(
                f"Failed to parse configuration file: {e}",
                suggestion="Check YAML syntax in config/settings.yaml",
            ) from e
        except OSError as e:
            raise ConfigurationError(
                f"Failed to read configuration file: {e}",
                suggestion="Check file permissions",
            ) from e

        # Apply environment variable overrides
        self._apply_env_overrides()

        # Validate required settings
        self._validate()

    def _apply_env_overrides(self) -> None:
        """Apply environment variable overrides to config."""
        # Model overrides
        if os.getenv("OLLAMA_HOST"):
            if "model" not in self._config:
                self._config["model"] = {}
            self._config["model"]["host"] = os.getenv("OLLAMA_HOST")

        if os.getenv("MODEL_NAME"):
            if "model" not in self._config:
                self._config["model"] = {}
            self._config["model"]["name"] = os.getenv("MODEL_NAME")

        # Storage overrides
        if os.getenv("STORAGE_PATH"):
            if "storage" not in self._config:
                self._config["storage"] = {}
            self._config["storage"]["path"] = os.getenv("STORAGE_PATH")

        # App overrides
        if os.getenv("DATA_DIR"):
            if "app" not in self._config:
                self._config["app"] = {}
            self._config["app"]["data_dir"] = os.getenv("DATA_DIR")

        if os.getenv("DEBUG"):
            if "app" not in self._config:
                self._config["app"] = {}
            self._config["app"]["debug"] = os.getenv("DEBUG").lower() in ("true", "1", "yes")

    def _validate(self) -> None:
        """Validate required configuration fields.

        Raises:
            ConfigurationError: If required fields are missing
        """
        required_sections = {
            "model": ["type", "name", "host"],
            "storage": ["type", "path"],
            "retrieval": ["top_k"],
            "app": ["data_dir"],
        }

        for section, fields in required_sections.items():
            if section not in self._config:
                raise ConfigurationError(
                    f"Missing required config section: [{section}]",
                    suggestion="Check config/settings.yaml has all required sections",
                )

            for field in fields:
                if field not in self._config[section]:
                    raise ConfigurationError(
                        f"Missing required config field: [{section}] {field}",
                        suggestion="Check config/settings.yaml has all required fields",
                    )

    def get(self, section: str, key: str, default: Any = None) -> Any:
        """Get configuration value.

        Args:
            section: Configuration section (e.g., 'model', 'storage')
            key: Configuration key within section
            default: Default value if key not found

        Returns:
            Configuration value or default
        """
        return self._config.get(section, {}).get(key, default)

    def get_section(self, section: str) -> Dict[str, Any]:
        """Get entire configuration section.

        Args:
            section: Configuration section

        Returns:
            Dictionary of configuration values in section
        """
        return self._config.get(section, {})

    def __repr__(self) -> str:
        """String representation of config (without sensitive values)."""
        return f"<Config sections: {list(self._config.keys())}>"

"""Configuration management for dash-ai."""

import os
from pathlib import Path
from typing import Any, Dict

import yaml
from dotenv import load_dotenv


class Config:
    """Load and manage configuration from YAML and environment variables."""

    def __init__(self, config_file: str = "config/settings.yaml"):
        """Initialize configuration.

        Args:
            config_file: Path to YAML config file

        Raises:
            FileNotFoundError: If config file not found
            ValueError: If required configuration is missing
        """
        # Load environment variables first
        load_dotenv()

        # Load YAML config
        config_path = Path(config_file)
        if not config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_file}")

        with open(config_path) as f:
            self._config = yaml.safe_load(f) or {}

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
            ValueError: If required fields are missing
        """
        required_sections = {
            "model": ["type", "name", "host"],
            "storage": ["type", "path"],
            "retrieval": ["top_k"],
            "app": ["data_dir"],
        }

        for section, fields in required_sections.items():
            if section not in self._config:
                raise ValueError(f"Missing required config section: [{section}]")

            for field in fields:
                if field not in self._config[section]:
                    raise ValueError(
                        f"Missing required config field: [{section}] {field}"
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

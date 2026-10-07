"""
Centralized Configuration Loader for South India DLMAI.
Loads YAML configurations for geography, indicators, pillars, weights, scoring, and sensitivity.
"""

import os
from pathlib import Path
import yaml
from dataclasses import dataclass, field
from typing import Dict, List, Any


def get_project_root() -> Path:
    """Returns absolute path to project root directory."""
    return Path(__file__).resolve().parent.parent


def load_yaml(file_path: str) -> Dict[str, Any]:
    """Loads and parses a YAML configuration file."""
    root = get_project_root()
    abs_path = root / file_path if not os.path.isabs(file_path) else Path(file_path)
    if not abs_path.exists():
        raise FileNotFoundError(f"Configuration file not found: {abs_path}")
    with open(abs_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


class ConfigManager:
    """Singleton access to all project configurations."""
    _instance = None

    def __init__(self):
        self.geography = load_yaml("config/geography.yaml")
        self.indicators = load_yaml("config/indicators.yaml")
        self.pillars = load_yaml("config/pillars.yaml")
        self.weights = load_yaml("config/weights.yaml")
        self.scoring = load_yaml("config/scoring.yaml")
        self.sensitivity = load_yaml("config/sensitivity.yaml")

    @classmethod
    def get_config(cls):
        if cls._instance is None:
            cls._instance = ConfigManager()
        return cls._instance


# Convenience helper
def get_config() -> ConfigManager:
    return ConfigManager.get_config()

"""Configuration management for EPPD.

This module provides centralized configuration for EnergyPlus installation paths.
All simulation parameters are defined as function defaults in the appropriate modules.
"""

import tomllib
from dataclasses import dataclass
from pathlib import Path

@dataclass
class EnergyPlusConfig:
    """EnergyPlus installation configuration.

    Requires energyplus_location to be explicitly set in config.toml.
    The value is the full path to the EnergyPlus executable
    (e.g. /usr/local/EnergyPlus-25-2-0/energyplus on Linux/macOS,
    C:/EnergyPlusV25-2-0/energyplus.exe on Windows).
    weatherfiles_folder is optional.

    To change the location at runtime, assign directly using Path:
        >>> from pathlib import Path
        >>> from eppd.config import energyplus_config
        >>> energyplus_config.energyplus_location = Path('/path/to/EnergyPlus-25-2-0/energyplus')
        >>> # Windows:
        >>> energyplus_config.energyplus_location = Path('C:/EnergyPlusV25-2-0/energyplus.exe')
        >>> # Can also use Path methods like expanduser():
        >>> energyplus_config.energyplus_location = Path('~/EnergyPlus-25-2-0/energyplus').expanduser()
    """

    energyplus_location: Path | None = None
    weatherfiles_folder: Path | None = None

    def __post_init__(self):
        """Convert strings to Path if needed."""
        if isinstance(self.energyplus_location, str):
            self.energyplus_location = (
                Path(self.energyplus_location) if self.energyplus_location else None
            )

        if isinstance(self.weatherfiles_folder, str):
            self.weatherfiles_folder = (
                Path(self.weatherfiles_folder) if self.weatherfiles_folder else None
            )

    @classmethod
    def load_from_toml(cls) -> "EnergyPlusConfig":
        """Load EnergyPlus configuration from config.toml in EPPD package.

        Returns:
            EnergyPlusConfig instance with settings from config.toml

        Raises:
            FileNotFoundError: If config.toml is not found
            ValueError: If config cannot be parsed or energyplus.energyplus_location is missing
        """
        config_path = Path(__file__).parent / "config.toml"

        if not config_path.exists():
            raise FileNotFoundError(
                f"config.toml not found at {config_path}\n"
                f"Please ensure config.toml exists in the eppd package directory"
            )

        try:
            with open(config_path, "rb") as f:
                toml_config = tomllib.load(f)
        except Exception as e:
            raise ValueError(f"Failed to parse config.toml: {e}") from e

        # Extract EnergyPlus configuration
        if "energyplus" not in toml_config:
            raise ValueError(
                "Missing [energyplus] section in config.toml"
            )

        ep_config = toml_config["energyplus"]
        energyplus_location = ep_config.get("energyplus_location")

        if not energyplus_location:
            raise ValueError(
                "Missing 'energyplus_location' in [energyplus] section of config.toml"
            )

        weatherfiles_folder = ep_config.get("weatherfiles_folder")

        return cls(
            energyplus_location=Path(energyplus_location),
            weatherfiles_folder=Path(weatherfiles_folder) if weatherfiles_folder else None,
        )


# Global configuration instance loaded from config.toml
energyplus_config = EnergyPlusConfig.load_from_toml()

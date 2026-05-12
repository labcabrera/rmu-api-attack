import os
from importlib.metadata import PackageNotFoundError, version
from urllib.parse import urlsplit, urlunsplit

PACKAGE_NAME = "rmu-api-attack"


def _getenv(*names: str, default: str | None = None) -> str | None:
    for name in names:
        value = os.getenv(name)
        if value:
            return value
    return default


def _package_version() -> str:
    try:
        return version(PACKAGE_NAME)
    except PackageNotFoundError:
        return "0.0.0"


class Settings:
    """Application settings and configuration"""

    DEFAULT_MONGODB_URL = (
        "mongodb://admin:admin@localhost:27017/rmu-attack?authSource=admin"
    )

    def __init__(self) -> None:
        # MongoDB Configuration
        self.MONGODB_URL = _getenv(
            "RMU_MONGO_ATTACK_URI",
            "MONGO_URI",
            "MONGODB_URL",
            default=self.DEFAULT_MONGODB_URL,
        )
        self.MONGODB_DATABASE = _getenv(
            "RMU_MONGO_ATTACK_DATABASE",
            "MONGO_DATABASE",
            "MONGODB_DATABASE",
            default="rmu-attack",
        )

        # API Configuration
        self.API_VERSION = "v1"
        self.API_PREFIX = f"/{self.API_VERSION}"

        # Application Configuration
        self.APP_NAME = "RMU API Attack"
        self.APP_DESCRIPTION = (
            "API for managing RMU (Role Master Unified) attack system"
        )
        self.APP_VERSION = _package_version()

        # Development Configuration
        self.DEBUG = os.getenv("DEBUG", "false").lower() == "true"
        self.LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()

    @property
    def REDACTED_MONGODB_URL(self) -> str:
        """Return the MongoDB URL without credentials for diagnostics."""
        parsed = urlsplit(self.MONGODB_URL)
        if not parsed.username and not parsed.password:
            return self.MONGODB_URL

        host = parsed.hostname or ""
        if parsed.port:
            host = f"{host}:{parsed.port}"
        return urlunsplit(
            (
                parsed.scheme,
                f"***:***@{host}",
                parsed.path,
                parsed.query,
                parsed.fragment,
            )
        )

    class Config:
        case_sensitive = True


# Global settings instance
settings = Settings()

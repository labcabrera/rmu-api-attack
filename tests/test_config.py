from importlib.metadata import version

from app.infrastructure.config.config import Settings


def test_settings_supports_legacy_mongo_uri_env(monkeypatch):
    monkeypatch.delenv("RMU_MONGO_ATTACK_URI", raising=False)
    monkeypatch.setenv("MONGO_URI", "mongodb://user:secret@mongo:27017/rmu")
    monkeypatch.setenv("MONGO_DATABASE", "rmu-test")

    settings = Settings()

    assert settings.MONGODB_URL == "mongodb://user:secret@mongo:27017/rmu"
    assert settings.MONGODB_DATABASE == "rmu-test"


def test_redacted_mongodb_url_hides_credentials(monkeypatch):
    monkeypatch.setenv(
        "RMU_MONGO_ATTACK_URI",
        "mongodb://admin:admin@localhost:27017/rmu-attack?authSource=admin",
    )

    settings = Settings()

    assert settings.REDACTED_MONGODB_URL == (
        "mongodb://***:***@localhost:27017/rmu-attack?authSource=admin"
    )
    assert "admin:admin" not in settings.REDACTED_MONGODB_URL


def test_app_version_comes_from_package_metadata():
    settings = Settings()

    assert settings.APP_VERSION == version("rmu-api-attack")

"""Settings of the webservice."""
from __future__ import annotations

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """The settings used within the service

    Args:
        BaseSettings: The pydantic base settings that are automatically picking
            up environment variables and are matching those against the settings
            down below case insensitively.
    """

    build_version: str = "0.0.0"

    minio_host: str = "localhost"
    minio_port: int = 9000

    minio_access_key: str = "minio-root-user"
    minio_secret_key: str = "minio-root-password"

    minio_original_images_prefix: str = "original"
    minio_coffee_images_bucket: str = "coffee-images"


settings = Settings()

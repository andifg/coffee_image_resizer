"""Settings of the webservice."""

from __future__ import annotations

from pydantic_settings import BaseSettings

from resize.types import ReduceType


class Settings(BaseSettings):
    """The settings used within the service

    Args:
        BaseSettings: The pydantic base settings that are automatically picking
            up environment variables and are matching those against the settings
            down below case insensitively.
    """

    build_version: str = "0.0.0"

    log_level: str = "info"

    thumbnail_width: int = 1200
    thumbnail_format: str = "JPEG"

    kafka_bootstrap_servers: str = "localhost:9094"
    kafka_topic: str = "coffee-images"
    kafka_consumer_group: str = "coffee-images"

    reduce_type: ReduceType = ReduceType.THUMBNAIL

    minio_host: str = "localhost"
    minio_port: int = 9000

    minio_access_key: str = "minio-root-user"
    minio_secret_key: str = "minio-root-password"

    minio_original_images_prefix: str = "original"
    minio_coffee_images_bucket: str = "coffee-images"


settings = Settings()

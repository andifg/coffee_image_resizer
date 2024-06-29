import logging

from minio import Minio

from resize.exceptions import ObjectNotFoundError
from resize.resizer.image_resizer import ImageResizer
from resize.s3.object import ObjectCRUD
from resize.settings import settings


class S3Service:
    def __init__(self) -> None:
        """Initialize the Service class."""
        self.bucket_name = settings.minio_coffee_images_bucket
        self.object_crud = ObjectCRUD(
            minio_client=Minio(
                f"{settings.minio_host}:{settings.minio_port}",
                settings.minio_access_key,
                settings.minio_secret_key,
                secure=False,
            ),
            bucket_name=self.bucket_name,
        )

        self.image_resizer = ImageResizer()

    async def handle_kafka_message(self, key: str, value: str) -> None:
        """Handles a Kafka message

        This method fulfills the MessageHandler protocol. It processes a
        Kafka message by managing the download, resizing an storing of an
        image identified by the key of the message.

        Args:
            key (str): The key of the Kafka message.
            value (str): The value of the Kafka message.
        """
        logging.debug("Handling message: %s - %s", key, value)

        key = key.replace(f"{self.bucket_name}/", "")
        path, key = key.split("original/")

        try:
            image, filetype = self.object_crud.read(
                filepath=f"{path}original", filename=key
            )

            resized_image = self.image_resizer.resize_image(image, filetype)

            self.object_crud.create(
                filepath=f"{path}small",
                filename=key,
                file=resized_image,
                file_type=filetype,
            )

        except ObjectNotFoundError:
            logging.info("Object %s not found in S3", f"{path}original/{key}")
            return

        logging.info("Resized and stored image: %s%s", f"{path}small", key)

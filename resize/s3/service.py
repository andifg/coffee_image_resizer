from minio import Minio

from resize.exceptions import ObjectNotFoundError
from resize.resizer.resize import ImageResizer
from resize.s3.objectCRUD import ObjectCRUD
from resize.settings import settings


class S3Service:
    def __init__(self) -> None:
        self.object_crud = ObjectCRUD(
            minio_client=Minio(
                f"{settings.minio_host}:{settings.minio_port}",
                settings.minio_access_key,
                settings.minio_secret_key,
                secure=False,
            ),
            bucket_name=settings.minio_coffee_images_bucket,
        )

        self.image_resizer = ImageResizer()

    async def handle_kafka_message(self, key: str, value: str) -> None:
        print(f"Handling message: {key} - {value}")

        _, prefix, object_path = key.split("/")

        try:
            image, filetype = self.object_crud.read(
                object_path=f"{prefix}/{object_path}"
            )

            resized_image = self.image_resizer.resize_image(image)

            self.object_crud.create(
                filename=object_path,
                file=resized_image,
                file_type=filetype,
                prefix="small",
            )

        except ObjectNotFoundError:
            print(f"Object not found: {key}")
            return

        print(f"Message handled: {key} - {value}")

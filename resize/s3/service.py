from resize.s3.objectCRUD import ObjectCRUD
from resize.settings import settings
from minio import Minio
from resize.exceptions import ObjectNotFoundError


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

    async def handle_kafka_message(self, key: str, value: str) -> None:
        print(f"Handling message: {key} - {value}")


        _ , object_path = key.split('/', 1)


        try:
            image = self.object_crud.read(object_path=object_path)

            print("Read image")

        except ObjectNotFoundError:
            print(f"Object not found: {key}")
            return



        print(f"Message handled: {key} - {value}")

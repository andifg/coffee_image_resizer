import io
from PIL import Image
from resize.settings import settings
from resize.types import ReduceType


class ImageResizer:

    def __init__(self):
        self.strategy = settings.reduce_type

    def resize_image(self, image_data: bytes):
        if self.strategy == ReduceType.QUALITY:
            return self._reduze_quality(image_data)

        elif self.strategy == ReduceType.THUMBNAIL:
            return self._create_thumbnail(image_data)

        else:
            raise ValueError("Invalid ReduceType")

    def _reduze_quality(self, image_data: bytes, quality: int = 20):

        image = Image.open(io.BytesIO(image_data))

        new_byte = io.BytesIO()

        image.save(new_byte, format="JPEG", quality=quality)

        size = round(len(new_byte.getvalue()) / (1024 * 1024), 2)

        print(f"File Size in MegaBytes is {size} for qaulity {quality}")

        new_byte.seek(0)

        if size > 0.3 and quality > 5:
            print("Image size is greater than 0.3 MB")
            return self._reduze_quality(image_data, quality=quality - 3)

        else:
            return new_byte

    def _create_thumbnail(self, image_data: bytes):

        image = Image.open(io.BytesIO(image_data))

        factor = image.size[0] / 1200

        width = int(image.size[0] / factor)
        height = int(image.size[1] / factor)

        image.thumbnail((width, height), Image.LANCZOS)

        new_byte = io.BytesIO()

        image.save(new_byte, format="JPEG", optimize=True)

        size = round(len(new_byte.getvalue()) / (1024 * 1024), 2)

        print(f"File Size in MegaBytes is {size}")

        new_byte.seek(0)

        return new_byte

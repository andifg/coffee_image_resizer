import io
import logging

from PIL import Image

from resize.settings import settings
from resize.types import ReduceType


class ImageResizer:

    def __init__(self) -> None:
        self.strategy = settings.reduce_type

    def resize_image(self, image_data: bytes) -> io.BytesIO:
        """Resize the given image based on the selected strategy.

        Args:
            image_data (bytes): The image data to be resized.

        Returns:
            io.BytesIO: The resized image data.

        Raises:
            ValueError: If an invalid ReduceType is selected.
        """
        if self.strategy == ReduceType.QUALITY:
            return self._reduze_quality(image_data)

        if self.strategy == ReduceType.THUMBNAIL:
            return self._create_thumbnail(image_data)

        raise ValueError("Invalid ReduceType")

    def _reduze_quality(
        self, image_data: bytes, quality: int = 20
    ) -> io.BytesIO:
        """Reduce the quality of an image while keeping the dimensions.

        Args:
            image_data (bytes): The image data as bytes.
            quality (int, optional): The desired quality of the image.
                Defaults to 20.

        Returns:
            io.BytesIO: The image data with reduced quality.
        """
        image = Image.open(io.BytesIO(image_data))

        new_byte = io.BytesIO()

        image.save(new_byte, format=settings.thumbnail_format, quality=quality)

        size = round(len(new_byte.getvalue()) / (1024 * 1024), 2)

        logging.debug(
            "File Size in MegaBytes is %s for quality %s", size, quality
        )

        new_byte.seek(0)

        if size > 0.3 and quality > 5:
            logging.debug("Image size is greater than 0.3 MB")
            return self._reduze_quality(image_data, quality=quality - 3)

        return new_byte

    def _create_thumbnail(self, image_data: bytes) -> io.BytesIO:
        """Create a thumbnail image without changing the aspect ratio.

        Args:
            image_data (bytes): The image data as bytes.

        Returns:
            io.BytesIO: The thumbnail image as a BytesIO object.
        """
        with io.BytesIO(image_data) as data:
            image = Image.open(data)

            factor = max(image.size) / settings.thumbnail_width

            width = int(image.size[0] / factor)
            height = int(image.size[1] / factor)

            image.thumbnail((width, height), resample=Image.Resampling.LANCZOS)

            new_byte = io.BytesIO()

            image.save(
                new_byte, format=settings.thumbnail_format, optimize=True
            )

            size = round(len(new_byte.getvalue()) / (1024 * 1024), 2)

            logging.debug("File Size in MegaBytes is %s", size)

            new_byte.seek(0)

            return new_byte

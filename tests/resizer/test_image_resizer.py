import io
from unittest.mock import MagicMock, patch

import pytest
from PIL import Image

from resize.resizer.image_resizer import ImageResizer


@patch.object(ImageResizer, "_create_thumbnail")
@pytest.mark.asyncio
async def test_image_resizer_resize_image(
    mock_create_thumbnail: MagicMock,
) -> None:
    """Test resize_image method of ImageResizer with thumbnail strategy."""

    resizer = ImageResizer()

    resizer.resize_image(b"image_data", "jpeg")

    mock_create_thumbnail.assert_called_once_with(b"image_data", "jpeg")


def test_image_resizer_create_thumbnail_image(
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Test _create_thumbnail method of ImageResizer class with image."""

    resizer = ImageResizer()

    image_data = Image.new("RGB", (2400, 3200))
    in_memory_bytes = io.BytesIO()

    # Keep exif data
    image_data.save(
        in_memory_bytes,
        format="jpeg",
        exif=image_data.getexif(),
    )

    # pylint: disable=protected-access
    thumbnail = resizer._create_thumbnail(in_memory_bytes.getvalue(), "jpeg")
    # pylint: enable=protected-access

    assert isinstance(thumbnail, io.BytesIO)

    resized_image = Image.open(thumbnail)

    assert resized_image.size == (1200, 1600)

    assert "File Size in MegaBytes is 0.01" in caplog.text

    assert (
        "Image is larger than the thumbnail size,so resizing with factor 2.0"
        in caplog.text
    )


def test_image_resizer_create_thumbnail_for_already_small_image(
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Test _create_thumbnail method of ImageResizer class with small image.

    As the image is already smaller than the thumbnail size, the image
    should not be resized but returned in the same size.

    """
    resizer = ImageResizer()

    image_data = Image.new("RGB", (1100, 1600))
    in_memory_bytes = io.BytesIO()

    # Keep exif data
    image_data.save(
        in_memory_bytes,
        format="jpeg",
        exif=image_data.getexif(),
    )

    # pylint: disable=protected-access
    thumbnail = resizer._create_thumbnail(in_memory_bytes.getvalue(), "jpeg")
    # pylint: enable=protected-access

    assert isinstance(thumbnail, io.BytesIO)

    resized_image = Image.open(thumbnail)

    assert resized_image.format == "JPEG"

    assert resized_image.size == (1100, 1600)

    assert "File Size in MegaBytes is 0.01" in caplog.text

    assert (
        "Image is smaller than the thumbnail size,"
        "so keeping the original as small image" in caplog.text
    )

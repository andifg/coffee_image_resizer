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

    resizer.resize_image(b"image_data")

    mock_create_thumbnail.assert_called_once_with(b"image_data")


def test_image_resizer_create_thumbnail_image(
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Test _create_thumbnail method of ImageResizer class with image."""

    resizer = ImageResizer()

    image_data = Image.new("RGB", (4000, 4000))
    in_memory_bytes = io.BytesIO()

    image_data.save(in_memory_bytes, format="JPEG")

    # pylint: disable=protected-access
    thumbnail = resizer._create_thumbnail(in_memory_bytes.getvalue())
    # pylint: enable=protected-access

    assert isinstance(thumbnail, io.BytesIO)

    resized_image = Image.open(thumbnail)

    assert resized_image.size == (1200, 1200)

    assert "File Size in MegaBytes is 0.01" in caplog.text

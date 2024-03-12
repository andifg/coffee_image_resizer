import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from resize.kafka.consumer import ResizerConsumer
from resize.main import ImageResizer
from resize.s3.service import S3Service


@patch("resize.s3.service.S3Service")
@patch.object(ResizerConsumer, "consume", new_callable=AsyncMock)
@pytest.mark.asyncio
async def test_image_resizer_run(
    consume_mock: AsyncMock,
    s3_mock: MagicMock,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Test the run method of the ImageResizer class."""

    consume_mock.return_value = asyncio.sleep(0)

    s3_service_mock = MagicMock()

    s3_mock.return_value = s3_service_mock

    # Create an instance of ImageResizer
    image_resizer = ImageResizer()

    # Call the run method
    await image_resizer.run()

    consume_mock.assert_awaited_once()

    assert "Stopped resizer" in caplog.text

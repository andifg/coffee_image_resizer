import asyncio
from unittest.mock import MagicMock, patch

import pytest

from resize.exceptions import ObjectNotFoundError
from resize.resizer.image_resizer import ImageResizer
from resize.s3.object import ObjectCRUD
from resize.s3.service import S3Service


@pytest.mark.asyncio
async def test_s3_service_init() -> None:
    """Test the initialization of the S3Service class."""

    s3_service = S3Service()
    assert s3_service.object_crud
    assert s3_service.image_resizer


@patch.object(ObjectCRUD, "create", return_value=None)
@patch.object(ImageResizer, "resize_image", return_value=b"test_value_small")
@patch.object(ObjectCRUD, "read", return_value=(b"test_value", "TFLPU"))
@pytest.mark.asyncio
async def test_s3_service_handle_kafka_message(
    object_crud_read_mock: MagicMock,
    image_resizer_mock: MagicMock,
    object_crud_create_mock: MagicMock,
) -> None:
    """Test the handle_kafka_message method of the S3Service class.

    This test checks if the handle_kafka_message method of the S3Service class
    calls the read and create methods of the ObjectCRUD class and the
    resize_image method of the ImageResizer class with the correct arguments.
    """

    s3_service = S3Service()
    await s3_service.handle_kafka_message(
        "bucket/prefix/image-id", "test_value"
    )

    object_crud_read_mock.assert_called_once_with(object_path="prefix/image-id")
    image_resizer_mock.assert_called_once_with(b"test_value", "TFLPU")
    object_crud_create_mock.assert_called_once_with(
        filename="image-id",
        file=b"test_value_small",
        file_type="TFLPU",
        prefix="small",
    )


@patch.object(ObjectCRUD, "create", return_value=None)
@patch.object(ImageResizer, "resize_image")
@patch.object(ObjectCRUD, "read", return_value=(b"test_value", "TFLPU"))
@pytest.mark.asyncio
async def test_s3_service_handle_kafka_message_object_not_found(
    object_crud_read_mock: MagicMock,
    image_resizer_mock: MagicMock,
    object_crud_create_mock: MagicMock,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Test handle_kafka_message with unknown object.

    This test checks if the handle_kafka_message method of the S3Service class
    handles the ObjectNotFoundError exception correctly.
    """

    s3_service = S3Service()
    object_crud_read_mock.side_effect = ObjectNotFoundError("Object not found")
    await s3_service.handle_kafka_message(
        "bucket/prefix/image-id", "test_value"
    )

    object_crud_read_mock.assert_called_once_with(object_path="prefix/image-id")
    image_resizer_mock.assert_not_called()
    object_crud_create_mock.assert_not_called()

    assert (
        "Object with key bucket/prefix/image-id not found in S3" in caplog.text
    )

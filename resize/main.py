import logging

from resize.config.log_levels import log_levels
from resize.kafka.consumer import ResizerConsumer
from resize.s3.service import S3Service
from resize.settings import settings

logging.basicConfig(level=log_levels.get(settings.log_level, logging.INFO))


class ImageResizer:
    """Class responsible managing image resizing triggered by kafka message."""

    def __init__(self) -> None:
        self.s3_service = S3Service()

    async def run(self) -> None:
        """Run the resizer service by consuming messages.

        This method creates a ResizerConsumer instance and hands over the
        S3Service as a message handler. The consumer then processes messages
        from the Kafka topic and calls the handle_kafka_message method of the
        S3Service for each message.
        """
        consumer = ResizerConsumer(message_handler=self.s3_service)
        try:
            await consumer.consume()
        finally:
            await consumer.consumer.stop()
            logging.info("Stopped resizer")

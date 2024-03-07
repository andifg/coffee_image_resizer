import logging
from resize.kafka.consumer import ResizerConsumer
from resize.s3.service import S3Service
from resize.settings import settings
from resize.config.log_levels import log_levels

logging.basicConfig(level=log_levels.get(settings.log_level, logging.INFO))


class ImageResizer:

    def __init__(self) -> None:
        self.s3_service = S3Service()

    async def run(self):
        consumer = ResizerConsumer(message_handler=self.s3_service)
        try:
            await consumer.consume()
        finally:
            await consumer.consumer.stop()
            logging.info("Stopp resizer")

from resize.kafka.consumer import ResizerConsumer
from resize.s3.service import S3Service


class ImageResizer:

    def __init__(self) -> None:
        self.s3_service = S3Service()

    async def run(self):
        print("running")
        consumer = ResizerConsumer(message_handler=self.s3_service)
        await consumer.consume()
        print("done")

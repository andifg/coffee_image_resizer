import json
import logging

from aiokafka import AIOKafkaConsumer, ConsumerRecord

from resize.settings import settings
from resize.types import MessageHandler

logger = logging.getLogger("aiokafka")
logger.setLevel(logging.INFO)


class Consumer:
    def __init__(self, message_handler: MessageHandler):
        self.consumer = AIOKafkaConsumer(
            settings.kafka_topic,
            bootstrap_servers=settings.kafka_bootstrap_servers,
            value_deserializer=lambda v: json.loads(v),
            key_deserializer=lambda v: v.decode("utf-8"),
            group_id=settings.kafka_consumer_group,
            enable_auto_commit=False,
            auto_offset_reset="earliest",
        )
        self.message_handler = message_handler

    async def consume(self) -> None:
        await self.consumer.start()
        logging.info("consumer started")
        async for msg in self.consumer:
            await self._process_message(msg)
            await self.consumer.commit()
            logging.info("Handled message and committed")

    async def _process_message(self, msg: ConsumerRecord) -> None:
        raise NotImplementedError("Not implemented")


class ResizerConsumer(Consumer):
    def __init__(self, message_handler: MessageHandler):
        super().__init__(message_handler=message_handler)

    async def _process_message(self, msg: ConsumerRecord) -> None:
        logging.info(
            "consumed: %s %s %s %s %s %s",
            msg.topic,
            msg.partition,
            msg.offset,
            msg.key,
            msg.value,
            msg.timestamp,
        )
        await self.message_handler.handle_kafka_message(msg.key, msg.value)

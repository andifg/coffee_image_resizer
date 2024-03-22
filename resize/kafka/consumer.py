import json
import logging

from aiokafka import AIOKafkaConsumer, ConsumerRecord
from aiokafka.helpers import create_ssl_context

from resize.settings import settings
from resize.types import MessageHandler


class Consumer:
    """A class representing a Kafka consumer."""

    def __init__(self, message_handler: MessageHandler):
        """
        Initializes a new instance of the Consumer class.

        Args:
            message_handler (MessageHandler): The message handler used to
                process incoming messages.
        """
        security_context = None

        if settings.kafka_ssl_protocol == "SSL":
            security_context = create_ssl_context(
                cafile=settings.kafka_ssl_cafile,
            )

        self.consumer = AIOKafkaConsumer(
            settings.kafka_topic,
            bootstrap_servers=settings.kafka_bootstrap_servers,
            value_deserializer=lambda v: json.loads(v),
            key_deserializer=lambda v: v.decode("utf-8"),
            group_id=settings.kafka_consumer_group,
            enable_auto_commit=False,
            auto_offset_reset="earliest",
            security_protocol=settings.kafka_ssl_protocol.value,
            ssl_context=security_context,
        )
        self.message_handler = message_handler

    async def consume(self) -> None:
        """Starts consuming messages from the Kafka topic.

        This method starts the consumer and processes messages as they arrive
        by calling the _process_message method.
        """
        await self.consumer.start()
        logging.info("consumer started")
        async for msg in self.consumer:
            await self._process_message(msg)
            await self.consumer.commit()
            logging.info("Handled message and committed")

    async def _process_message(self, msg: ConsumerRecord) -> None:
        """Processes a single message.

        This method needs to be implemented in a subclass to handle incoming
            messages.

        Args:
            msg (ConsumerRecord): The message to be processed.

        Raises:
            NotImplementedError: If the method is not implemented in a subclass.
        """
        raise NotImplementedError("Not implemented")


class ResizerConsumer(Consumer):
    """Kafka Consumer for the Resizer service.

    Args:
        message_handler (MessageHandler): The message handler object responsible
            for handling Kafka messages.

    """

    def __init__(self, message_handler: MessageHandler):
        super().__init__(message_handler=message_handler)

    async def _process_message(self, msg: ConsumerRecord) -> None:
        """Process a Kafka message.

        Args:
            msg (ConsumerRecord): The Kafka message to be processed.
        """
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

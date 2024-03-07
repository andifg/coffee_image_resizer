import json
from typing import Protocol

from aiokafka import AIOKafkaConsumer, ConsumerRecord

class MessageHandler(Protocol):
    async def handle_kafka_message(self, key: str, value: str):
        pass


class Consumer:
    def __init__(self, message_handler: MessageHandler):
        self.consumer = AIOKafkaConsumer(
            "coffee-images",
            bootstrap_servers="localhost:9094",
            value_deserializer=self.json_deserializer(),
            key_deserializer=lambda v: v.decode("utf-8"),
            group_id="my-group",
        )
        self.message_handler = message_handler

    async def consume(self):
        await self.consumer.start()
        try:
            # Consume messages
            async for msg in self.consumer:
                await self._process_message(msg)
        finally:
            # Will leave consumer group; perform autocommit if enabled.
            print("closing consumer")
            await self.consumer.stop()

    async def _process_message(self):
        raise NotImplementedError("Not implemented")

    def json_deserializer(self):
        return lambda v: json.loads(v)


class ResizerConsumer(Consumer):
    def __init__(self, message_handler: MessageHandler):
        super().__init__(message_handler=message_handler)

    async def _process_message(self, msg: ConsumerRecord):
        print(
            "consumed: ",
            msg.topic,
            msg.partition,
            msg.offset,
            msg.key,
            msg.value,
            msg.timestamp,
        )
        await self.message_handler.handle_kafka_message(msg.key, msg.value)

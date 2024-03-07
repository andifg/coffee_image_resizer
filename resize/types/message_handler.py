from typing import Protocol

class MessageHandler(Protocol):
    async def handle_kafka_message(self, key: str, value: str):
        pass
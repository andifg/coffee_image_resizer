from typing import Protocol


class MessageHandler(Protocol):
    """Protocoll Class for Kafka message handler."""

    async def handle_kafka_message(self, key: str, value: str) -> None:
        """Handles a Kafka message.

        Args:
            key (str): The key of the Kafka message.
            value (str): The value of the Kafka message.
        """

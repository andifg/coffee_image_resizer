import asyncio
import json
from unittest.mock import AsyncMock

import pytest

from resize.kafka.consumer import ResizerConsumer
from tests.conftest import TestKafkaSession


@pytest.mark.asyncio
async def test_consumer_consume(
    init_kakfa: TestKafkaSession, caplog: pytest.LogCaptureFixture
) -> None:
    """Test kafka message consumption.

    This test checks if the consume method of the ResizerConsumer class is working as expected.
    It sends a message to the Kafka topic, starts the consumer, and checks if the message is consumed correctly.
    The test also checks if the appropriate log messages are generated.

    Args:
        init_kakfa (TestKafkaSession): A fixture that initializes a Kafka session for testing.
        caplog (pytest.LogCaptureFixture): A fixture that captures log messages for testing.
    """

    handler_mock = AsyncMock()

    consumer = ResizerConsumer(message_handler=handler_mock)

    init_kakfa.sync_producer.send(
        "coffee-images", key="origin/12345678", value=json.dumps({"a": "b"})
    )

    consume_task = asyncio.create_task(consumer.consume())

    try:
        await asyncio.gather(
            consume_task,
            _wait_and_cancel_task(
                handler_mock.handle_kafka_message, consume_task
            ),
        )

    except asyncio.CancelledError:
        print("Task cancelled")

    finally:
        print("Stopping consumer")
        await consumer.consumer.stop()

    handler_mock.handle_kafka_message.assert_awaited_once_with(
        "origin/12345678", {"a": "b"}
    )

    assert "consumer started" in caplog.text
    assert "Handled message and committed" in caplog.text
    assert (
        "consumed: coffee-images 0 0 origin/12345678 {'a': 'b'}" in caplog.text
    )


async def _wait_and_cancel_task(spy: AsyncMock, task: asyncio.Task) -> None:
    for _ in range(100):
        print("Checking spy")
        if spy.called:
            print("Spy called")
            task.cancel()
        await asyncio.sleep(2)

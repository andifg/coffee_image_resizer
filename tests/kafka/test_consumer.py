import asyncio
import json
from unittest.mock import AsyncMock

import pytest

from resize.kafka.consumer import ResizerConsumer
from tests.conftest import TestKafkaSession


@pytest.mark.asyncio
async def test_consumer_consume(init_kakfa: TestKafkaSession):

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


async def _wait_and_cancel_task(spy: AsyncMock, task: asyncio.Task) -> None:
    for _ in range(100):
        print("Checking spy")
        if spy.called:
            print("Spy called")
            task.cancel()
        await asyncio.sleep(2)

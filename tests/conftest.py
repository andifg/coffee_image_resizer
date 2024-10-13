import logging
from dataclasses import dataclass
from typing import AsyncGenerator

import pytest
import pytest_asyncio
from kafka import KafkaProducer
from testcontainers.kafka import RedpandaContainer

from resize.settings import settings

logging.getLogger().setLevel(logging.DEBUG)

logging.getLogger("kafka").setLevel(logging.INFO)


@dataclass
class TestKafkaSession:
    """
    Represents a test Kafka session.

    Attributes:
        sync_producer (KafkaProducer): The synchronous Kafka producer.
        __test__ (bool): Flag indicating whether the class should be
            considered for testing.
    """

    sync_producer: KafkaProducer
    __test__: bool = False


@pytest_asyncio.fixture(name="kafka_service")
async def fixture_kafka_service() -> AsyncGenerator[str, None]:
    """Fixture to wait for Kafka dev container to become responsive.

    Args:
        docker_ip (str): The IP address of the Docker container.
        docker_services (Services): The Docker services.

    Returns:
        str: The bootstrap server address.

    Raises:
        TimeoutError: If the Kafka service does not become responsive within
            the timeout period.
    """

    with RedpandaContainer() as redpanda:
        connection = redpanda.get_bootstrap_server()

        print(connection)
        yield connection


@pytest_asyncio.fixture()
async def init_kakfa(
    monkeypatch: pytest.MonkeyPatch, kafka_service: str
) -> AsyncGenerator:
    """Yield a Kafka test sesson.

    Args:
        monkeypatch (pytest.MonkeyPatch): The pytest monkeypatch fixture.
        kafka_service (str): The Kafka service to connect to.

    Yields:
        TestKafkaSession: A test Kafka session object.
    """
    sync_producer: KafkaProducer = KafkaProducer(
        bootstrap_servers=kafka_service,
        value_serializer=lambda v: v.encode("utf-8"),
        key_serializer=lambda v: v.encode("utf-8"),
    )

    monkeypatch.setattr(settings, "kafka_bootstrap_servers", kafka_service)

    yield TestKafkaSession(sync_producer=sync_producer)

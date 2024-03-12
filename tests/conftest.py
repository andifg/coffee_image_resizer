import logging
from dataclasses import dataclass
from typing import AsyncGenerator, Generator
from uuid import UUID

import pytest
import pytest_asyncio
from kafka import KafkaConsumer, KafkaProducer
from kafka.errors import UnrecognizedBrokerVersion
from pytest_docker.plugin import Services

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
async def fixture_kafka_service(
    docker_ip: str, docker_services: Services
) -> str:
    """ Fixture to wait for Kafka dev container to become responsive.

    Args:
        docker_ip (str): The IP address of the Docker container.
        docker_services (Services): The Docker services.

    Returns:
        str: The bootstrap server address.

    Raises:
        TimeoutError: If the Kafka service does not become responsive within
            the timeout period.
    """
    port = docker_services.port_for("kafka", 9095)
    bootstrap_server = f"{docker_ip}:{port}"
    docker_services.wait_until_responsive(
        timeout=30.0, pause=0.1, check=lambda: test_kafka(bootstrap_server)
    )
    return bootstrap_server


@pytest_asyncio.fixture()
async def init_kakfa(
    monkeypatch: pytest.MonkeyPatch, kafka_service: str
) -> AsyncGenerator:
    """ Yield a Kafka test sesson.

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


def test_kafka(bootstrap_server: str) -> bool:
    """ Test the connection to a Kafka server.

    Args:
        bootstrap_server (str): The address of the Kafka bootstrap server.

    Returns:
        bool: True if the connection is successful, False otherwise.
    """
    print("Try kafka connection")

    print("BOOOTSTRAP ", bootstrap_server)
    try:
        consumer = KafkaConsumer(
            group_id="test", bootstrap_servers=[bootstrap_server]
        )
        if consumer.bootstrap_connected():
            return True
        else:
            return False
    except UnrecognizedBrokerVersion as e:
        return False
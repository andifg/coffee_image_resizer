import logging
from dataclasses import dataclass
from typing import AsyncGenerator

import pytest
import pytest_asyncio
from kafka import KafkaConsumer, KafkaProducer
from kafka.errors import NoBrokersAvailable
from testcontainers.core.container import DockerContainer
from testcontainers.core.waiting_utils import wait_for_logs  # type: ignore

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

    kafka_testcontainer = (
        DockerContainer("docker.io/bitnami/kafka:3.6")
        .with_bind_ports(9095, 9095)
        .with_env("KAFKA_CFG_NODE_ID", "0")
        .with_env("KAFKA_CFG_PROCESS_ROLES", "controller,broker")
        .with_env("KAFKA_CFG_CONTROLLER_QUORUM_VOTERS", "0@0.0.0.0:9093")
        .with_env(
            "KAFKA_CFG_LISTENERS",
            "PLAINTEXT://:9092,CONTROLLER://:9093,EXTERNAL://0.0.0.0:9095",
        )
        .with_env(
            "KAFKA_CFG_ADVERTISED_LISTENERS",
            "PLAINTEXT://:9092,EXTERNAL://127.0.0.1:9095",
        )
        .with_env(
            "KAFKA_CFG_LISTENER_SECURITY_PROTOCOL_MAP",
            "CONTROLLER:PLAINTEXT,PLAINTEXT:PLAINTEXT,EXTERNAL:PLAINTEXT",
        )
        .with_env("KAFKA_CFG_CONTROLLER_LISTENER_NAMES", "CONTROLLER")
        .with_env("KAFKA_CFG_INTER_BROKER_LISTENER_NAME", "PLAINTEXT")
    )

    with kafka_testcontainer as container:
        host_ip = container.get_container_host_ip()
        exposed_port = container.get_exposed_port(9095)
        bootstrap_server = f"{host_ip}:{exposed_port}"
        wait_for_logs(
            container=container, predicate="Kafka Server started", timeout=15
        )

        yield bootstrap_server

    # port = docker_services.port_for("kafka", 9095)
    # bootstrap_server = f"{docker_ip}:{port}"
    # docker_services.wait_until_responsive(
    #     timeout=30.0, pause=0.1, check=lambda: test_kafka(bootstrap_server)
    # )
    # return bootstrap_server


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


def test_kafka(bootstrap_server: str) -> bool:
    """Test the connection to a Kafka server.

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
        print("Connected to Kafka")
        consumer.bootstrap_connected()
        return True

    except (NoBrokersAvailable, ValueError) as e:
        print(e)
        return False

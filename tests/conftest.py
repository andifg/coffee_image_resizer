import logging
from dataclasses import dataclass
from typing import AsyncGenerator, Generator
from uuid import UUID

import pytest
import pytest_asyncio
from kafka import KafkaConsumer, KafkaProducer
from pytest_docker.plugin import Services

from resize.settings import settings

logging.getLogger().setLevel(logging.DEBUG)

logging.getLogger("kafka").setLevel(logging.INFO)


@dataclass
class TestKafkaSession:
    sync_producer: KafkaProducer
    __test__: bool = False


@pytest_asyncio.fixture(name="kafka_service")
async def fixture_kafka_service(
    docker_ip: str, docker_services: Services
) -> str:
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

    sync_producer: KafkaProducer = KafkaProducer(
        bootstrap_servers=kafka_service,
        value_serializer=lambda v: v.encode("utf-8"),
        key_serializer=lambda v: v.encode("utf-8"),
    )

    monkeypatch.setattr(settings, "kafka_bootstrap_servers", kafka_service)

    yield TestKafkaSession(sync_producer=sync_producer)
    cleanup_kafka_topic(sync_producer)


def test_kafka(bootstrap_server: str) -> bool:
    print("Try kafka connection")

    print("BOOOTSTRAP ", bootstrap_server)
    try:
        consumer = KafkaConsumer(
            group_id="test", bootstrap_servers=[bootstrap_server]
        )
        if consumer.bootstrap_connected():
            return True
    except Exception as e:
        return False


# To be done
def cleanup_kafka_topic(producer: KafkaProducer) -> None:
    # Empty the topic
    producer.flush()

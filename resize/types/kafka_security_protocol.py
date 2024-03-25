from enum import Enum


class KafkaSecurityProtocol(Enum):
    PLAINTEXT = "PLAINTEXT"
    SASL_SSL = "SASL_SSL"

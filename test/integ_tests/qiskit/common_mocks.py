from unittest.mock import patch

from qiskit import user_config
from qiskit_braket_provider import BraketAwsBackend

EMPTY_QUEUE_INFO = [
    {"queue": "QUANTUM_TASKS_QUEUE", "queueSize": "0", "queuePriority": "Normal"},
    {"queue": "QUANTUM_TASKS_QUEUE", "queueSize": "0", "queuePriority": "Priority"},
    {"queue": "JOBS_QUEUE", "queueSize": "0"},
]


def prefer_text_circuit_drawer():
    qiskit_config = user_config.get_config()
    if qiskit_config:
        user_config.set_config("circuit_drawer", "text")


def patch_braket_qubit_labels():
    patch.object(
        BraketAwsBackend,
        "qubit_labels",
        property(
            lambda self: (
                tuple(sorted(self._device.topology_graph.nodes))
                if self._device.topology_graph
                else None
            )
        ),
        create=True,
    ).start()


def device_summary(device_arn, device_name, device_type, provider_name):
    return {
        "deviceArn": device_arn,
        "deviceName": device_name,
        "deviceType": device_type,
        "deviceStatus": "ONLINE",
        "providerName": provider_name,
    }

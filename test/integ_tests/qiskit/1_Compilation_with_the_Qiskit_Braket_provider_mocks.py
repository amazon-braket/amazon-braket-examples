from unittest.mock import patch

from qiskit_braket_provider import BraketAwsBackend


def pre_run_inject(mock_utils):
    mocker = mock_utils.Mocker()
    mock_utils.mock_default_device_calls(mocker)
    mocker.set_get_device_result({
        "deviceType": "QPU",
        "deviceCapabilities": mock_utils.read_file(
            "garnet_device_capabilities_without_programset.json", __file__
        ),
    })
    mocker.set_task_result_return(mock_utils.read_file("result_compiled.json", __file__))
    
    # Ensure qubit_labels property exists
    patch.object(
        BraketAwsBackend, 'qubit_labels', property(lambda self: tuple(sorted(self._device.topology_graph.nodes)) if self._device.topology_graph else None), create=True).start()

def post_run(tb):
    pass

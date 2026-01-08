import os
import random
import sys
from unittest.mock import MagicMock, PropertyMock, patch

from braket.aws.aws_device import AwsDevice
from braket.program_sets import ProgramSet

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'examples', 'error_mitigation')))

from tools.mitigation_tools import SparseReadoutMitigation  # type: ignore


def pre_run_inject(mock_utils):
    mocker = mock_utils.Mocker()
    mock_utils.mock_default_device_calls(mocker)    
    mocker.set_get_device_result(
        {
            "deviceType": "QPU",
            "deviceCapabilities": mock_utils.read_file("rigetti_device_capabilities.json", __file__),
        },
    )
    
    patch.object(AwsDevice, 'provider_name', PropertyMock(return_value='rigetti'), create=True).start()
    patch.object(AwsDevice, 'gate_calibrations', PropertyMock(return_value=None), create=True).start()
    
    original_run = AwsDevice.run

    def mock_run(self,program, *args, **kwargs):
        if isinstance(program, ProgramSet):
            mock_result = MagicMock()
            mock_results = []
            for _ in range(len(program)):
                mock_entry = MagicMock()
                mock_entry.__getitem__.return_value = MagicMock(counts={'00': 50, '11': 50}, probabilities = {"00":0.5, "11":0.5,})
                mock_entry.entries = [MagicMock(counts={'00': 50, '11': 50}, probabilities = {"00":0.5, "11":0.5,})]
                mock_results.append(mock_entry)
            mock_result.result.return_value = mock_results
            return mock_result
        return original_run(self,program, *args, **kwargs)
    
    def mock_readout(*args,**kwargs):
        return 0.1*random.random()

    patch.object(AwsDevice, "run", mock_run).start()
    patch.object(SparseReadoutMitigation, "process_single", mock_readout).start()
    
    mock_tracker = MagicMock()
    mock_tracker.qpu_tasks_cost.return_value = 100.0
    mock_tracker.start.return_value = None
    patch('braket.tracking.Tracker', return_value=mock_tracker).start()

def post_run(tb):
    pass

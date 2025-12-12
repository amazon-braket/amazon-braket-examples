from unittest.mock import patch

def pre_run_inject(mock_utils):
    mocker = mock_utils.Mocker()
    mock_utils.mock_default_device_calls(mocker)
    mocker.set_get_device_result(
        {
            "deviceType": "QPU",
            "deviceCapabilities": mock_utils.read_file(
                "garnet_device_capabilities_without_programset.json",
                __file__,
            ),
        },
    )

    qasm = "OPENQASM 3.0;\nbit[8] c;\n#pragma braket verbatim\nbox {\nprx(0.5*pi,1.5*pi) $4;\nprx(0.5*pi,1.5*pi) $5;\nprx(0.5*pi,1.5*pi) $9;\nprx(0.5*pi,1.5*pi) $10;\nprx(0.5*pi,1.5*pi) $11;\nprx(0.5*pi,1.5*pi) $14;\nprx(0.5*pi,1.5*pi) $15;\nprx(0.5*pi,1.5*pi) $16;\ncz $10,$11;\nprx(0.5*pi,0.5*pi) $11;\ncz $11,$16;\nprx(0.5*pi,0.5*pi) $16;\ncz $16,$15;\nprx(0.5*pi,0.5*pi) $15;\ncz $15,$14;\nprx(0.5*pi,0.5*pi) $14;\ncz $14,$9;\nprx(0.5*pi,0.5*pi) $9;\ncz $9,$4;\nprx(0.5*pi,0.5*pi) $4;\ncz $4,$5;\nprx(0.5*pi,0.5*pi) $5;\n}\nc[0] = measure $10;\nc[1] = measure $11;\nc[2] = measure $16;\nc[3] = measure $15;\nc[4] = measure $14;\nc[5] = measure $9;\nc[6] = measure $4;\nc[7] = measure $5;"
    with patch('braket.aws.aws_quantum_task_result.AwsQuantumTaskResult.get_compiled_circuit') as mock_compiled:
        mock_compiled.return_value = qasm

# In the mock file
def pre_run_inject(mock_utils):
    mocker = mock_utils.Mocker()
    mock_utils.mock_default_device_calls(mocker)
    
    # Mock compiled circuit with valid OpenQASM
    valid_qasm = """OPENQASM 3.0;
qubit[2] q;
h q[0];
cx q[0], q[1];"""
    
    # Mock the get_compiled_circuit method
    mocker.set_task_result_return('{"compiledProgram": "' + valid_qasm + '"}')


def post_run(tb):
    pass

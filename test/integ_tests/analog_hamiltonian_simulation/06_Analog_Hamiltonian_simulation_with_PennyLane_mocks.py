import re


def pre_run_inject(mock_utils):
    mocker = mock_utils.Mocker()
    mock_utils.mock_default_device_calls(mocker)
    mocker.set_get_device_result(
        {
            "deviceType": "QPU",
            "deviceCapabilities": mock_utils.read_file("ahs_device_capabilities.json", __file__),
        },
    )
    mocker.set_task_result_return(mock_utils.read_file("ahs_results_06.json", __file__))


def modify_cells(cells):
    # The dominant cost of this notebook is the local PennyLane/JAX pulse-level
    # optimization loop (~40s of ~53s), not any Braket call. The integ test only
    # verifies that cells execute without error output, so reducing the epoch
    # count and shot count is safe and leaves the published notebook untouched.
    for cell in cells:
        if cell.get("cell_type") != "code":
            continue
        src = cell["source"]
        src = re.sub(r"n_epochs = 10\b", "n_epochs = 3", src)
        src = re.sub(r"shots = 1000\b", "shots = 100", src)
        cell["source"] = src


def post_run(tb):
    pass

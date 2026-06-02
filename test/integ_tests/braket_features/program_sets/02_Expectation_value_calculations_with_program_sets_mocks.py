import re


def pre_run_inject(mock_utils):
    mocker = mock_utils.Mocker()
    mock_utils.mock_default_device_calls(mocker)


def modify_cells(cells):
    for cell in cells:
        if cell.get("cell_type") != "code":
            continue
        src = cell["source"]
        src = re.sub(r"num_trials = 100", "num_trials = 3", src)
        src = re.sub(r"total_shots = 10000", "total_shots = 100", src)
        cell["source"] = src


def post_run(tb):
    pass

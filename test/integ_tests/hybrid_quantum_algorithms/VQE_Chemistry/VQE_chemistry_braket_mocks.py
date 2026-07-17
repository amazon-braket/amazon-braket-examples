import re


def pre_run_inject(mock_utils):
    mocker = mock_utils.Mocker()
    mock_utils.mock_default_device_calls(mocker)


def modify_cells(cells):
    # This notebook scans a potential-energy surface: n_configs bond lengths x
    # n_theta grid points, each doing a LocalSimulator run (all local compute, no
    # Braket calls). The integ test only checks that cells execute without error,
    # so a coarser scan (6 bond lengths x 6 theta = 36 runs instead of 28 x 24 =
    # 672) is safe and leaves the published notebook untouched.
    for cell in cells:
        if cell.get("cell_type") != "code":
            continue
        src = cell["source"]
        src = re.sub(r"step=0\.1\)", "step=0.5)", src)
        src = re.sub(r"n_theta = 24\b", "n_theta = 6", src)
        cell["source"] = src


def post_run(tb):
    pass

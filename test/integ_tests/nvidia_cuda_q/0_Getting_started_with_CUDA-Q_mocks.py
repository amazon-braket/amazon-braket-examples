def pre_run_inject(mock_utils):
    mocker = mock_utils.Mocker()
    mock_utils.mock_default_device_calls(mocker)
    # In ALL mode (GitHub CI), cudaq.set_target("braket") would fail without
    # AWS credentials. Patch it to use emulate=True so it runs locally via
    # the CUDA-Q simulator. In LEAST mode (NBI pipeline), the real Braket
    # path is tested with MOCK_DEVICE_CONFIG handling device routing.
    if mock_utils.Mocker.mock_level == "ALL":
        import cudaq
        _real = cudaq.set_target
        def _wrapped(*a, **kw):
            kw.setdefault("emulate", True)
            return _real(*a, **kw)
        cudaq.set_target = _wrapped


def post_run(tb):
    pass

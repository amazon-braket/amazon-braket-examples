def pre_run_inject(mock_utils):
    mocker = mock_utils.Mocker()
    mock_utils.mock_default_device_calls(mocker)

    # Return device-specific capabilities based on ARN so topology graphs
    # match what the notebook expects (IQM has hardcoded node positions 1-20,
    # IonQ is fully connected, Rigetti is a 107-node lattice).
    rigetti_caps = mock_utils.read_file("rigetti_device_capabilities.json")
    ionq_caps = mock_utils.read_file("ionq_forte_enterprise_device_capabilities.json")
    iqm_caps = mock_utils.read_file("iqm_garnet_device_capabilities.json")

    def get_device_by_arn(*args, **kwargs):
        arn = args[0] if args else kwargs.get("deviceArn", "")
        if "iqm" in arn.lower():
            caps, provider = iqm_caps, "IQM"
        elif "ionq" in arn.lower():
            caps, provider = ionq_caps, "IonQ"
        else:
            caps, provider = rigetti_caps, "Rigetti"
        return {
            "deviceType": "QPU",
            "providerName": provider,
            "deviceCapabilities": caps,
            "deviceQueueInfo": [
                {"queue": "QUANTUM_TASKS_QUEUE", "queueSize": "0", "queuePriority": "Normal"},
                {"queue": "QUANTUM_TASKS_QUEUE", "queueSize": "0", "queuePriority": "Priority"},
                {"queue": "JOBS_QUEUE", "queueSize": "0"},
            ],
        }

    mocker._wrapper.boto_client.get_device.side_effect = get_device_by_arn
    mocker.set_task_result_return(mock_utils.read_file("default_results.json"))


def post_run(tb):
    pass

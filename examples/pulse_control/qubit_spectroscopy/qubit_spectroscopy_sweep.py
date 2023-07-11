#! Braket jobs

import json
import os
import numpy as np

from braket.aws import AwsDevice
from braket.parametric import FreeParameter
from braket.pulse import PulseSequence, GaussianWaveform, ConstantWaveform
from braket.jobs import save_job_result
from braket.jobs.metrics import log_metric
from braket.tracking import Tracker

cost_tracker = Tracker().start()

print("Test job started!")

# Use the device declared in the creation script
device_arn = os.environ["AMZN_BRAKET_DEVICE_ARN"]
device = AwsDevice(device_arn)

# Load the Hybrid Job hyperparameters
hp_file = os.environ["AMZN_BRAKET_HP_FILE"]
with open(hp_file, "r") as f:
    hyperparams = json.load(f)

qubit = hyperparams.get("qubit", None)
assert qubit is not None
experiment_configuration = {
    "arn:aws:braket:us-west-1::device/qpu/rigetti/Aspen-M-3": {
        "drive_frame": f"q{qubit}_rf_frame",
        "readout_frame": f"q{qubit}_ro_rx_frame",
        "spectroscopy_wf": GaussianWaveform(100e-9, 25e-9, 0.1, True),
    },
    "arn:aws:braket:eu-west-2::device/qpu/oqc/Lucy": {
        "drive_frame": f"q{qubit}_drive",
        "readout_frame": f"r{qubit}_measure",
        "spectroscopy_wf": ConstantWaveform(25e-9, 0.03),
    },
}
drive_frame = device.frames[experiment_configuration[device_arn]["drive_frame"]]
readout_frame = device.frames[experiment_configuration[device_arn]["readout_frame"]]
waveform = GaussianWaveform(100e-9, 25e-9, 0.1, True)

N_steps = int(hyperparams.get("N_steps", 25))
N_shots = int(hyperparams.get("N_shots", 100))
span = (
    75e6
    if not ("frequency_start" in hyperparams and "frequency_stop" in hyperparams)
    else None
)
frequency_start = float(
    hyperparams.get("frequency_start", drive_frame.frequency - span / 2)
)
frequency_stop = float(
    hyperparams.get("frequency_stop", drive_frame.frequency + span / 2)
)

frequency_free_parameter = FreeParameter("frequency")
pulse_sequence = (
    PulseSequence()
    .set_frequency(drive_frame, frequency_free_parameter)
    .play(drive_frame, waveform)
    .capture_v0(readout_frame)
)

frequencies = np.linspace(frequency_start, frequency_stop, N_steps)
populations = []

for i, frequency in enumerate(frequencies):
    task = device.run(
        pulse_sequence(frequency=frequency),
        shots=N_shots,
        tags={"frequency": str(frequency)},
    )
    counts = task.result().measurement_counts

    population_zero = counts["0"] / N_shots
    populations.append(population_zero)

    braket_tasks_cost = float(
        cost_tracker.simulator_tasks_cost() + cost_tracker.qpu_tasks_cost()
    )
    log_metric(
        metric_name="braket_tasks_cost", value=braket_tasks_cost, iteration_number=i
    )

# Save the variables of interest so that we can access later
save_job_result(
    {
        "populations in |0>": populations,
        "frequencies": frequencies.tolist(),
        "task summary": cost_tracker.quantum_tasks_statistics(),
        "estimated cost": braket_tasks_cost,
    }
)

print("Test job completed!")

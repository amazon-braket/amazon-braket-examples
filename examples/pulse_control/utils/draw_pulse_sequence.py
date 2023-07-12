from braket.pulse.pulse_sequence import PulseSequence
from braket.pulse.waveforms import ArbitraryWaveform, Waveform

import numpy as np
import matplotlib.pyplot as plt

def draw_waveform(waveform: Waveform, dt: float):
    if isinstance(waveform, ArbitraryWaveform):
        plt.plot(np.arange(0, len(waveform.amplitudes))*dt*1e9, [amp.real for amp in waveform.amplitudes])
    else:
        y=waveform.sample(dt)
        plt.plot(np.arange(0, len(y))*dt*1e9, y)

    plt.xlabel('Time (ns)')
    plt.ylabel('Amplitude (a. u.)')

def draw(pulse_sequence: PulseSequence):
    data = pulse_sequence.to_time_trace()
    for frame_id in data.amplitudes:
        f, ax = plt.subplots(nrows=3, sharex=True)
        f.subplots_adjust(hspace=0)

        ax[0].set_title(frame_id)
        ax[0].plot(
            data.amplitudes[frame_id].times(),
            np.real(data.amplitudes[frame_id].values()),
            label="Real",
        )
        ax[0].plot(
            data.amplitudes[frame_id].times(),
            np.imag(data.amplitudes[frame_id].values()),
            label="Imag",
        )
        ax[0].set_ylabel("Amplitude\n(a. u.)")
        ax[0].tick_params("x", labelbottom=False)

        ax[1].plot(
            data.frequencies[frame_id].times(),
            np.array(data.frequencies[frame_id].values()) * 1e-9,
        )
        ax[1].set_ylabel("Frequency\n(GHz)")
        ax[1].tick_params("x", labelbottom=False)

        ax[2].plot(data.phases[frame_id].times(), data.phases[frame_id].values())
        ax[2].set_xlabel("Time (s)")
        ax[2].set_ylabel("Phase\n(rad)")


def draw_multiple_frames(pulse_sequence: PulseSequence):
    data = pulse_sequence.to_time_trace()
    for frame_id in data.amplitudes:
        f = plt.figure(figsize=(12, 4))
        plt.subplot(1, 3, 1)
        plt.plot(
            data.amplitudes[frame_id].times(),
            np.real(data.amplitudes[frame_id].values()),
            label="Real",
        )
        plt.plot(
            data.amplitudes[frame_id].times(),
            np.imag(data.amplitudes[frame_id].values()),
            label="Imag",
        )
        plt.xlabel("Time (s)")
        plt.ylabel("Amplitude (norm.)")
        plt.legend(loc="upper right")

        plt.subplot(1, 3, 2)
        plt.title(frame_id)
        plt.plot(
            data.frequencies[frame_id].times(), data.frequencies[frame_id].values()
        )
        plt.xlabel("Time (s)")
        plt.ylabel("Frequency (Hz)")

        plt.subplot(1, 3, 3)
        plt.plot(data.phases[frame_id].times(), data.phases[frame_id].values())
        plt.xlabel("Time (s)")
        plt.ylabel("Phase (rad)")
        f.tight_layout()

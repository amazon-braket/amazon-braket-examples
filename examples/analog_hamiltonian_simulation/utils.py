import numpy as np
import matplotlib.pyplot as plt
from braket.ahs.atom_arrangement import SiteType
from braket.ahs.time_series import TimeSeries
from braket.ahs.driving_field import DrivingField
from braket.ahs.shifting_field import ShiftingField
from braket.ahs.field import Field
from braket.ahs.pattern import Pattern

def show_register(register, blockade_radius=0.0):
    filled_sites = [site.coordinate for site in register if site.site_type == SiteType.FILLED]
    fig = plt.figure(figsize=(7, 7))
    plt.plot(np.array(filled_sites)[:, 0], np.array(filled_sites)[:, 1], 'r.', ms=15, label='filled')
    plt.legend(bbox_to_anchor=(1.1, 1.05))
    
    if blockade_radius > 0:
        for i in range(len(filled_sites)):
            for j in range(i+1, len(filled_sites)):            
                dist = np.linalg.norm(np.array(filled_sites[i]) - np.array(filled_sites[j]))
                if dist <= blockade_radius:
                    plt.plot([filled_sites[i][0], filled_sites[j][0]], [filled_sites[i][1], filled_sites[j][1]], 'b')


def get_drive(times, amplitude_values, detuning_values, phase_values):
    assert len(times) == len(amplitude_values)
    assert len(times) == len(detuning_values)
    assert len(times) == len(phase_values)
    
    amplitude = TimeSeries()
    detuning = TimeSeries()  
    phase = TimeSeries()    
    
    for t, amplitude_value, detuning_value, phase_value in zip(times, amplitude_values, detuning_values, phase_values):
        amplitude.put(t, amplitude_value)
        detuning.put(t, detuning_value)
        phase.put(t, phase_value) 

    drive = DrivingField(
        amplitude=amplitude, 
        detuning=detuning, 
        phase=phase
    )    
    
    return drive


def get_shift(times, values, pattern):
    assert len(times) == len(values)    
    
    magnitude = TimeSeries()
    for t, v in zip(times, values):
        magnitude.put(t, v)
    shift = ShiftingField(Field(magnitude, Pattern(pattern)))

    return shift
                    
def show_global_drive(drive):
    data = {
        'amplitude [rad/s]': drive.amplitude.time_series,
        'detuning [rad/s]': drive.detuning.time_series,
        'phase [rad]': drive.phase.time_series,
    }
    
    fig, axes = plt.subplots(3, 1, figsize=(7, 7), sharex=True)
    for ax, data_name in zip(axes, data.keys()):
        ax.plot(data[data_name].times(), data[data_name].values(), '.-')
        ax.set_ylabel(data_name)
        ax.grid(ls=':')
    axes[-1].set_xlabel('time [s]')
    plt.tight_layout()
    
def show_local_shift(shift):
    data = shift.magnitude.time_series
    pattern = shift.magnitude.pattern.series
    
    plt.plot(data.times(), data.values(), '.-', label="pattern: " + str(pattern))
    plt.xlabel('time [s]')
    plt.ylabel('shift [rad/s]')
    plt.legend()
    plt.tight_layout()
    
def show_drive_and_shift(drive, shift):
    drive_data = {
        'amplitude [rad/s]': drive.amplitude.time_series,
        'detuning [rad/s]': drive.detuning.time_series,
        'phase [rad]': drive.phase.time_series,
    }
    
    fig, axes = plt.subplots(4, 1, figsize=(7, 7), sharex=True)
    for ax, data_name in zip(axes, drive_data.keys()):
        ax.plot(drive_data[data_name].times(), drive_data[data_name].values(), '.-')
        ax.set_ylabel(data_name)
        ax.grid(ls=':')
        
    shift_data = shift.magnitude.time_series
    pattern = shift.magnitude.pattern.series   
    axes[-1].plot(shift_data.times(), shift_data.values(), '.-', label="pattern: " + str(pattern))
    axes[-1].set_ylabel('shift [rad/s]')
    axes[-1].set_xlabel('time [s]')
    axes[-1].legend()
    axes[-1].grid()
    plt.tight_layout()
    
def get_avg_density(result):
    measurements = result.measurements
    postSeqs = [measurement.shotResult.postSequence for measurement in measurements]
    postSeqs = 1 - np.array(postSeqs) # change the notation such 1 for rydberg state, and 0 for ground state
    
    avg_density = np.sum(postSeqs, axis=0)/len(postSeqs)
    
    return avg_density

def show_final_avg_density(result):
    avg_density = get_avg_density(result)
    
    plt.bar(range(len(avg_density)), avg_density)
    plt.xlabel("Indices of atoms")
    plt.ylabel("Average Rydberg density")
    
def concatenate_time_series(time_series_1, time_series_2):
    assert time_series_1.values()[-1] == time_series_2.values()[0]
    
    duration_1 = time_series_1.times()[-1] - time_series_1.times()[0]
    
    new_time_series = TimeSeries()
    new_times = time_series_1.times() + [t + duration_1 - time_series_2.times()[0] for t in time_series_2.times()[1:]]
    new_values = time_series_1.values() + time_series_2.values()[1:]
    for t, v in zip(new_times, new_values):
        new_time_series.put(t, v)
    
    return new_time_series
    
    
def concatenate_drives(drive_1, drive_2):
    return DrivingField(
        amplitude=concatenate_time_series(drive_1.amplitude.time_series, drive_2.amplitude.time_series),
        detuning=concatenate_time_series(drive_1.detuning.time_series, drive_2.detuning.time_series),
        phase=concatenate_time_series(drive_1.phase.time_series, drive_2.phase.time_series)
    )

    
def concatenate_shifts(shift_1, shift_2):
    assert shift_1.magnitude.pattern.series == shift_2.magnitude.pattern.series
    
    new_magnitude = concatenate_time_series(shift_1.magnitude.time_series, shift_2.magnitude.time_series)
    return ShiftingField(Field(new_magnitude, shift_1.magnitude.pattern))
    

def concatenate_drive_list(drive_list):
    drive = drive_list[0]
    for dr in drive_list[1:]:
        drive = concatenate_drives(drive, dr)
    return drive    


def concatenate_shift_list(shift_list):
    shift = shift_list[0]
    for sf in shift_list[1:]:
        shift = concatenate_shifts(shift, sf)
    return shift

def constant_time_series(other_time_series, constant=0.0):
    ts = TimeSeries()
    for t in other_time_series.times():
        ts.put(t, constant)
    return ts
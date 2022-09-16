import numpy as np
import matplotlib.pyplot as plt
from braket.ahs.atom_arrangement import SiteType

def show_register(register, blockade_radius=0.0):
    filled_sites = [site.coordinate for site in register._sites if site.site_type == SiteType.FILLED]
    fig = plt.figure(figsize=(7, 7))
    plt.plot(np.array(filled_sites)[:, 0], np.array(filled_sites)[:, 1], 'r.', ms=15, label='filled')
    plt.legend(bbox_to_anchor=(1.1, 1.05))
    
    if blockade_radius > 0:
        for i in range(len(filled_sites)):
            for j in range(i+1, len(filled_sites)):            
                dist = np.linalg.norm(np.array(filled_sites[i]) - np.array(filled_sites[j]))
                if dist <= blockade_radius:
                    plt.plot([filled_sites[i][0], filled_sites[j][0]], [filled_sites[i][1], filled_sites[j][1]], 'b')


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
    
    
def get_avg_density(result):
    measurements = result.measurements
    postSeqs = [measurement.shotResult.postSequence for measurement in measurements]
    
    avg_density = np.sum(np.array(postSeqs), axis=0)/len(postSeqs)
    
    return avg_density

def show_final_avg_density(result):
    avg_density = get_avg_density(result)
    
    plt.bar(range(len(avg_density)), get_avg_density(result))
    plt.xlabel("Indices of atoms")
    plt.ylabel("Average Rydberg density")
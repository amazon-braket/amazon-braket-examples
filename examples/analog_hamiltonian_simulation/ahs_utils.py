import numpy as np
import matplotlib.pyplot as plt
import networkx as nx
from braket.ahs.atom_arrangement import SiteType
from braket.timings.time_series import TimeSeries
from braket.ahs.driving_field import DrivingField
from braket.ahs.shifting_field import ShiftingField
from braket.ahs.field import Field
from braket.ahs.pattern import Pattern
from collections import Counter

from typing import Dict, List, Tuple
from braket.tasks.analog_hamiltonian_simulation_quantum_task_result import AnalogHamiltonianSimulationQuantumTaskResult
from braket.ahs.atom_arrangement import AtomArrangement


def show_register(
    register: AtomArrangement, 
    blockade_radius: float=0.0, 
    what_to_draw: str="bond", 
    show_atom_index:bool=True
):
    """Plot the given register 

        Args:
            register (AtomArrangement): A given register
            blockade_radius (float): The blockade radius for the register. Default is 0
            what_to_draw (str): Either "bond" or "circle" to indicate the blockade region. 
                Default is "bond"
            show_atom_index (bool): Whether showing the indices of the atoms. Default is True
        
    """
    filled_sites = [site.coordinate for site in register if site.site_type == SiteType.FILLED]
    empty_sites = [site.coordinate for site in register if site.site_type == SiteType.VACANT]
    
    fig = plt.figure(figsize=(7, 7))
    if filled_sites:
        plt.plot(np.array(filled_sites)[:, 0], np.array(filled_sites)[:, 1], 'r.', ms=15, label='filled')
    if empty_sites:
        plt.plot(np.array(empty_sites)[:, 0], np.array(empty_sites)[:, 1], 'k.', ms=5, label='empty')
    plt.legend(bbox_to_anchor=(1.1, 1.05))
    
    if show_atom_index:
        for idx, site in enumerate(register):
            plt.text(*site.coordinate, f"  {idx}", fontsize=12)
    
    if blockade_radius > 0 and what_to_draw=="bond":
        for i in range(len(filled_sites)):
            for j in range(i+1, len(filled_sites)):            
                dist = np.linalg.norm(np.array(filled_sites[i]) - np.array(filled_sites[j]))
                if dist <= blockade_radius:
                    plt.plot([filled_sites[i][0], filled_sites[j][0]], [filled_sites[i][1], filled_sites[j][1]], 'b')
                    
    if blockade_radius > 0 and what_to_draw=="circle":
        for site in filled_sites:
            plt.gca().add_patch( plt.Circle((site[0],site[1]), blockade_radius/2, color="b", alpha=0.3) )
        plt.gca().set_aspect(1)
    plt.show()


def rabi_pulse(
    rabi_pulse_area: float, 
    omega_max: float,
    omega_slew_rate_max: float
) -> Tuple[List[float], List[float]]:
    """Get a time series for Rabi frequency with specified Rabi phase, maximum amplitude
    and maximum slew rate

        Args:
            rabi_pulse_area (float): Total area under the Rabi frequency time series
            omega_max (float): The maximum amplitude 
            omega_slew_rate_max (float): The maximum slew rate

        Returns:
            Tuple[List[float], List[float]]: A tuple containing the time points and values
                of the time series for the time dependent Rabi frequency

        Notes: By Rabi phase, it means the integral of the amplitude of a time-dependent 
            Rabi frequency, \int_0^T\Omega(t)dt, where T is the duration.
    """

    phase_threshold = omega_max**2 / omega_slew_rate_max
    if rabi_pulse_area <= phase_threshold:
        t_ramp = np.sqrt(rabi_pulse_area / omega_slew_rate_max)
        t_plateau = 0
    else:
        t_ramp = omega_max / omega_slew_rate_max
        t_plateau = (rabi_pulse_area / omega_max) - t_ramp
    t_pules = 2 * t_ramp + t_plateau
    time_points = [0, t_ramp, t_ramp + t_plateau, t_pules]
    amplitude_values = [0, t_ramp * omega_slew_rate_max, t_ramp * omega_slew_rate_max, 0]
    
    return time_points, amplitude_values


def get_counts(result: AnalogHamiltonianSimulationQuantumTaskResult) -> Dict[str, int]:
    """Aggregate state counts from AHS shot results

        Args:
            result (AnalogHamiltonianSimulationQuantumTaskResult): The result 
                from which the aggregated state counts are obtained

        Returns:
            Dict[str, int]: number of times each state configuration is measured

        Notes: We use the following convention to denote the state of an atom (site):
            e: empty site
            r: Rydberg state atom
            g: ground state atom
    """

    state_counts = Counter()
    states = ['e', 'r', 'g']
    for shot in result.measurements:
        pre = shot.pre_sequence
        post = shot.post_sequence
        state_idx = np.array(pre) * (1 + np.array(post))
        state = "".join(map(lambda s_idx: states[s_idx], state_idx))
        state_counts.update((state,))

    return dict(state_counts)


def get_drive(
    times: List[float], 
    amplitude_values: List[float], 
    detuning_values: List[float], 
    phase_values: List[float]
) -> DrivingField:
    """Get the driving field from a set of time points and values of the fields

        Args:
            times (List[float]): The time points of the driving field
            amplitude_values (List[float]): The values of the amplitude
            detuning_values (List[float]): The values of the detuning
            phase_values (List[float]): The values of the phase

        Returns:
            DrivingField: The driving field obtained
    """

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


def get_shift(times: List[float], values: List[float], pattern: List[float]) -> ShiftingField:
    """Get the shifting field from a set of time points, values and pattern

        Args:
            times (List[float]): The time points of the shifting field
            values (List[float]): The values of the shifting field
            pattern (List[float]): The pattern of the shifting field

        Returns:
            ShiftingField: The shifting field obtained
    """    
    assert len(times) == len(values)    
    
    magnitude = TimeSeries()
    for t, v in zip(times, values):
        magnitude.put(t, v)
    shift = ShiftingField(Field(magnitude, Pattern(pattern)))

    return shift


def show_global_drive(drive, axes=None, **plot_ops):
    """Plot the driving field
        Args:
            drive (DrivingField): The driving field to be plot
            axes: matplotlib axis to draw on
            **plot_ops: options passed to matplitlib.pyplot.plot
    """   

    data = {
        'amplitude [rad/s]': drive.amplitude.time_series,
        'detuning [rad/s]': drive.detuning.time_series,
        'phase [rad]': drive.phase.time_series,
    }


    if axes is None:
        fig, axes = plt.subplots(3, 1, figsize=(7, 7), sharex=True)

    for ax, data_name in zip(axes, data.keys()):
        if data_name == 'phase [rad]':
            ax.step(data[data_name].times(), data[data_name].values(), '.-', where='post',**plot_ops)
        else:
            ax.plot(data[data_name].times(), data[data_name].values(), '.-',**plot_ops)
        ax.set_ylabel(data_name)
        ax.grid(ls=':')
    axes[-1].set_xlabel('time [s]')
    plt.tight_layout()
    plt.show()


def show_local_shift(shift:ShiftingField):
    """Plot the shifting field
        Args:
            shift (ShiftingField): The shifting field to be plot
    """       
    data = shift.magnitude.time_series
    pattern = shift.magnitude.pattern.series
    
    plt.plot(data.times(), data.values(), '.-', label="pattern: " + str(pattern))
    plt.xlabel('time [s]')
    plt.ylabel('shift [rad/s]')
    plt.legend()
    plt.tight_layout()
    plt.show()

    
def show_drive_and_shift(drive: DrivingField, shift: ShiftingField):
    """Plot the driving and shifting fields
    
        Args:
            drive (DrivingField): The driving field to be plot
            shift (ShiftingField): The shifting field to be plot
    """        
    drive_data = {
        'amplitude [rad/s]': drive.amplitude.time_series,
        'detuning [rad/s]': drive.detuning.time_series,
        'phase [rad]': drive.phase.time_series,
    }
    
    fig, axes = plt.subplots(4, 1, figsize=(7, 7), sharex=True)
    for ax, data_name in zip(axes, drive_data.keys()):
        if data_name == 'phase [rad]':
            ax.step(drive_data[data_name].times(), drive_data[data_name].values(), '.-', where='post')
        else:
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
    plt.show()


def get_avg_density(result: AnalogHamiltonianSimulationQuantumTaskResult) -> np.ndarray:
    """Get the average Rydberg densities from the result

        Args:
            result (AnalogHamiltonianSimulationQuantumTaskResult): The result 
                from which the aggregated state counts are obtained

        Returns: 
            ndarray: The average densities from the result
    """    

    measurements = result.measurements
    postSeqs = [measurement.post_sequence for measurement in measurements]
    postSeqs = 1 - np.array(postSeqs) # change the notation such 1 for rydberg state, and 0 for ground state
    
    avg_density = np.sum(postSeqs, axis=0)/len(postSeqs)
    
    return avg_density


def show_final_avg_density(result: AnalogHamiltonianSimulationQuantumTaskResult):
    """Showing a bar plot for the average Rydberg densities from the result

        Args:
            result (AnalogHamiltonianSimulationQuantumTaskResult): The result 
                from which the aggregated state counts are obtained
    """    
    avg_density = get_avg_density(result)
    
    plt.bar(range(len(avg_density)), avg_density)
    plt.xlabel("Indices of atoms")
    plt.ylabel("Average Rydberg density")
    plt.show()


def constant_time_series(other_time_series: TimeSeries, constant: float=0.0) -> TimeSeries:
    """Obtain a constant time series with the same time points as the given time series

        Args:
            other_time_series (TimeSeries): The given time series

        Returns:
            TimeSeries: A constant time series with the same time points as the given time series
    """
    ts = TimeSeries()
    for t in other_time_series.times():
        ts.put(t, constant)
    return ts


def concatenate_time_series(time_series_1: TimeSeries, time_series_2: TimeSeries) -> TimeSeries:
    """Concatenate two time series to a single time series

        Args:
            time_series_1 (TimeSeries): The first time series to be concatenated
            time_series_2 (TimeSeries): The second time series to be concatenated

        Returns:
            TimeSeries: The concatenated time series

    """
    assert time_series_1.values()[-1] == time_series_2.values()[0]
    
    duration_1 = time_series_1.times()[-1] - time_series_1.times()[0]
    
    new_time_series = TimeSeries()
    new_times = time_series_1.times() + [t + duration_1 - time_series_2.times()[0] for t in time_series_2.times()[1:]]
    new_values = time_series_1.values() + time_series_2.values()[1:]
    for t, v in zip(new_times, new_values):
        new_time_series.put(t, v)
    
    return new_time_series


def concatenate_drives(drive_1: DrivingField, drive_2: DrivingField) -> DrivingField:
    """Concatenate two driving fields to a single driving field

        Args:
            drive_1 (DrivingField): The first driving field to be concatenated
            drive_2 (DrivingField): The second driving field to be concatenated

        Returns:
            DrivingField: The concatenated driving field
    """    
    return DrivingField(
        amplitude=concatenate_time_series(drive_1.amplitude.time_series, drive_2.amplitude.time_series),
        detuning=concatenate_time_series(drive_1.detuning.time_series, drive_2.detuning.time_series),
        phase=concatenate_time_series(drive_1.phase.time_series, drive_2.phase.time_series)
    )


def concatenate_shifts(shift_1: ShiftingField, shift_2: ShiftingField) -> ShiftingField:
    """Concatenate two driving fields to a single driving field

        Args:
            shift_1 (ShiftingField): The first shifting field to be concatenated
            shift_2 (ShiftingField): The second shifting field to be concatenated

        Returns:
            ShiftingField: The concatenated shifting field
    """        
    assert shift_1.magnitude.pattern.series == shift_2.magnitude.pattern.series
    
    new_magnitude = concatenate_time_series(shift_1.magnitude.time_series, shift_2.magnitude.time_series)
    return ShiftingField(Field(new_magnitude, shift_1.magnitude.pattern))


def concatenate_drive_list(drive_list: List[DrivingField]) -> DrivingField:
    """Concatenate a list of driving fields to a single driving field

        Args:
            drive_list (List[DrivingField]): The list of driving fields to be concatenated

        Returns:
            DrivingField: The concatenated driving field
    """        
    drive = drive_list[0]
    for dr in drive_list[1:]:
        drive = concatenate_drives(drive, dr)
    return drive    


def concatenate_shift_list(shift_list: List[ShiftingField]) -> ShiftingField:
    """Concatenate a list of shifting fields to a single driving field

        Args:
            shift_list (List[ShiftingField]): The list of shifting fields to be concatenated

        Returns:
            ShiftingField: The concatenated shifting field
    """            
    shift = shift_list[0]
    for sf in shift_list[1:]:
        shift = concatenate_shifts(shift, sf)
    return shift


def plot_avg_density_2D(densities, register, with_labels = True, batch_index = None, batch_mapping = None, custom_axes = None):
    
    # get atom coordinates
    atom_coords = list(zip(register.coordinate_list(0), register.coordinate_list(1)))
    # convert all to micrometers
    atom_coords = [(atom_coord[0] * 10**6, atom_coord[1] * 10**6) for atom_coord in atom_coords]
    
    plot_avg_of_avgs = False
    plot_single_batch = False
        
    if batch_index is not None:
        if batch_mapping is not None:
                plot_single_batch = True
                # provided both batch and batch_mapping, show averages of single batch
                batch_subindices = batch_mapping[batch_index]
                batch_labels = {i:label for i,label in enumerate(batch_subindices)}
                # get proper positions
                pos = {i:tuple(coord) for i,coord in enumerate(list(np.array(atom_coords)[batch_subindices]))}
                # narrow down densities
                densities = np.array(densities)[batch_subindices]
                
        else:
            raise Exception("batch_mapping required to index into")
    else:
        if batch_mapping is not None:
            plot_avg_of_avgs = True
            # just need the coordinates for first batch_mapping
            subcoordinates = np.array(atom_coords)[batch_mapping[(0,0)]]
            pos = {i:coord for i,coord in enumerate(subcoordinates)}                                     
        else:
            # If both not provided do standard FOV
            # handle 1D case
            pos = {i:coord for i,coord in enumerate(atom_coords)}
           
    # get colors
    vmin = 0
    vmax = 1
    cmap = plt.cm.Blues
    
    # construct graph
    g = nx.Graph()
    g.add_nodes_from(list(range(len(densities))))
    
    # construct plot
    if custom_axes is None:
        fig, ax = plt.subplots()
    else:
        ax = custom_axes
    
    nx.draw(g, 
            pos,
            node_color=densities,
            cmap=cmap,
            node_shape="o",
            vmin=vmin,
            vmax=vmax,
            font_size=9,
            with_labels=with_labels,
            labels= batch_labels if plot_single_batch else None,
            ax = custom_axes if custom_axes is not None else ax)
        
    ## Set axes
    ax.set_axis_on()
    ax.tick_params(left=True, 
                   bottom=True, 
                   top=True,
                   right=True,
                   labelleft=True, 
                   labelbottom=True, 
                   # labeltop=True,
                   # labelright=True,
                   direction="in")
    ## Set colorbar
    sm = plt.cm.ScalarMappable(cmap=cmap, norm=plt.Normalize(vmin=vmin, vmax=vmax))
    sm.set_array([])

    
    ax.ticklabel_format(style="sci", useOffset=False)
    
    # set titles on x and y axes
    plt.xlabel("x [μm]")
    plt.ylabel("y [μm]")
    
    
    if plot_avg_of_avgs:
        cbar_label = "Averaged Rydberg Density"
    else:
        cbar_label = "Rydberg Density"
        
    plt.colorbar(sm, ax=ax, label=cbar_label)

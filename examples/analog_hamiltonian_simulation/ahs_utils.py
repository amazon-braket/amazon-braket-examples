import matplotlib.pyplot as plt
import networkx as nx
import numpy as np

from braket.ahs.atom_arrangement import AtomArrangement, SiteType
from braket.ahs.driving_field import DrivingField
from braket.ahs.local_detuning import LocalDetuning
from braket.tasks.analog_hamiltonian_simulation_quantum_task_result import (
    AnalogHamiltonianSimulationQuantumTaskResult,
)


def show_register(
    register: AtomArrangement,
    blockade_radius: float = 0.0,
    what_to_draw: str = "bond",
    show_atom_index: bool = True,
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

    plt.figure(figsize=(7, 7))
    if filled_sites:
        plt.plot(
            np.array(filled_sites)[:, 0], np.array(filled_sites)[:, 1], "r.", ms=15, label="filled"
        )
    if empty_sites:
        plt.plot(
            np.array(empty_sites)[:, 0], np.array(empty_sites)[:, 1], "k.", ms=5, label="empty"
        )
    plt.legend(bbox_to_anchor=(1.1, 1.05))

    if show_atom_index:
        for idx, site in enumerate(register):
            plt.text(*site.coordinate, f"  {idx}", fontsize=12)

    if blockade_radius > 0 and what_to_draw == "bond":
        for i in range(len(filled_sites)):
            for j in range(i + 1, len(filled_sites)):
                dist = np.linalg.norm(np.array(filled_sites[i]) - np.array(filled_sites[j]))
                if dist <= blockade_radius:
                    plt.plot(
                        [filled_sites[i][0], filled_sites[j][0]],
                        [filled_sites[i][1], filled_sites[j][1]],
                        "b",
                    )

    if blockade_radius > 0 and what_to_draw == "circle":
        for site in filled_sites:
            plt.gca().add_patch(
                plt.Circle((site[0], site[1]), blockade_radius / 2, color="b", alpha=0.3)
            )
        plt.gca().set_aspect(1)
    plt.show()


def show_global_drive(drive, axes=None, **plot_ops):
    """Plot the driving field
    Args:
        drive (DrivingField): The driving field to be plot
        axes: matplotlib axis to draw on
        **plot_ops: options passed to matplitlib.pyplot.plot
    """

    data = {
        "amplitude [rad/s]": drive.amplitude.time_series,
        "detuning [rad/s]": drive.detuning.time_series,
        "phase [rad]": drive.phase.time_series,
    }

    if axes is None:
        _fig, axes = plt.subplots(3, 1, figsize=(7, 7), sharex=True)

    for ax, data_name in zip(axes, data.keys()):
        if data_name == "phase [rad]":
            ax.step(
                data[data_name].times(), data[data_name].values(), ".-", where="post", **plot_ops
            )
        else:
            ax.plot(data[data_name].times(), data[data_name].values(), ".-", **plot_ops)
        ax.set_ylabel(data_name)
        ax.grid(ls=":")
    axes[-1].set_xlabel("time [s]")
    plt.tight_layout()
    plt.show()


def show_local_detuning(local_detuning: LocalDetuning):
    """Plot local_detuning
    Args:
        local_detuning (LocalDetuning): The local detuning to be plotted
    """
    data = local_detuning.magnitude.time_series
    pattern = local_detuning.magnitude.pattern.series

    plt.plot(data.times(), data.values(), ".-", label="pattern: " + str(pattern))
    plt.xlabel("time [s]")
    plt.ylabel("detuning [rad/s]")
    plt.legend()
    plt.tight_layout()
    plt.show()


def show_drive_and_local_detuning(drive: DrivingField, local_detuning: LocalDetuning):
    """Plot the driving field and local detuning

    Args:
        drive (DrivingField): The driving field to be plot
        local_detuning (LocalDetuning): The local detuning to be plotted
    """
    drive_data = {
        "amplitude [rad/s]": drive.amplitude.time_series,
        "detuning [rad/s]": drive.detuning.time_series,
        "phase [rad]": drive.phase.time_series,
    }

    _fig, axes = plt.subplots(4, 1, figsize=(7, 7), sharex=True)
    for ax, data_name in zip(axes, drive_data.keys()):
        if data_name == "phase [rad]":
            ax.step(
                drive_data[data_name].times(), drive_data[data_name].values(), ".-", where="post"
            )
        else:
            ax.plot(drive_data[data_name].times(), drive_data[data_name].values(), ".-")
        ax.set_ylabel(data_name)
        ax.grid(ls=":")

    local_detuning_data = local_detuning.magnitude.time_series
    pattern = local_detuning.magnitude.pattern.series
    axes[-1].plot(
        local_detuning_data.times(),
        local_detuning_data.values(),
        ".-",
        label="pattern: " + str(pattern),
    )
    axes[-1].set_ylabel("detuning [rad/s]")
    axes[-1].set_xlabel("time [s]")
    axes[-1].legend()
    axes[-1].grid()
    plt.tight_layout()
    plt.show()


def show_final_avg_density(result: AnalogHamiltonianSimulationQuantumTaskResult):
    """Showing a bar plot for the average Rydberg densities from the result

    Args:
        result (AnalogHamiltonianSimulationQuantumTaskResult): The result
            from which the aggregated state counts are obtained
    """
    avg_density = result.get_avg_density()

    plt.bar(range(len(avg_density)), avg_density)
    plt.xlabel("Indices of atoms")
    plt.ylabel("Average Rydberg density")
    plt.show()


def plot_avg_density_2D(
    densities, register, with_labels=True, batch_index=None, batch_mapping=None, custom_axes=None
):
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
            batch_labels = {i: label for i, label in enumerate(batch_subindices)}
            # get proper positions
            pos = {
                i: tuple(coord)
                for i, coord in enumerate(list(np.array(atom_coords)[batch_subindices]))
            }
            # narrow down densities
            densities = np.array(densities)[batch_subindices]

        else:
            raise Exception("batch_mapping required to index into")
    else:
        if batch_mapping is not None:
            plot_avg_of_avgs = True
            # just need the coordinates for first batch_mapping
            subcoordinates = np.array(atom_coords)[batch_mapping[(0, 0)]]
            pos = {i: coord for i, coord in enumerate(subcoordinates)}
        else:
            # If both not provided do standard FOV
            # handle 1D case
            pos = {i: coord for i, coord in enumerate(atom_coords)}

    # get colors
    vmin = 0
    vmax = 1
    cmap = plt.cm.Blues

    # construct graph
    g = nx.Graph()
    g.add_nodes_from(list(range(len(densities))))

    # construct plot
    if custom_axes is None:
        _fig, ax = plt.subplots()
    else:
        ax = custom_axes

    nx.draw(
        g,
        pos,
        node_color=densities,
        cmap=cmap,
        node_shape="o",
        vmin=vmin,
        vmax=vmax,
        font_size=9,
        with_labels=with_labels,
        labels=batch_labels if plot_single_batch else None,
        ax=custom_axes if custom_axes is not None else ax,
    )

    ## Set axes
    ax.set_axis_on()
    ax.tick_params(
        left=True,
        bottom=True,
        top=True,
        right=True,
        labelleft=True,
        labelbottom=True,
        # labeltop=True,
        # labelright=True,
        direction="in",
    )
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

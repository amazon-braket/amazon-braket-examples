# IMPORTS
import warnings

import matplotlib.cbook
import matplotlib.pyplot as plt
import networkx as nx
from pyqubo import Spin, solve_ising

warnings.filterwarnings("ignore", category=matplotlib.cbook.mplDeprecation)


def build_classical_ising(J, N):
    """
    function to build classical Ising Hamiltonian
    """

    # define classical spin (Ising) variables
    spins = []
    for ii in range(N):
        spin_name = "s" + str(ii)
        spin = Spin(spin_name)
        spins.append(spin)

    # build Ising Hamiltonian
    ham = 0
    for ii in range(N):
        for jj in range(ii + 1, N):
            ham += J[ii][jj] * spins[ii] * spins[jj]

    # create Ising model
    model = ham.compile()
    linear, quad, offset = model.to_ising()

    return model, linear, quad, offset


def get_classical_energy_min(J, solution):
    """
    function to return min energy for given classical solution of
    Ising Hamiltonian with two-body terms for weighted graph
    NO SINGLE BIT TERMS, NO CONSTANT OFFSET
    """

    N = J.shape[0]
    # calculate energy and maxcut (UNWEIGHTED graph)
    energy_min = 0
    for ii in range(N):
        for jj in range(ii + 1, N):
            energy_min += J[ii][jj] * solution["s" + str(ii)] * solution["s" + str(jj)]

    print("Minimal energy found classically:", energy_min)

    return energy_min


# helper function to plot graph
def plot_colored_graph_simple(graph, colors, pos):
    """
    plot colored graph for given colored solution
    """

    # define color scheme
    colorlist = [
        "#e41a1c",
        "#377eb8",
        "#4daf4a",
        "#984ea3",
        "#ff7f00",
        "#ffff33",
        "#a65628",
        "#f781bf",
    ]

    # draw network
    nx.draw_networkx(
        graph,
        pos,
        node_color=[colorlist[colors[int(node)]] for node in graph.nodes],
        node_size=400,
        font_weight="bold",
        font_color="w",
    )

    # plot the graph
    plt.axis("off")
    # plt.savefig("./figures/weighted_graph.png") # save as png
    # plt.show();


# helper function to plot graph
def plot_colored_graph(J, N, colors, pos):
    """
    plot colored graph for given colored solution
    """
    # define graph
    graph = nx.Graph()
    all_weights = []

    for ii in range(0, N):
        for jj in range(ii + 1, N):
            if J[ii][jj] != 0:
                graph.add_edge(str(ii), str(jj), weight=J[ii][jj])
                all_weights.append(J[ii][jj])

    # positions for all nodes
    # pos = nx.spring_layout(graph)

    # get unique weights
    unique_weights = list(set(all_weights))

    # plot the edges - one by one
    for weight in unique_weights:
        # form a filtered list with just the weight you want to draw
        weighted_edges = [
            (node1, node2)
            for (node1, node2, edge_attr) in graph.edges(data=True)
            if edge_attr["weight"] == weight
        ]
        # multiplying by [num_nodes/sum(all_weights)] makes the graphs edges look cleaner
        # width = weight
        width = weight * N * 5.0 / sum(all_weights)
        nx.draw_networkx_edges(graph, pos, edgelist=weighted_edges, width=width)

    colorlist = [
        "#e41a1c",
        "#377eb8",
        "#4daf4a",
        "#984ea3",
        "#ff7f00",
        "#ffff33",
        "#a65628",
        "#f781bf",
    ]
    nx.draw_networkx(
        graph,
        pos,
        node_color=[colorlist[colors[int(node)]] for node in graph.nodes],
        node_size=400,
        font_weight="bold",
        font_color="w",
    )

    # plot the graph
    plt.axis("off")
    # plt.savefig("./figures/weighted_graph.png") # save as png
    # plt.show();


def solve_classical_ising(J, N, pos):
    """
    function to solve classical optimization problem defined by graph
    """

    # define and build classical Ising
    model, linear, quad, offset = build_classical_ising(J, N)

    # Solve classical Ising model
    solution = solve_ising(linear, quad)

    # print calssical solution
    print("Classical solution:", solution)

    # get corresponding energy
    energy_min = get_classical_energy_min(J, solution)

    # Obtain colors of each vertex
    colors = [0 for _ in range(N)]
    for ii in range(N):
        if solution["s" + str(ii)] == 1:
            colors[ii] = 1

    # Plot graph after coloring
    # plot_colored_graph(J, N, colors, pos)

    return solution, energy_min, colors

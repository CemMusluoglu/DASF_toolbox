import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np

# Choose plot backend.
mpl.use("macosx")
# mpl.use('Qt5Agg')
# mpl.use('TkAgg')
# mpl.use("Agg")
from dasftoolbox import (
    DASF,
    ConvergenceParameters,
    DynamicPlotParameters,
    NetworkGraph,
    get_stationary_setting,
)
from dasftoolbox.data_retrievers.ica_data_retriever import ICADataRetriever
from dasftoolbox.optimization_problems.ica_problem import ICAProblem

random_seed = 2025
rng = np.random.default_rng(random_seed)

# Number of nodes
nb_nodes = 5
# Number of channels per node
nb_sensors_per_node = (5 * np.ones(nb_nodes)).astype(int)
# Create adjacency matrix (hollow matrix) of a random graph
adjacency_matrix = rng.integers(0, 1, size=(nb_nodes, nb_nodes), endpoint=True)
adjacency_matrix = np.triu(adjacency_matrix, 1) + np.tril(adjacency_matrix.T, -1)
network_graph = NetworkGraph(
    nb_nodes=nb_nodes,
    nb_sensors_per_node=nb_sensors_per_node,
    adjacency_matrix=adjacency_matrix,
)

# Number of samples per window of the signals
nb_samples_per_window = 10000

# Number of windows in total
nb_windows = 1

# Number of filters of X
nb_filters = 2

# DASF solver convergence parameters
dasf_iterations = 300
dasf_convergence_parameters = ConvergenceParameters(max_iterations=dasf_iterations)

data_window_params = get_stationary_setting(
    window_length=nb_samples_per_window, iterations=dasf_iterations
)

ica_data_retriever = ICADataRetriever(
    data_window_params=data_window_params,
    nb_sensors=network_graph.nb_sensors_total,
    nb_windows=nb_windows,
    rng=rng,
)

# Since the ICA problem is solved in an iterative way, we provide convergence parameters for its solver
ica_iterations = 200
ica_convergence_parameters = ConvergenceParameters(max_iterations=ica_iterations)
ica_problem = ICAProblem(
    nb_filters=nb_filters,
    convergence_parameters=ica_convergence_parameters,
)

update_path = rng.permutation(range(nb_nodes))

# Dynamic plotting parameters
dynamic_plot_params = DynamicPlotParameters(
    tau=50, show_x=True, show_xTY=True, X_col=1, XTY_col=1, Y_id=0
)


dasf_solver = DASF(
    problem=ica_problem,
    data_retriever=ica_data_retriever,
    network_graph=network_graph,
    dasf_convergence_params=dasf_convergence_parameters,
    updating_path=update_path,
    rng=rng,
    dynamic_plot=True,
    dynamic_plot_params=dynamic_plot_params,
)
dasf_solver.run()

fig = dasf_solver.plot_error()

plt.show()

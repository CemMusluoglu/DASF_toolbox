import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt

# Choose plot backend.
mpl.use("macosx")
# mpl.use('Qt5Agg')
# mpl.use('TkAgg')
# mpl.use("Agg")
from dasf_tbx.problem_settings import (
    NetworkGraph,
    ConvergenceParameters,
)
from dasf_tbx.optimization_problems import RTLSProblem
from dasf_tbx.data_retriever import (
    RTLSDataRetriever,
    DataWindowParameters,
)
from dasf_tbx.dasf import DASF, DynamicPlotParameters

random_seed = 2025
rng = np.random.default_rng(random_seed)

# Number of nodes
nb_nodes = 10
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
nb_windows = 200

# Number of filters of X
nb_filters = 1

nb_window_reuse = 1

data_window_params = data_window_params = DataWindowParameters(
    window_length=nb_samples_per_window,
    nb_window_reuse=nb_window_reuse,
)

rtls_data_retriever = RTLSDataRetriever(
    data_window_params=data_window_params,
    nb_sensors=network_graph.nb_sensors_total,
    nb_sources=nb_filters,
    nb_windows=nb_windows,
    rng=rng,
)

# Since the RTLS problem is solved in an iterative way, we provide convergence parameters for its solver
rtls_iterations = 200
rtls_convergence_parameters = ConvergenceParameters(max_iterations=rtls_iterations)
rtls_problem = RTLSProblem(
    nb_filters=nb_filters, convergence_parameters=rtls_convergence_parameters
)

# DASF solver convergence parameters
dasf_iterations = nb_windows
dasf_convergence_parameters = ConvergenceParameters(max_iterations=dasf_iterations)
update_path = rng.permutation(range(nb_nodes))

# Dynamic plotting parameters
dynamic_plot_params = DynamicPlotParameters(
    tau=50, show_x=True, show_xTY=True, X_col=0, XTY_col=0, Y_id=0
)

# We can additionally provide another class of convergence parameters for the internal solver used in DASF, for example to save in computational costs
internal_iterations = 10
solver_convergence_parameters = ConvergenceParameters(
    max_iterations=internal_iterations
)
dasf_solver = DASF(
    problem=rtls_problem,
    data_retriever=rtls_data_retriever,
    network_graph=network_graph,
    dasf_convergence_params=dasf_convergence_parameters,
    updating_path=update_path,
    solver_convergence_parameters=solver_convergence_parameters,
    rng=rng,
    dynamic_plot=True,
    dynamic_plot_params=dynamic_plot_params,
)
dasf_solver.run()

fig = dasf_solver.plot_error()

plt.show()

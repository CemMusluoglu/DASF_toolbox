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
    DataWindowParameters,
    DynamicPlotParameters,
    NetworkGraph,
)
from dasftoolbox.data_retrievers.qcqp_data_retriever import QCQPDataRetriever
from dasftoolbox.optimization_problems.qcqp_problem import QCQPProblem

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
nb_filters = 3

nb_window_reuse = 1

data_window_params = data_window_params = DataWindowParameters(
    window_length=nb_samples_per_window,
    nb_window_reuse=nb_window_reuse,
)

qcqp_data_retriever = QCQPDataRetriever(
    data_window_params=data_window_params,
    nb_filters=nb_filters,
    nb_sensors=network_graph.nb_sensors_total,
    nb_windows=nb_windows,
    rng=rng,
)

qcqp_problem = QCQPProblem(
    nb_filters=nb_filters,
)

# DASF solver convergence parameters
dasf_iterations = nb_windows
dasf_convergence_parameters = ConvergenceParameters(max_iterations=dasf_iterations)
update_path = rng.permutation(range(nb_nodes))

# Dynamic plotting parameters
dynamic_plot_params = DynamicPlotParameters(
    tau=50, show_x=True, show_xTY=True, X_col=0, XTY_col=0, Y_id=0
)

dasf_solver = DASF(
    problem=qcqp_problem,
    data_retriever=qcqp_data_retriever,
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

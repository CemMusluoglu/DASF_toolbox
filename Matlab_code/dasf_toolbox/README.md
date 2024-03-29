# The DASF framework

Folder with the DASF implementation and utility functions (more details inside the code).

`dasf.m:` Function implementing the DASF framework taking as arguments:

        - prob_params: Structure containing the problem parameters such as the number of nodes, the size of the filter, etc.
        
        - data: Structure containing the data of the problem.

        - prob_solver: Function handle to the solver of the problem.

        - conv: (Optional) Structure related the stopping criterion.

        - prob_select_sol: (Optional) Function handle to the method for resolving uniqueness ambiguities.

        - prob_eval: (Optional) Function handle to the objective function evaluation. 

`find_path.m:` Function finding the neighbors of node q and the shortest path to other every other node in the network.

`shortest_path.m:` Function computing the shortest path distance between a source node and all nodes in the network using Dijkstra's method. Note: This implementation is only for graphs for which the weight at each edge is equal to 1.

`make_sym.m:` Function to force symmetry.

`find_clusters.m:` Function to obtain clusters of nodes for each neighbor.

`build_Cq.m:` Function to build the transition matrix between the local data and variables and the global ones.

`compress.m:` Function to compress the data.

`block_q.m:` Function to extract the block of X corresponding to node q.

`dasf_multivar.m:` Same function as `dasf` but for problems with multiple variables (e.g. Canonical Correlation Analysis). The output `X` is a cell containing multiple variables.

`dasf_block.m:` Same function as `dasf` but the optimization variable is divided into cells *within the function* to explicitly emphasize and separate the block structure of the global variable `X=[X1;...;Xk;...XK]`. At the expense of a slightly less straightforward implementation than `dasf`, it better represents how each node updates their local variable.

`update_X_block.m:` Only called from `dasf_block`. Explicitly updating the `Xk` of each node `k` separately, where the global variable `X` is equal to `[X1;...;Xk;...XK]`, it allows to adapt the updating scheme depending on the user's application in an easier way than the implementation used in `dasf`, resulting in more flexibility. 

**Dependencies:**



                                dasf
                                  |
                                  |
           ----------------------------------------------------------------
           |    |           |           |            |     |    |    |    |
           |    |           |           |            |     |    |    |    |
           |    v           v           v            v     |    v    |    v
           |find_path  find_clusters   build_Cq   compress | block_q |  plot_dynamic
           |    |                                    |     |         |
           |    |                                    |     |         |
           |    v                                    v     |         |
           | shortest_path                         make_sym|         |
           |                                               |         |
           |                                               |         |
           |                                               |         |
           |                                               |         |
           v                                               v         v
        prob_eval                                 prob_solver   prob_select_sol





                              dasf_block
                                  |
                                  |
           ------------------------------------------------------------------------------
           |    |        |          |          |     |    |    |         |    |         |
           |    |        |          |          |     |    |    |         |    |         |
           |    v        v          v          v     |    |    v         |    v         v
           |find_path find_clusters build_Cq compress|    |update_X_block| block_q plot_dynamic
           |    |                                    |    |          |   |         
           |    |                                    |    |          |   |         
           |    v                                    v    |          |   |         
           | shortest_path                        make_sym|          |   |
           |                                              |          |   |
           |                                              |          |   |
           |                                              |          |   |
           |                                              |          |   |
           v                                              v          v   v
        prob_eval                                    prob_solver   prob_select_sol

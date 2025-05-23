import numpy as np

from dasftoolbox.optimization_problems.optimization_problem import (
    ConstraintType,
    OptimizationProblem,
)
from dasftoolbox.problem_settings import ConvergenceParameters, ProblemInputs
from dasftoolbox.utils import autocorrelation_matrix


class LCMVProblem(OptimizationProblem):
    """
    LCMV problem class.

    :math:`\min_X\; \mathbb{E}[\| X^T \mathbf{y}(t)\|^2]` subject to :math:`X^TB=H.`

    Attributes
    ----------
    nb_filters : int
        Number of filters.
    """

    def __init__(self, nb_filters: int, **kwargs) -> None:
        super().__init__(nb_filters=nb_filters, **kwargs)

    def solve(
        self,
        problem_inputs: ProblemInputs,
        save_solution: bool = False,
        convergence_parameters: ConvergenceParameters | None = None,
        initial_estimate: np.ndarray | None = None,
    ) -> np.ndarray:
        """
        Solve the LCMV problem.

        The solver implements the closed-form solution: :math:`X^*=R_{\mathbf{yy}}^{-1}B(B^TR_{\mathbf{yy}}^{-1}B)^{-1}H^T)`, where :math:`R_{\mathbf{yy}}` corresponds to the autocorrelation matrix of the observed signal :math:`\mathbf{y}`.


        Parameters
        ----------
        problem_inputs : ProblemInputs
            The problem inputs containing the observed signal :math:`\mathbf{y}` and the matrices :math:`B` and  :math:`H`.
        save_solution : bool, optional
            Whether to save the solution or not, by default False
        convergence_parameters : ConvergenceParameters | None, optional
            Convergence parameters, by default None
        initial_estimate : np.ndarray | None, optional
            Initial estimate, by default None

        Returns
        -------
        np.ndarray
            The solution to the LCMV problem.
        """
        Y = problem_inputs.fused_signals[0]
        B = problem_inputs.fused_constants[0]
        H = problem_inputs.global_parameters[0]

        Ryy = autocorrelation_matrix(Y)

        X_star = (
            np.linalg.inv(Ryy) @ B @ np.linalg.inv(B.T @ np.linalg.inv(Ryy) @ B) @ H.T
        )

        if save_solution:
            self._X_star = X_star

        return X_star

    def evaluate_objective(self, X: np.ndarray, problem_inputs: ProblemInputs) -> float:
        """
        Evaluate the LCMV objective :math:`\mathbb{E}[\|X^T \mathbf{y}(t)\|^2]`.

        Parameters
        ----------
        X : np.ndarray
            The point to evaluate.
        problem_inputs : ProblemInputs
            The problem inputs containing the observed signal :math:`\mathbf{y}` and the matrices :math:`B` and  :math:`H`.

        Returns
        -------
        float
            The value of the objective function at point `X`.
        """
        Y = problem_inputs.fused_signals[0]

        Ryy = autocorrelation_matrix(Y)

        f = np.trace(X.T @ Ryy @ X)

        return f

    def get_problem_constraints(self, problem_inputs: ProblemInputs) -> ConstraintType:
        B = problem_inputs.fused_constants[0]
        H = problem_inputs.global_parameters[0]

        def equality_constraint(X: np.ndarray) -> np.ndarray:
            return X.T @ B - H

        return equality_constraint, None

    get_problem_constraints.__doc__ = (
        OptimizationProblem.get_problem_constraints.__doc__
    )

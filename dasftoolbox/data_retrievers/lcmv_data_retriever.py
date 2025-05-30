import numpy as np

from dasftoolbox.data_retrievers.data_retriever import (
    DataRetriever,
    DataWindowParameters,
)
from dasftoolbox.problem_settings import ProblemInputs
from dasftoolbox.utils import normalize


class LCMVDataRetriever(DataRetriever):
    """
    LCMV data retriever class.

    Simulates a setting where a noisy mixture of sources is observed by the nodes of the network.

    Formally, the signals generated are given by :math:`\mathbf{y}(t)=A(t)\cdot\mathbf{d}(t)+\mathbf{n}(t)`, where :math:`\mathbf{d}\in\mathbb{R}^L` corresponds to the source signal, :math:`\mathbf{n}\in\mathbb{R}^M` to the noise and :math:`A\in\mathbb{R}^{M\times L}` to the mixture matrix. The non-stationarity of :math:`\mathbf{y}` follows from the dependence of :math:`A` on time, where :math:`A(t)=A_0+\Delta\cdot w(t)`, with :math:`w` representing a weight function varying in time.

    The signal :math:`\mathbf{y}` is finally normalized to have unit norm and zero mean.

    The steering matrix is given by :math:`B\in\mathbb{R}^{M\times P}` and the constraint is equal to :math:`H\in\mathbb{R}^{Q\times P}`.

    Attributes
    ----------
    data_window_params : DataWindowParameters
        Class instance storing the parameters that define a window of data.
    nb_sensors : int
        Number of sensors in the network. Equals to :math:`M`, the dimension of :math:`\mathbf{y}`.
    nb_sources : int
        Number of sources. Represents the number of true number of sources that generate the data. Equals to :math:`L`, the dimension of :math:`\mathbf{d}`.
    nb_windows : int
        Number of windows of data.
    rng : np.random.Generator
        Random number generator for reproducibility.
    nb_filters : int
        Number of filters. Equals to :math:`Q`.
    nb_steering : int | None
        Number of steering vectors. If None, will be fixed to :math:`Q`. By default None.
    signal_var : float
        Variance of the signals of interest, i.e., :math:`\mathbf{d}`. By default 0.5.
    noise_var : float
        Variance of the noise, i.e., :math:`\mathbf{n}`. By default 0.1.
    mixture_var : float
        Variance of the elements of mixture matrix :math:`A_0`. By default 0.5.
    diff_var : float
        Norm of :math:`\Delta`. By default 1.
    """

    def __init__(
        self,
        data_window_params: DataWindowParameters,
        nb_sensors: int,
        nb_sources: int,
        nb_windows: int,
        rng: np.random.Generator,
        nb_filters: int,
        nb_steering: int | None = None,
        signal_var: float = 0.5,
        noise_var: float = 0.1,
        mixture_var: float = 0.5,
        diff_var: float = 1,
    ) -> None:
        self.data_window_params = data_window_params
        nb_samples = data_window_params.window_length
        self.D = rng.normal(
            loc=0,
            scale=np.sqrt(signal_var),
            size=(nb_sources, nb_samples),
        )
        self.A_0 = rng.normal(
            loc=0, scale=np.sqrt(mixture_var), size=(nb_sensors, nb_sources)
        )
        self.Delta = rng.normal(
            loc=0, scale=np.sqrt(mixture_var), size=(nb_sensors, nb_sources)
        )
        self.Delta = (
            self.Delta
            * np.linalg.norm(self.A_0, "fro")
            * diff_var
            / np.linalg.norm(self.Delta, "fro")
        )
        self.noise = rng.normal(
            loc=0,
            scale=np.sqrt(noise_var),
            size=(nb_sensors, nb_samples),
        )
        self.nb_filters = nb_filters
        self.nb_steering = nb_steering if nb_steering is not None else nb_filters
        self.B = self.A_0[:, 0:nb_steering]
        self.H = rng.standard_normal(size=(self.nb_filters, self.nb_steering))

        self.weights = self.weight_function(nb_windows)

    def get_data_window(self, window_id: int) -> ProblemInputs:
        Y_window = (
            self.A_0 + self.Delta * self.weights[window_id]
        ) @ self.D + self.noise
        Y_window = normalize(Y_window)
        lcmv_inputs = ProblemInputs(
            fused_signals=[Y_window],
            fused_constants=[self.B],
            global_parameters=[self.H],
        )
        return lcmv_inputs

    get_data_window.__doc__ = DataRetriever.get_data_window.__doc__

    def weight_function(self, nb_windows: int) -> np.ndarray:
        """
        Weight function :math:`w` for the non-stationarity of the signals. Here, a piecewise linear function is used.

        Parameters
        ----------
        nb_windows : int
            Number of windows of data.
        """
        if nb_windows < 10:
            weights = np.zeros(nb_windows)
        else:
            segment_1 = np.linspace(0, 1, int(5 * nb_windows / 10), endpoint=False)
            segment_2 = np.linspace(0, 1, int(3 * nb_windows / 10), endpoint=False)
            segment_3 = np.linspace(0, 1, int(2 * nb_windows / 10), endpoint=False)

            weights = np.concatenate([segment_1, segment_2, segment_3])
        return weights

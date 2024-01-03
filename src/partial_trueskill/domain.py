import abc
import inspect
import math
from dataclasses import dataclass
import typing
import statistics


@dataclass(frozen=True)
class Parameters:
    static_performance_spread: float
    constant_additional_variance: float

    @property
    def beta(self): return self.static_performance_spread

    @property
    def tau(self): return self.constant_additional_variance


# noinspection PyStatementEffect
class Rating(abc.ABC):
    """
    Must have:
    mean: float
    variance: float
    beta_count: int
    """
    mean: float
    variance: float
    beta_count: int

    def sigma_variance_for_std_dev(self) -> float:
        return self.variance ** 2

    def update_mean_and_variance(self, event: 'Event'):
        """
        This order is required because the old variance is used in both calculations whereas the old mean is only used in `update_mean`.
        :return:
        """
        self.update_mean(event)
        self.update_variance(event)

    @abc.abstractmethod
    def update_mean(self, event: 'Event', won_or_lost: typing.Literal[1, -1, None] = None):
        ...

    @abc.abstractmethod
    def update_variance(self, event: 'Event'):
        ...


@dataclass
class ConstantRating(Rating):
    is_set: bool
    variance: float
    mean: float
    beta_count = 0

    def update_mean(self, event, won_or_lost: typing.Literal[1, -1, None] = None):
        if self.is_set: return
        self.mean = standard_mean_update(self, event, won_or_lost)

    def update_variance(self, event):
        if self.is_set: return
        self.variance = standard_variance_update(self, event)


@dataclass
class SkillBasedRating(Rating):
    mean: float
    variance: float
    beta_count = 1

    def update_mean(self, event, won_or_lost: typing.Literal[1, -1, None] = None):
        self.mean = standard_mean_update(self, event, won_or_lost)

    def update_variance(self, event):
        self.variance = standard_variance_update(self, event)


@dataclass
class RateableTotality(Rating):
    name: str
    ratings: list[Rating]

    @property
    def mean(self):
        return sum([rating.mean for rating in self.ratings])

    @property
    def beta_count(self):
        return sum([rating.beta_count for rating in self.ratings])

    @property
    def variance(self):
        return sum([rating.variance for rating in self.ratings])

    @typing.override
    def sigma_variance_for_std_dev(self) -> float:
        return sum([rating.sigma_variance_for_std_dev() for rating in self.ratings])

    def update_mean(self, event, won_or_lost=None):
        for rating in self.ratings:
            rating.update_mean(event, event.direction_of_weight(self))

    def update_variance(self, event):
        for rating in self.ratings:
            rating.update_variance(event)


@dataclass
class Event:
    weight: float  # MUST BE 0 < weight <= 1!
    name: str
    winner: Rating
    loser: Rating
    parameters: Parameters

    def __post_init__(self):
        """
        Done based in the format of non-dependent variables first and then using those to build subsequent variables.
        """
        self.__delta = self._delta()
        self.__std_dev_of_performances = self._std_dev_of_performances()
        self.__z_factor = self._z_factor()
        self.__mean_scale = self._mean_scale()
        self.__variance_scale = self._variance_scale()

    # <editor-fold desc="Delta">
    def _delta(self) -> float:
        return self.winner.mean - self.loser.mean

    @property
    def delta(self): return self.__delta

    # </editor-fold>

    # <editor-fold desc="C">
    def _std_dev_of_performances(self) -> float:
        # sqrt(beta_count*beta**2 + sum(variance**2 for all variances)
        # :return: V
        return math.sqrt(
            ((self.winner.beta_count + self.loser.beta_count) * self.parameters.static_performance_spread ** 2)
            + self.winner.sigma_variance_for_std_dev() + self.loser.sigma_variance_for_std_dev()
        )

    @property
    def std_dev_of_performances(self): return self.__std_dev_of_performances

    @property
    def c(self): return self.__std_dev_of_performances

    # </editor-fold>

    # <editor-fold desc="Z Factor">
    def _z_factor(self) -> float:
        return self.delta / self.std_dev_of_performances

    @property
    def z_factor(self): return self.__z_factor

    # </editor-fold>

    # <editor-fold desc="V">
    def _mean_scale(self) -> float:
        # z_factor = delta/std-dev
        # pdf(z_factor)/cdf(z_factor)
        normal_dist = statistics.NormalDist()
        return normal_dist.pdf(self.z_factor) / normal_dist.cdf(self.z_factor)

    @property
    def mean_scale(self): return self.__mean_scale

    @property
    def v(self): return self.__mean_scale

    # </editor-fold>

    # <editor-fold desc="W">
    def _variance_scale(self) -> float:
        return self.v * (self.v + self.z_factor)

    @property
    def variance_scale(self): return self.__variance_scale

    @property
    def w(self): return self.__variance_scale

    # </editor-fold>

    def direction_of_weight(self, rating: Rating) -> typing.Literal[1, -1]:
        """
        Returns the direction of the weight to determine whether the rating should go up or down.
        :param rating: Rating object to be determined whether won or lost
        :return: 1 or -1
        """
        if rating == self.winner:
            return 1
        return -1


def standard_mean_update(rating: Rating, event: Event, won_or_lost: typing.Literal[1, -1, None] = None) -> float:
    """

    :param rating: Rating to update (not in place returns new mean as float)
    :param event: The event which the rating object played which will change its rating
    :param won_or_lost: Whether the rating object won or lost (MUST BE `1, -1 or None`)
    :return: New mean for rating
    """
    if won_or_lost is None:
        won_or_lost = event.direction_of_weight(rating)
    new_mean = rating.mean + (event.weight * won_or_lost) * (event.mean_scale * (
            (rating.variance ** 2 + event.parameters.tau ** 2) / event.std_dev_of_performances)
                                                             )
    return new_mean


def standard_variance_update(rating: Rating, event: Event) -> float:
    tau_sqr = event.parameters.constant_additional_variance ** 2
    variance_sqr = rating.variance ** 2
    new_variance_sqr = (variance_sqr + tau_sqr) * (1 - abs(event.weight) * (
        # abs might not be necessary since direction is determined in mean update specifically
            event.variance_scale * (
            (variance_sqr + tau_sqr) / event.std_dev_of_performances ** 2)
    ))
    return math.sqrt(new_variance_sqr)


def name_of_func_in_scope():
    return inspect.stack()[1][3]


if __name__ == '__main__':
    winner = SkillBasedRating(mean=1200, variance=150)
    loser = SkillBasedRating(mean=1400, variance=40)
    test_parameters = Parameters(200, 0)
    test_event = Event(1, 'test event', winner, loser, test_parameters)

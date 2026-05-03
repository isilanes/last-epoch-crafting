from enum import Enum, auto
from typing import Protocol, Self

from pydantic import BaseModel


class ObjectType(Enum):
    GOOD_UNIQUE_LP0 = auto()
    GOOD_UNIQUE_LP1 = auto()
    GOOD_UNIQUE_LP2 = auto()
    BAD_UNIQUE_LP0 = auto()
    BAD_UNIQUE_LP1 = auto()
    BAD_UNIQUE_LP2 = auto()


class Probabilities(BaseModel):
    """Object to provide the probability for all outcomes in all processes."""

    unique_is_good: float
    lp1: float
    lp2: float = 0.0

    @property
    def unique_is_bad(self) -> float:
        return 1 - self.unique_is_good

    @property
    def lp0(self) -> float:
        return 1 - self.lp1 - self.lp2


class CraftProcess(Protocol):

    def __init__(self, probs: Probabilities) -> None:
        self.probs = probs

    def apply(self, pop: dict[ObjectType, float]) -> dict[ObjectType, float]:
        pass


class Drop(CraftProcess):

    def __init__(self, probs: Probabilities) -> None:  # noqa
        super().__init__(probs)

    def apply(self, pop: dict[ObjectType, float]) -> dict[ObjectType, float]:
        return {
            ObjectType.GOOD_UNIQUE_LP0: self.probs.unique_is_good * self.probs.lp0,
            ObjectType.GOOD_UNIQUE_LP1: self.probs.unique_is_good * self.probs.lp1,
            ObjectType.GOOD_UNIQUE_LP2: self.probs.unique_is_good * self.probs.lp2,
            ObjectType.BAD_UNIQUE_LP0: self.probs.unique_is_bad * self.probs.lp0,
            ObjectType.BAD_UNIQUE_LP1: self.probs.unique_is_bad * self.probs.lp1,
            ObjectType.BAD_UNIQUE_LP2: self.probs.unique_is_bad * self.probs.lp2,
        }


class Population(BaseModel):
    """Holds amount of items of every object type."""

    population: dict[ObjectType, float] = {}

    def apply(self, craft: CraftProcess) -> Self:
        self.population = craft.apply(self.population)

    def __str__(self) -> str:
        return "\n".join([f"{k.name:15s}: {v:.3f}" for k, v in self.population.items()])



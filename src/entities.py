from enum import Enum, auto
from typing import Protocol

from pydantic import BaseModel


class Unique(Enum):
    GOOD_LP0 = auto()
    GOOD_LP1 = auto()
    GOOD_LP2 = auto()
    BAD_LP0 = auto()
    BAD_LP1 = auto()
    BAD_LP2 = auto()


class Legendary(Enum):
    GOOD_LP1 = auto()
    GOOD_LP2 = auto()
    BAD_LP1 = auto()
    BAD_LP2 = auto()


LootItem = Unique | Legendary
Fractions = dict[LootItem, float]


class Probabilities(BaseModel):
    """Object to provide the probability for all outcomes in all processes."""

    unique_is_good: float        # probability that a Unique rolls as "good"
    exalted_is_good: float       # probability that an Exalted (with proper affixes) rerolls as "good"
    nemesis_stays_unique: float  # probability that the Unique in the Nemesis gets added LP, and not affixes
    lp1: float                   # probability for {roll LP -> turns out LP1}
    lp2: float = 0.0             # probability for {roll LP -> turns out LP2}

    @property
    def unique_is_bad(self) -> float:
        return 1 - self.unique_is_good

    @property
    def lp0(self) -> float:
        return 1 - self.lp1 - self.lp2

    @property
    def exalted_is_bad(self) -> float:
        return 1 - self.exalted_is_good


class CraftProcess(Protocol):

    def __init__(self, probabilities: Probabilities):
        pass

    @staticmethod
    def apply_to(item: LootItem) -> tuple[LootItem, float]:
        pass


class RerollQuality:

    def __init__(self, probabilities: Probabilities):
        self.probabilities = probabilities

    def apply_to(self, item: LootItem) -> tuple[LootItem, float]:
        p = self.probabilities.unique_is_good / (1 + self.probabilities.unique_is_good)

        if item is Unique.BAD_LP0:
            return Unique.GOOD_LP0, p

        if item is Unique.BAD_LP1:
            return Unique.GOOD_LP1, p

        raise ValueError(f"Do not apply RerollQuality to {item}")


class Population(BaseModel):
    """Holds amount of items of every object type."""

    fractions: Fractions = {}

    def __str__(self) -> str:
        strings = [
            "---\n",
            "\n".join([f"UNIQUE:{item.name:10s}: {self.fractions.get(item, 0.0):6.3f}" for item in Unique]),
            "\n\n",
            "\n".join([f"LEGEND:{item.name:10s}: {self.fractions.get(item, 0.0):6.3f}" for item in Legendary]),
        ]

        return "".join(strings)

    def apply(self, craft: CraftProcess, item: LootItem) -> None:
        new, p = craft.apply_to(item)
        self.fractions[new] = self.fractions.get(new, 0.0) + p * self.fractions[item]
        self.fractions[item] = 0.0

from enum import Enum, auto

from pydantic import BaseModel


class LootItem(Enum):
    pass


class Unique(LootItem):
    GOOD_LP0 = auto()
    GOOD_LP1 = auto()
    GOOD_LP2 = auto()
    BAD_LP0 = auto()
    BAD_LP1 = auto()
    BAD_LP2 = auto()


class Legendary(LootItem):
    GOOD_LP1 = auto()
    GOOD_LP2 = auto()
    BAD_LP1 = auto()
    BAD_LP2 = auto()


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


class Population(BaseModel):
    """Holds amount of items of every object type."""

    fractions: dict[LootItem, float] = {}

    def __str__(self) -> str:
        strings = [
            "---\n",
            "\n".join([f"UNIQUE:{item.name:10s}: {self.fractions.get(item, 0.0):6.3f}" for item in Unique]),
            "\n\n",
            "\n".join([f"LEGEND:{item.name:10s}: {self.fractions.get(item, 0.0):6.3f}" for item in Legendary]),
        ]

        return "".join(strings)


def drop(probs: Probabilities, normalize: float = 1.0) -> Population:
    """
    Produce a Population of items according to the drop chances from monsters.

    Args:
        probs (Probabilities):
            Probabilities object, holding probabilities for dropping each object type.
        normalize (optional float):
            If given, normalize total population to this number. By default, normalize to 1.

    Returns:
        A Population of object types.
    """
    return Population(
        fractions={
            Unique.BAD_LP0: probs.unique_is_bad * probs.lp0 * normalize,
            Unique.BAD_LP1: probs.unique_is_bad * probs.lp1 * normalize,
            Unique.BAD_LP2: probs.unique_is_bad * probs.lp2 * normalize,
            Unique.GOOD_LP0: probs.unique_is_good * probs.lp0 * normalize,
            Unique.GOOD_LP1: probs.unique_is_good * probs.lp1 * normalize,
            Unique.GOOD_LP2: probs.unique_is_good * probs.lp2 * normalize,
        },
    )

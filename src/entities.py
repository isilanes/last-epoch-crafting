from enum import Enum, auto
from typing import Self

from pydantic import BaseModel


class Unique(Enum):
    GOOD_LP0 = "Good Unique LP0"
    GOOD_LP1 = "Good Unique LP1"
    GOOD_LP2 = "Good Unique LP2"
    BAD_LP0 = "Bad Unique LP0"
    BAD_LP1 = "Bad Unique LP1"
    BAD_LP2 = "Bad Unique LP2"

    @property
    def to_str(self) -> str:
        return self.value


class Legendary(Enum):
    GOOD_LP1 = "Good Legendary LP1"
    GOOD_LP2 = "Good Legendary LP2"
    BAD_LP1 = "Bad Legendary LP1"
    BAD_LP2 = "Bad Legendary LP2"

    @property
    def to_str(self) -> str:
        return self.value


LootItem = Unique | Legendary
Fractions = dict[LootItem, float]


class Probabilities(BaseModel):
    """Object to provide the probability for all outcomes in all processes."""

    unique_is_good: float        # probability that a Unique rolls as "good"
    exalted_is_good_1: float     # probability that an Exalted (with ONE proper affix) rerolls as "good"
    exalted_is_good_2: float     # probability that an Exalted (with TWO proper affixes) rerolls as "good"
    nemesis_stays_unique: float  # probability that the Unique in the Nemesis gets added LP, and not affixes
    lp1: float                   # probability for {roll LP -> turns out LP1}
    lp2: float = 0.0             # probability for {roll LP -> turns out LP2}
    nemesis_lp1: float = 1.0     # probability for Nemesis to move from LP0 to LP1

    @property
    def unique_is_bad(self) -> float:
        return 1 - self.unique_is_good

    @property
    def lp0(self) -> float:
        return 1 - self.lp1 - self.lp2

    @property
    def exalted_is_bad_1(self) -> float:
        return 1 - self.exalted_is_good_1

    @property
    def exalted_is_bad_2(self) -> float:
        return 1 - self.exalted_is_good_2

    @property
    def nemesis_lp2(self) -> float:
        return 1 - self.nemesis_lp1


class CraftProcess(BaseModel):
    name: str
    applies_to: list[LootItem]
    probabilities: Probabilities

    @staticmethod
    def apply_to(item: LootItem) -> 'Population':
        pass


class CraftAction(BaseModel):
    """A craft action (CraftProcess plus LootItem to apply it to)."""
    item: LootItem
    process: CraftProcess

    def __str__(self) -> str:
        return f"{self.item.to_str} + {self.process.name}"


class CraftPlan(BaseModel):
    """A selection of what to do to each LootItem, and in what order."""

    actions: list[CraftAction] = []

    @classmethod
    def add(cls, plan: Self, action: CraftAction) -> Self:
        actions = [*plan.actions, action]

        return cls(actions=actions)

    def __str__(self) -> str:
        lines = [str(a) for a in self.actions]
        lines = ["---", *lines]

        return "\n".join(lines)


class RerollQuality(CraftProcess):
    name: str = "[Reroll Quality]"
    applies_to: list[LootItem] = [
        Unique.BAD_LP0,
        Unique.BAD_LP1,
        Unique.BAD_LP2,
        Legendary.BAD_LP1,
        Legendary.BAD_LP2,
    ]

    def apply_to(self, item: LootItem) -> 'Population':
        pu = self.probabilities.unique_is_good
        pe1 = self.probabilities.exalted_is_good_1
        pe2 = self.probabilities.exalted_is_good_2
        pop_u = pu / (1 + pu)
        pop_l1 = pu * pe1 / (1 + pu * pe1)
        pop_l2 = pu * pe2 / (1 + pu * pe2)
        fractions = None

        if item is Unique.BAD_LP0:
            fractions = {Unique.GOOD_LP0: pop_u}

        if item is Unique.BAD_LP1:
            fractions = {Unique.GOOD_LP1: pop_u}

        if item is Unique.BAD_LP2:
            fractions = {Unique.GOOD_LP2: pop_u}

        if item is Legendary.BAD_LP1:
            fractions = {Legendary.GOOD_LP1: pop_l1}

        if item is Legendary.BAD_LP2:
            fractions = {Legendary.GOOD_LP2: pop_l2}

        if fractions is None:
            raise ValueError(f"Can not apply RerollQuality to {item}")

        return Population(fractions=fractions)


class Nemesis(CraftProcess):
    name: str = "[Nemesis]"
    applies_to: list[LootItem] = [
        Unique.BAD_LP0,
        Unique.GOOD_LP0,
    ]

    def apply_to(self, item: LootItem) -> 'Population':
        pu = self.probabilities.nemesis_stays_unique
        p1 = self.probabilities.nemesis_lp1
        p2 = self.probabilities.nemesis_lp2
        fractions = None

        if item is Unique.BAD_LP0:
            fractions = {
                Unique.BAD_LP1: pu * p1,
                Unique.BAD_LP2: pu * p2,
                Legendary.BAD_LP1: (1 - pu) * p1,
                Legendary.BAD_LP2: (1 - pu) * p2,
            }

        if item is Unique.GOOD_LP0:
            fractions = {
                Unique.GOOD_LP1: pu * p1,
                Unique.GOOD_LP2: pu * p2,
                Legendary.BAD_LP1: (1 - pu) * p1,  # Legendaries out of a Nemesis will always be bad
                Legendary.BAD_LP2: (1 - pu) * p2,  # Legendaries out of a Nemesis will always be bad
            }

        if fractions is None:
            raise ValueError(f"Can not apply Nemesis to {item}")

        return Population(fractions=fractions)


class Slam(CraftProcess):
    name: str = "[Slam]"
    applies_to: list[LootItem] = [
        Unique.BAD_LP1,
        Unique.BAD_LP2,
        Unique.GOOD_LP1,
        Unique.GOOD_LP2,
    ]

    def apply_to(self, item: LootItem) -> 'Population':
        fractions = None

        if item is Unique.BAD_LP1:
            fractions = {Legendary.BAD_LP1: 1.0}

        if item is Unique.BAD_LP2:
            fractions = {Legendary.BAD_LP2: 1.0}

        if item is Unique.GOOD_LP1:
            fractions = {Legendary.GOOD_LP1: 1.0}

        if item is Unique.GOOD_LP2:
            fractions = {
                Legendary.GOOD_LP1: 1.0 / 3.0,
                Legendary.BAD_LP1: 2.0 / 3.0,
            }

        if fractions is None:
            raise ValueError(f"Can not apply Slam to {item}")

        return Population(fractions=fractions)


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

    def apply_action(self, action: CraftAction) -> None:
        new = action.process.apply_to(action.item)
        p = self.fractions[action.item]

        for k, v in new.fractions.items():
            self.fractions[k] = self.fractions.get(k, 0) + p * v

        self.fractions[action.item] = 0.0

    def apply_craft_plan(self, plan: CraftPlan, goal: list[LootItem]) -> bool:
        max_cycles = 5
        i = 0
        while not self.has_only(*goal):
            i += 1
            for action in plan.actions:
                self.apply_action(action)
            if i > max_cycles:
                return False

        return True

    def has_only(self, *items: LootItem) -> bool:
        for item in self.fractions:
            if item not in items and self.fractions[item] > 0:
                return False

        return True


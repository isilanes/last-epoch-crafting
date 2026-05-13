from src.entities import (
    Probabilities,
    Population,
    Unique,
    RerollQuality,
    CraftProcess,
    Legendary,
    CraftPlan,
    CraftAction, Nemesis, Slam,
)


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


def make_craft_plans(crafts: list[CraftProcess]) -> list[CraftPlan]:
    """
    Given a list of craft processes, produce a list of craft plans.

    Args:
        crafts (list of CraftProcesses):
            Available craft processes.

    Returns:
        A list of craft plans.
    """
    plans = [CraftPlan()]  # base blank plan
    for item in(*Unique, *Legendary):
        actions = [CraftAction(item=item, process=craft) for craft in crafts if item in craft.applies_to]
        if not actions:
            continue

        new = []
        for plan in plans:
            for action in actions:
                extended = CraftPlan.add(plan, action)
                new.append(extended)
        plans = new

    print(len(plans), "plans created")
    print(plans[0])

    return plans


def main():
    probs = Probabilities(
        unique_is_good=0.013,
        exalted_is_good_1=0.1,
        exalted_is_good_2=0.0,
        nemesis_stays_unique=0.25,
        nemesis_lp1=1.0,
        lp1=0.2,
    )
    population = drop(probs, normalize=100)
    crafts = [
        craft(probabilities=probs)
        for craft in (
            RerollQuality,
            Nemesis,
            Slam,
        )
    ]

    # craft_plans = make_craft_plans(crafts)

    print(population)
    population.apply(crafts[1], Unique.GOOD_LP0)
    print(population)
    population.apply(crafts[1], Unique.BAD_LP0)
    print(population)
    population.apply(crafts[2], Unique.BAD_LP1)
    print(population)
    population.apply(crafts[0], Legendary.BAD_LP1)
    print(population)
    population.apply(crafts[2], Unique.GOOD_LP1)
    print(population)


if __name__ == "__main__":
    main()

# nemesis = Nemesis(probs)
# reroll_q = RerollQuality(probs)
#
# population.apply(reroll_q, LootItem.BAD_UNIQUE_LP0)
# print(population)
#
# population.apply(nemesis, LootItem.GOOD_UNIQUE_LP0)
# print(population)
#
# population.apply(reroll_q, LootItem.BAD_UNIQUE_LP1)
# print(population)
#
# population.apply(reroll_q, LootItem.BAD_LEGENDARY_LP1)
# print(population)

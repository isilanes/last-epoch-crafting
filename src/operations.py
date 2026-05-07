from src.entities import Probabilities, Population, Unique, RerollQuality, CraftProcess, LootItem, Legendary, CraftPlan, \
    CraftAction


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

    A craft plan is a list of the form:

    [
        (CraftProcess1, LootItem1),
        (CraftProcess2, LootItem2),
        ...

    ]

    where it is specified what crafting to apply to each loot item type AND it is provided
    in the order that it should be applied (in-game the order is not important).

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

    for plan in plans:
        print("---")
        for action in plan.actions:
            print("ac:", action)




def main():
    probs = Probabilities(
        unique_is_good=0.013,
        exalted_is_good=0.1,
        nemesis_stays_unique=0.25,
        lp1=0.2,
    )
    population = drop(probs, normalize=100)
    crafts = [
        c(probabilities=probs)
        for c in (
            RerollQuality,
        )
    ]

    craft_plans = make_craft_plans(crafts)

    population.apply(crafts[0], Unique.BAD_LP0)


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

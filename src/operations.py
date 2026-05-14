from src.entities import (
    Probabilities,
    Population,
    Unique,
    RerollQuality,
    CraftProcess,
    Legendary,
    CraftPlan,
    CraftAction, Nemesis, Slam, LootItem,
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


def make_craft_plans(crafts: list[CraftProcess], items: list[LootItem]) -> list[CraftPlan]:
    """
    Given a list of craft processes, produce a list of craft plans.

    Args:
        crafts (list of CraftProcesses):
            Available craft processes.
        items (list of LootItem):
            Available items types.

    Returns:
        A list of craft plans.
    """
    plans = [CraftPlan()]  # base blank plan
    for item in items:
        actions = [CraftAction(item=item, process=craft) for craft in crafts if item in craft.applies_to]
        if not actions:
            continue

        new = []
        for plan in plans:
            for action in actions:
                extended = CraftPlan.add(plan, action)
                new.append(extended)
        plans = new

    return plans


def main():
    valid_items = [
        Unique.GOOD_LP0,
        Unique.GOOD_LP1,
        Unique.BAD_LP0,
        Unique.BAD_LP1,
        Legendary.GOOD_LP1,
        Legendary.BAD_LP1,
    ]
    goal = [Legendary.GOOD_LP1]
    valid_crafts = [RerollQuality, Nemesis, Slam]
    probs = Probabilities(
        unique_is_good=0.013,
        exalted_is_good_1=0.1,
        exalted_is_good_2=0.0,
        nemesis_stays_unique=0.25,
        nemesis_lp1=1.0,
        lp1=0.2,
    )
    crafts = [craft(probabilities=probs) for craft in valid_crafts]

    craft_plans = make_craft_plans(crafts, items=valid_items)
    print(len(craft_plans), "plans created")

    plans = []
    for plan in craft_plans:
        population = drop(probs, normalize=100)
        success = population.apply_craft_plan(plan, goal=goal)
        if success:
            pop = population.fractions[Legendary.GOOD_LP1]
            plans.append((pop, plan))
        else:
            print("Failure!")
            print(population)

    plans.sort()
    worst = plans[0][0]
    for pop, plan in plans:
        print(f"Good Legendary LP1: {pop:6.3f} ({pop/worst:4.2f}x)")

    print("\nBest plan:")
    print(plans[0][1])


if __name__ == "__main__":
    main()

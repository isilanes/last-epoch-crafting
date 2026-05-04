from src.entities import Probabilities, Population, Unique, RerollQuality


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


def main():
    probs = Probabilities(
        unique_is_good=0.013,
        exalted_is_good=0.1,
        nemesis_stays_unique=0.25,
        lp1=0.2,
    )
    population = drop(probs, normalize=100)
    print(population)

    rq = RerollQuality(probabilities=probs)

    population.apply(rq, Unique.BAD_LP0)
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

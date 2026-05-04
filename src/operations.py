from src.entities import Probabilities, drop


probs = Probabilities(
    unique_is_good=0.013,
    exalted_is_good=0.1,
    nemesis_stays_unique=0.25,
    lp1=0.2,
)
population = drop(probs, 100)
print(population)

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

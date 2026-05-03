from src.entities import Probabilities, Drop, Population


probs = Probabilities(unique_is_good=0.013, lp1=0.2)
drop = Drop(probs=probs)

population = Population()
population.apply(drop)

print(population)

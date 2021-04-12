import random

stat = {"s": 0, "l": 0, "i": 0, "v": 0}
stats = 0
for i in stat:
    stat[i] = random.randint(1, 4)
    stats += stat[i]
print(stat, stats)

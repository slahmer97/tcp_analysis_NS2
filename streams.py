import random
import math
from statistics import mean

def streams(total_quantity, min_size = 15*1000):
    s = 0.0
    strms = []
    while s < total_quantity:
        u = random.random()
        k = math.log(4) / math.log(5)
        t = min_size / (u ** (1 / k))
        s += t
        strms.append(t)

    d = sum(strms) - total_quantity
    strms[-1] -= d
    return strms

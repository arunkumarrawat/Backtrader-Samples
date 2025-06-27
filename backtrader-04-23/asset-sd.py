import math
import matplotlib.pyplot as plt

def s(x, Sa, Sb, corr):
    return math.sqrt( (x**2) * Sa**2 + ((1-x)**2) * Sb**2 + 2 * x * (1-x) * corr * Sa * Sb )

def exp_return(x):
    return(9*x+18*(1-x))

import pandas as pd
import numpy as np

# params
corr_set = [-1, -0.5, 0, 0.5, 1]

# standard deviation set
std_dev = []
std_dev_sets = []


rets=list(map(exp_return,[x/100 for x in range(101)]))

# calculate standard deviations
for corr in corr_set:
    std_dev = []
    for x in range(0,101):
        std_dev.append(s(x/100, 0.1, 0.3, corr))
    std_dev_sets.append(std_dev)

# 繪圖
plt.figure(figsize=(15, 10))
plt.plot(std_dev_sets[0], rets, label='corr = -1')
plt.plot(std_dev_sets[1], rets, label='corr = -0.5')
plt.plot(std_dev_sets[2], rets, label='corr = 0')
plt.plot(std_dev_sets[3], rets, label='corr = 0.5')
plt.plot(std_dev_sets[4], rets, label='corr = 1')
plt.xlabel('Stand Dev(%)', fontsize=20)
plt.ylabel('Expected Rate of Return(%)', fontsize=20)
plt.xticks(fontsize=15)
plt.yticks(fontsize=15)
plt.legend(loc='upper left',prop={'size': 15})
plt.show()
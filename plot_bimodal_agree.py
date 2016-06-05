import matplotlib.pyplot as plt
import numpy as np

bimodal = [86.21, 87.34, 88.17, 88.64, 89.07, 89.19]
agreepd = [86.20, 87.32, 88.13, 88.69, 89.26, 89.47]
log2size = [10, 11, 12, 13, 14, 15]

agree_warmup = [49.0, 39.0, 76.5, 75.0, 88.0, 89.5, 95.0, 93.5, 93.0, 79.5, 94.0, 93.5, 76.0,
                84.0, 90.0, 87.0, 94.5, 92.0, 91.0, 95.0]
x_ticks = [200 * (i + 1) for i in range(len(agree_warmup))]

bimodal_warmup = [83.0, 75.0, 88.5, 82.5, 88.5, 89.5, 94.5, 94.0, 91.0, 84.0, 94.0, 91.0, 90.5,
                  89.5, 91.5, 94.0, 94.0, 91.5, 91.5, 92.5]


plt.figure(1)
plt.grid(True)
plt.plot(log2size, bimodal, 'r^-', label='Bimodal Predictor')
plt.plot(log2size, agreepd, 'bs-', label='Agree Predictor')

plt.xticks(log2size)
plt.xlabel('Predictor Size (log2(Table Entries)')
plt.ylabel('Prediction Accuracy (%)')
plt.legend(loc=2)

plt.figure(2)
plt.grid(True)
plt.plot(x_ticks, bimodal_warmup, 'r^-', label='Bimodal Predictor')
plt.plot(x_ticks, agree_warmup, 'bs-', label='Agree Predictor')

#plt.xticks(x_ticks)
plt.xlabel('Number of Branches from the Beginning')
plt.ylabel('Prediction Accuracy (%)')
plt.legend(loc=4)
plt.show()

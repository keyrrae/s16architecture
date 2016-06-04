import random
import matplotlib.pyplot as plt
import numpy as np

Hs = [1, 2, 4, 8, 16, 32, 64, 128, 256, 512, 1024, 2048, 4096, 8192]
experiment_times = 100000

cores = [1, 2, 4, 8, 16]
symbols = ['b^-', 'rx-', 'gD-', 'ks-', 'mv-']
count = 0

for core in cores:
    #fig = plt.figure(count)
    plt.grid(True)

    average = []
    upper = []
    lower = []
    speedup = []
    for H in Hs:

        speedup_temp = []
        for time in xrange(experiment_times):
            trans = [random.randint(0, H) for i in xrange(core)]
            trans_count = {}
            for item in trans:
                if item not in trans_count:
                    trans_count[item] = 1
                else:
                    trans_count[item] += 1
            max_conflict = max(trans_count.values()) - 1

            speedup_temp.append(2.0 * 2.0 * 1e9 * core / (160.0 + max_conflict * 160.0) / (4e7/1.6))

        average.append(sum(speedup_temp) / float(len(speedup_temp)))
        upper.append(max(speedup_temp))
        lower.append(min(speedup_temp))
        speedup.append(speedup_temp)
    upper_error = np.asarray(upper)
    lower_error = np.asarray(lower)
    errors = [lower_error, upper_error]

    lbl = str(core) + ' ' + ("core" if core == 1 else "cores")

    plt.semilogx(Hs, average, symbols[count], label=lbl)
    plt.xlabel("Size of the Hash Table (Number of Entries)")
    plt.ylabel("Average Speedup")
    plt.title("Speedup vs. Size of the Hash Table")
    #plt.xticks(Hs)
    count += 1
plt.legend(loc=2)
plt.show()

print "hello"

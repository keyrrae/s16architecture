import math
import matplotlib.pyplot as plt

c = 0.5/100
p = range(2, 9)
s = []
sid = []
for pval in p:
    s.append(1.0/(1.0/pval + (pval)/10.0 + 1.0/100))
    sid.append(1.0/(1.0/pval + 1.0/100))

plt.figure(1)
plt.grid(True)

plt.xlabel("Number of Pipeline Stages")
plt.ylabel("Speedup")
plt.title("W = 1 ns, B = 100, R = 100 ps")
plt.xticks(p)
plt.plot(p, s, '-^')

plt.figure(2)
plt.grid(True)

plt.xlabel("Number of Pipeline Stages")
plt.ylabel("Speedup")
plt.title("W = 1 ns, B = 100, R = 0 ns")
plt.xticks(p)
plt.plot(p, sid, '-o')
plt.show()
# plt.xlim(1,256)
# plt.legend(bbox_to_anchor=(1,0.5), prop={'size':10}, loc='center left', numpoints=1)
# plt.tight_layout(pad=8)

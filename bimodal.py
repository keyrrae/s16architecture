from __future__ import print_function
import pyrtl
import math
import sys

# reference predictor from assignment 2

class singlebit_bimodal_predictor():
    def __init__(self, num_entries):
        self.num_entries = num_entries
        self.bimod_table = [0]*self.num_entries

    def get_prediction(self, pc):
        index = (pc >> 2) % self.num_entries
        return self.bimod_table[index]

    def update(self, pc, branch_outcome):
        index = (pc >> 2) % self.num_entries
        self.bimod_table[index] = branch_outcome


# Parameters
num_entries = 32768
render_trace = False
modulo = int(math.log(num_entries, 2))
modulo_mask = pyrtl.Const(num_entries - 1)

# Define Inputs and Outputs
pc, outcome = pyrtl.Input(32, 'pc'), pyrtl.Input(1, 'outcome')
prediction = pyrtl.Output(1, 'prediction')

# RTL description
bimod_table = pyrtl.MemBlock(bitwidth=1, addrwidth=modulo, name='history_table', asynchronous=True)
index_temp = pyrtl.Register(bitwidth=modulo, name='index_temp')
outcome_temp = pyrtl.Register(bitwidth=1, name='outcome_temp')
pc_shift_right_2bits = pc[-30:]


index = pyrtl.WireVector(bitwidth=modulo, name='index')
index <<= pc_shift_right_2bits & modulo_mask

index_temp.next <<= index

outcome_temp.next <<= outcome

bimod_table[index] <<= outcome
prediction <<= bimod_table[index]

# --- Simulation ---
sim_trace = pyrtl.SimulationTrace()
sim = pyrtl.FastSimulation(tracer=sim_trace)

predictor = singlebit_bimodal_predictor(num_entries)

# --- stimuli ---
f = open('serv1.trace', 'r')
correct_predictions = 0
total_predictions = 0
window_size = 200
moving_correct_predictions = 0
_ = f.readline()  # throw away first line
i = 0
predicts = []
moving_rate = []

line = f.readline()

while line:
    # get the two fields and convert them to integers
    [pc_val, branch_outcome] = [int(x, 0) for x in line.split()]

    this_prediction = predictor.get_prediction(pc_val)
    predicts.append(this_prediction)
    total_predictions += 1
    if this_prediction == branch_outcome:
        correct_predictions += 1
        moving_correct_predictions += 1
    predictor.update(pc_val, branch_outcome)
    i += 1
    if i == 50000:
        print(("%.1f" % (100 * float(total_predictions) / 3811906)) + '%')
        i = 0
    if i % window_size == 0:
        moving_rate.append(100 * moving_correct_predictions / float(window_size))
        moving_correct_predictions = 0
        line = f.readline()

    sim.step({pc: pc_val, outcome: branch_outcome})
    line = f.readline()

print("\n\nWarm up:")
i = 0
for rate in moving_rate:
    if i > 20:
        break
    print("%.1f" % rate)
    i += 1


# print out the statistics
print(predictor.__class__.__name__, 100 * correct_predictions / float(total_predictions))

print('--- Branch Prediction Simulation ---')
if render_trace:
    sim_trace.render_trace(trace_list=[pc, outcome, prediction, index, index_temp, outcome_temp], symbol_len=5, segment_size=16)
for i in range(total_predictions):
    if sim_trace.trace[prediction][i] != predicts[i]:
        print("Prediction results don't match at line: " + str(i))
        exit(1)

print('PyRTL simulation result matched with the reference predictor.')




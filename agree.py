from __future__ import print_function
import pyrtl
import math
import sys


class AgreePredictor():
    def __init__(self, num_PHT_entries, num_BBS_entries):
        self.num_PHT_entries = num_PHT_entries
        self.num_BBS_entries = num_BBS_entries
        self.PHT = [0]*self.num_PHT_entries
        self.BBS = [0] * num_BBS_entries
        self.PHT_mask = num_PHT_entries - 1
        #print(self.PHT_mask)
        self.BBS_mask = num_BBS_entries - 1
        #print(self.BBS_mask)
        self.BHR = 0
        self.BHR_mask = num_PHT_entries - 1

    def get_indices(self, pc):
        pc_shifted = pc >> 2
        PHT_index = (self.BHR ^ pc_shifted) & self.PHT_mask
        BBS_index = pc_shifted & self.BBS_mask
        return PHT_index, BBS_index

    def get_prediction(self, pc):
        PHTind, BBSind = self.get_indices(pc)
        # print(pc>>2)
        #print(PHTind, BBSind)
        PHT_result = (self.PHT[PHTind] & 2) >> 1
        #print('phtres', PHT_result)

        BBS_result = self.BBS[BBSind]
        #print('bbsres', BBS_result)
        return ~(PHT_result ^ BBS_result) & 1

    def update(self, pc, prediction, branch_outcome):
        #print('BHR', self.BHR)
        PHTind, BBSind = self.get_indices(pc)
        self.BHR = ((self.BHR << 1) | branch_outcome) & self.PHT_mask



        if prediction == self.BBS[BBSind]:
            if self.PHT[PHTind] < 3:
                self.PHT[PHTind] += 1
        else:
            if self.PHT[PHTind] > 0:
                self.PHT[PHTind] -= 1

        self.BBS[BBSind] = ~branch_outcome & 1
        #print("PHT", self.PHT[PHTind])

# Parameters
PHT_size = 1024
BBS_size = 4096
PHT_bitwidth = int(math.log(PHT_size, 2))
BBS_bitwidth = int(math.log(BBS_size, 2))
BHR_bitwidth = PHT_bitwidth
PHT_mask = pyrtl.Const(PHT_size - 1)
BBS_mask = pyrtl.Const(BBS_size - 1)

# Define Inputs and Outputs
pc_i, outcome_i = pyrtl.Input(32, 'pc'), pyrtl.Input(1, 'outcome')
prediction_o = pyrtl.Output(1, 'prediction')


# PyRTL description of the Agree Predictor
BHR_r = pyrtl.Register(bitwidth=BHR_bitwidth, name='BHR_r')
PHT_m = pyrtl.MemBlock(bitwidth=2, addrwidth=PHT_bitwidth, name='PHT_table', asynchronous=True)
BBS_m = pyrtl.MemBlock(bitwidth=1, addrwidth=BBS_bitwidth, name='BBS_table', asynchronous=True)

pc_shift_right_2bits = pc_i[-30:]
PHT_ind = pyrtl.WireVector(bitwidth=PHT_bitwidth, name='PHT_ind')
PHT_ind <<= (pc_shift_right_2bits ^ BHR_r) & PHT_mask

BBS_ind = pyrtl.WireVector(bitwidth=BBS_bitwidth, name='BBS_ind')
BBS_ind <<= pc_shift_right_2bits & BBS_mask

pred_PHT_res = pyrtl.WireVector(bitwidth=1, name='pred_pht_res')
pred_BBS_res = pyrtl.WireVector(bitwidth=1, name='pred_bbs_res')
prediction_int = pyrtl.WireVector(bitwidth=1, name='prediction_int')

pred_PHT_res <<= PHT_m[PHT_ind][-1]
pred_BBS_res <<= BBS_m[BBS_ind]
prediction_int <<= ~(pred_PHT_res ^ pred_BBS_res)

prediction_o <<= prediction_int
BHR_r.next <<= pyrtl.concat(BHR_r, outcome_i)
a = pyrtl.Const(1)

PHT_inc = pyrtl.WireVector(bitwidth=2, name='PHT_inc')
PHT_inc <<= PHT_m[PHT_ind] + pyrtl.Const(1)

PHT_dec = pyrtl.WireVector(bitwidth=2, name='PHT_dec')
PHT_dec <<= PHT_m[PHT_ind] - pyrtl.Const(1)

with pyrtl.conditional_assignment:
    with prediction_int == BBS_m[BBS_ind]:
        with PHT_m[PHT_ind] < pyrtl.Const(3):
            PHT_m[PHT_ind] |= PHT_inc
    with pyrtl.Const(0) < PHT_m[PHT_ind]:
        PHT_m[PHT_ind] |= PHT_dec
BBS_m[BBS_ind] <<= ~outcome_i

# Simulation
sim_trace = pyrtl.SimulationTrace()
sim = pyrtl.FastSimulation(tracer=sim_trace)

# stimuli
#f = open('serv1', 'r')
predictor = AgreePredictor(PHT_size, BBS_size)
correct_predictions = 0
total_predictions = 0
moving_correct_predictions = 0
_ = sys.stdin.readline()  # throw away first line
i = 0
predicts = []
moving_rate = []
#line = sys.readline()
for line in sys.stdin:
    # get the two fields and convert them to integers
    [pc_val, branch_outcome] = [int(x, 0) for x in line.split()]

    this_prediction = predictor.get_prediction(pc_val)
    predicts.append(this_prediction)
    total_predictions += 1
    if this_prediction == branch_outcome:
        correct_predictions += 1
        moving_correct_predictions += 1
    predictor.update(pc_val, this_prediction, branch_outcome)
    # print(this_prediction, branch_outcome)



    sim.step({pc_i: pc_val, outcome_i: branch_outcome})
    #print('i', i)
    #print(sim_trace.trace[prediction_o][i], sim_trace.trace[pred_PHT_res][i], sim_trace.trace[pred_BBS_res][i],
    #      sim_trace.trace[PHT_ind][i], sim_trace.trace[BBS_ind][i], this_prediction)

    '''
    if sim_trace.trace[prediction_o][i] != this_prediction:
        print('i', i)
        print(sim_trace.trace[prediction_o][i], sim_trace.trace[BHR_r][i], this_prediction)
        this_prediction = predictor.get_prediction(pc_val)
        predictor.update(pc_val, this_prediction, branch_outcome)
        print('wrong')
    '''
    #line = f.readline()

    i += 1
    if i % 50000 == 0:
        print(("%.1f" % (100 * float(total_predictions) / 3811906)) + '%')

    if i % 100 == 0:
        moving_rate.append(100 * moving_correct_predictions / float(100))
        moving_correct_predictions = 0


for i in range(total_predictions):
    #print(sim_trace.trace[prediction_o][i], predicts[i])

    if sim_trace.trace[prediction_o][i] != predicts[i]:

        print(sim_trace.trace[prediction_o][i], predicts[i])
        print("Prediction results don't match at line: ", i)
        exit(1)

#for i in range(100):
    #print(moving_rate[i])
print(predictor.__class__.__name__, 100 * correct_predictions / float(total_predictions))


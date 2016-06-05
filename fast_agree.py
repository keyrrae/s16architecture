from __future__ import print_function


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
PHT_size = 16384
BBS_size = 32768

# stimuli
f = open('serv1.trace', 'r')
predictor = AgreePredictor(PHT_size, BBS_size)
correct_predictions = 0
total_predictions = 0
moving_correct_predictions = 0
window_size = 200
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
    predictor.update(pc_val, this_prediction, branch_outcome)

    i += 1
    if i % 50000 == 0:
        print(("%.1f" % (100 * float(total_predictions) / 3811906)) + '%')

    if i % window_size == 0:
        moving_rate.append(100 * moving_correct_predictions / float(window_size))
        moving_correct_predictions = 0
    line = f.readline()
i = 0
for rate in moving_rate:
    if i > 20:
        break
    print("%.1f" % rate)
    i += 1

print(predictor.__class__.__name__, 100 * correct_predictions / float(total_predictions))


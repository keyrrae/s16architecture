#!/usr/bin/python
import sys


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


class GlobalPredictor:
    def __init__(self, num_history_bits=12, num_counter_bits=2):
        self.history = 0
        self.num_history_bits = num_history_bits
        self.num_counter_bits = num_counter_bits
        counterFiller = 1 << (self.num_counter_bits - 1)
        self.counters = [counterFiller for i in xrange(1 << self.num_history_bits)]
        self.counterUpperLimit = 1 << self.num_counter_bits
        self.historyBitsMask = (1 << self.num_history_bits) - 1

    def get_prediction(self, pc):
        mask = (pc >> 2) & ((1 << self.num_history_bits) - 1)
        index = self.history ^ mask
        counter = self.counters[index]
        return counter >> (self.num_counter_bits - 1)

    def update(self, pc, branch_outcome):
        mask = (pc >> 2) & (2 ** self.num_history_bits - 1)
        index = self.history ^ mask

        # Update the counter
        counter = self.counters[index]
        counter += 1 if branch_outcome == 1 else -1
        counter = 0 if counter < 0 else counter

        if counter >= self.counterUpperLimit:
            counter = self.counterUpperLimit - 1
        self.counters[index] = counter

        # Update global history
        self.history = (self.history << 1 | branch_outcome) & self.historyBitsMask


class LocalPredictor():
    def __init__(self, num_entries=1024, num_history_bits=8, num_counter_bits=2):
        self.num_entries = num_entries
        self.num_history_bits = num_history_bits
        self.num_counter_bits = num_counter_bits
        self.histories = [0 for i in xrange(num_entries)]
        counterFiller = 1 << (self.num_counter_bits - 1)
        counterNumber = 1 << self.num_history_bits
        self.counters = [counterFiller for i in xrange(counterNumber)]
        self.counterUpperLimit = 1 << self.num_counter_bits
        self.historyBitsMask = (1 << self.num_history_bits) - 1

    def get_prediction(self, pc):
        index = (pc >> 2) % self.num_entries
        history = self.histories[index]
        counter = self.counters[history]
        return counter >> (self.num_counter_bits - 1)

    def update(self, pc, branch_outcome):
        index = (pc >> 2) % self.num_entries
        histIndex = self.histories[index]
        counter = self.counters[histIndex]

        counter += 1 if branch_outcome == 1 else -1
        counter = 0 if counter < 0 else counter

        if counter >= self.counterUpperLimit:
            counter = self.counterUpperLimit - 1
        self.counters[histIndex] = counter

        histIndex = (histIndex << 1 | branch_outcome) & self.historyBitsMask
        self.histories[index] = histIndex


class TournamentPredictor():
    def __init__(self, num_entries, counter_bits):
        self.history = 0
        self.num_entries = num_entries
        self.num_counter_bits = counter_bits
        counterFiller = 1 << (self.num_counter_bits - 1)
        self.counters = [counterFiller for i in xrange(num_entries)]
        self.globalPredictor = GlobalPredictor(12, 2)
        self.localPredictor = LocalPredictor(1024, 8, 2)

        self.counterUpperLimit = 1 << self.num_counter_bits

    def get_prediction(self, pc):
        counter = self.counters[self.history]
        if counter >> (self.num_counter_bits - 1) == 1:
            return self.globalPredictor.get_prediction(pc)
        else:
            return self.localPredictor.get_prediction(pc)

    def update(self, pc, branch_outcome):
        globalPrediction = self.globalPredictor.get_prediction(pc)
        g = 1 if branch_outcome == globalPrediction else 0

        localPrediction = self.localPredictor.get_prediction(pc)
        l = 1 if branch_outcome == localPrediction else 0

        counter = self.counters[self.history]
        counter += g
        counter -= l
        counter = 0 if counter < 0 else counter

        if counter >= self.counterUpperLimit:
            counter = self.counterUpperLimit - 1
        self.counters[self.history] = counter

        self.history = (self.history << 1 | branch_outcome) % self.num_entries

        self.globalPredictor.update(pc, branch_outcome)
        self.localPredictor.update(pc, branch_outcome)


def printUsage():
    print "python branch.py bimodal"
    print "    - Single bit bimodal predictor\n"
    print "python branch.py local"
    print "    - Local predictor\n"
    print "python branch.py global"
    print "    - Global predictor\n"
    print "python branch.py tournament"
    print "    - Tournament predictor\n"


def main(which):
    if which.lower() == "tournament":
        predictor = TournamentPredictor(1024, 2)
    elif which.lower() == "global":
        predictor = GlobalPredictor(12, 2)
    elif which.lower() == "local":
        predictor = LocalPredictor(1024, 8, 2)
    elif which.lower() == "bimodal":
        predictor = singlebit_bimodal_predictor(1024)
    else:
        printUsage()
        exit(1)

    correct_predictions = 0
    total_predictions = 0
    _ = sys.stdin.readline()  # discard the first line in the input file

    hist = {}

    for line in sys.stdin:
        # get the two fields and convert them to integers
        [pc, branch_outcome] = [int(x, 0) for x in line.split()]
        this_prediction = predictor.get_prediction(pc)
        total_predictions += 1
        if this_prediction == branch_outcome:
            correct_predictions += 1
        else:
            hist[str(pc)] = 1 if str(pc) not in hist else hist[str(pc)] + 1
        predictor.update(pc, branch_outcome)
    # print out the statistics
    max_item = reduce(lambda x, y: x if x[1] > y[1] else y, hist.items())
    print "pc: " + format(int(max_item[0]), '#08x') + " misses: " + str(max_item[1])
    print predictor.__class__.__name__ + ":", 100.0 - 100 * correct_predictions / float(total_predictions)

if __name__ == "__main__":
    if len(sys.argv) == 0:
        printUsage()
        exit(1)
    main(sys.argv[1])

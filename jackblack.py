# Let's play JackBlack. We have a large deck of cards A, 2, 4, 8, 16, 32, 64
# in equal proportion (so here 1/7th). Each card is worth the number of points
# inscribed on it with A being worth 1 point. You draw cards iteratively
# until the sum of their point values is greater than or equal to N. The
# difference of the sum and N is your score. So if N = 21 and you draw a 64, 
# then your score is 64 - N = 64 - 21 = 43

import numpy as np

cardvals = [1, 2, 4, 8, 16, 32, 64]

def draw_card(N, the_sum=0):
    while the_sum < N:
        indx = np.random.randint(7)
        the_sum += cardvals[indx]

    return the_sum

trials = 1000000
n_means = 100
N = 1000#21
means = np.zeros(n_means)
stdev = np.zeros(n_means)

for ii in range(n_means):
    scores = np.zeros(trials)

    for jj in range(trials):
        scores[jj] = draw_card(N) - N

    means[ii] = np.mean(scores)
    stdev[ii] = np.std(scores)


class Recur(object):
    def __init__(self, N):
        self.N = N
        self.superset = []

    def recursion(self, prev_sum=0, this_sum=0, old_nums=[], new_nums=[]):
        for ii in range(len(cardvals)):
            prev_sum = this_sum
            old_nums = new_nums

            this_sum += cardvals[ii]
            new_nums.append(cardvals[ii])

            if this_sum < self.N:
                self.recursion(prev_sum, this_sum, old_nums, new_nums)

            else:
                self.add_to_superset(new_nums)

            new_nums.pop()
            this_sum = prev_sum

    def add_to_superset(self, the_list):
        self.superset.append(str(the_list))

    def finish_superset(self):
        self.superset = [eval(the_set) for the_set in self.superset]

    def calculate_scores(self):
        if self.superset == []:
            self.recursion()
            self.finish_superset()

        self.scores = np.zeros(len(self.superset))
        for ii in range(len(self.superset)):
            self.scores[ii] = (sum(self.superset[ii]) - self.N)

    def prob_score_lte(self, num):
        draws = len(self.scores)
        less_than_lim = sum(self.scores <= num)
        return less_than_lim / float(draws)

    def prob_draw_card(self, card):
        draws = len(self.scores)
        drew_an_8 = sum([1 for combo in self.superset if card in combo])
        return drew_an_8 / float(draws)

    def prob_score_lte_given_card(self, num, card):
        drew_a_card = sum([1 for combo in self.superset if card in combo])
        the_count = 0
        for combo in self.superset:
            if card in combo:
                if sum(combo) - self.N <= num:
                    the_count += 1

        return float(the_count) / drew_a_card

    def prob_drew_card_given_score(self, card, num):
        got_a_score = sum([1 for score in self.scores if score <= num])
        the_count = 0
        for combo in self.superset:
            if sum(combo) - self.N <= num:
                if card in combo:
                    the_count += 1
        return float(the_count) / got_a_score


recur = Recur(21)
recur.calculate_scores()
print recur.prob_score_lte_given_card(5, 8)

# recur = Recur(100)
# recur.calculate_scores()
# print recur.prob_score_lte_given_card(5, 8)

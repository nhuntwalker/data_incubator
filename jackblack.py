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
        self.superset = "["
        self.scores = []

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
        self.superset += str(the_list) + ","

    def finish_superset(self):
        self.superset += "]"
        self.superset = eval(self.superset)

    def calculate_scores(self):
        if type(self.superset) == str:
            self.recursion()
            self.finish_superset()

        for combo in self.superset:
            self.scores.append(sum(combo) - self.N)

recur = Recur(21)


less_than_5 = 0
has_an_eight = 0
has_eight_and_lt_5 = 0

for each_set in set_of_steps:
    if sum(each_set) - N <= 5:
        less_than_5 += 1
    if 8 in each_set:
        has_an_eight += 1
    if (sum(each_set) - N <= 5) & (8 in each_set):
        has_eight_and_lt_5 += 1

# def test_recursion_nosave(N, prev_sum=0, current_sum=0, card_flag=False):
#     for ii in range(len(cardvals)):
#         prev_sum = current_sum
#         current_sum += cardvals[ii]

#         if (cardvals[ii] == 1) & (card_flag == False):
#             card_flag = True
        
#         if current_sum < N:
#             test_recursion_nosave(N, prev_sum, current_sum, card_flag)
#             current_sum = prev_sum

#             if card_flag == True:
#                 card_flag = False

#         else:
#             the_count.append(1)
#             if current_sum - N <= 5:
#                 score_lt_5.append(1)

#                 if card_flag == True:
#                     score_and_8.append(1)

#             if card_flag == True:
#                 drew_an_8.append(1)
#                 # print current_sum
#                 # card_flag = False

#             current_sum = prev_sum 
         

# the_count = []
# score_lt_5 = []
# drew_an_8 = []
# score_and_8 = []

# test_recursion_nosave(2)

# print len(the_count), len(score_lt_5), len(drew_an_8), len(score_and_8)

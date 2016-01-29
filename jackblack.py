# Let's play JackBlack. We have a large deck of cards A, 2, 4, 8, 16, 32, 64
# in equal proportion (so here 1/7th). Each card is worth the number of points
# inscribed on it with A being worth 1 point. You draw cards iteratively
# until the sum of their point values is greater than or equal to N. The
# difference of the sum and N is your score. So if N = 21 and you draw a 64, 
# then your score is 64 - N = 64 - 21 = 43

# class Recur(object):
#     def __init__(self, N):
#         self.N = N
#         self.superset = []

#     def recursion(self, prev_sum=0, this_sum=0, old_nums=[], new_nums=[]):
#         for ii in range(len(cardvals)):
#             prev_sum = this_sum
#             old_nums = new_nums

#             this_sum += cardvals[ii]
#             new_nums.append(cardvals[ii])

#             if this_sum < self.N:
#                 self.recursion(prev_sum, this_sum, old_nums, new_nums)

#             else:
#                 self.add_to_superset(new_nums)

#             new_nums.pop()
#             this_sum = prev_sum

#     def add_to_superset(self, the_list):
#         self.superset.append(str(the_list))

#     def finish_superset(self):
#         self.superset = [eval(the_set) for the_set in self.superset]

#     def calculate_scores(self):
#         if self.superset == []:
#             self.recursion()
#             self.finish_superset()

#         self.scores = np.zeros(len(self.superset))
#         for ii in range(len(self.superset)):
#             self.scores[ii] = (sum(self.superset[ii]) - self.N)

#     def prob_score_lte(self, num):
#         draws = len(self.scores)
#         less_than_lim = sum(self.scores <= num)
#         return less_than_lim / float(draws)

#     def prob_draw_card(self, card):
#         draws = len(self.scores)
#         drew_an_8 = sum([1 for combo in self.superset if card in combo])
#         return drew_an_8 / float(draws)

#     def prob_score_lte_given_card(self, num, card):
#         drew_a_card = sum([1 for combo in self.superset if card in combo])
#         the_count = 0
#         for combo in self.superset:
#             if card in combo:
#                 if sum(combo) - self.N <= num:
#                     the_count += 1

#         return float(the_count) / drew_a_card

#     def prob_drew_card_given_score(self, card, num):
#         got_a_score = sum([1 for score in self.scores if score <= num])
#         the_count = 0
#         for combo in self.superset:
#             if sum(combo) - self.N <= num:
#                 if card in combo:
#                     the_count += 1
#         return float(the_count) / got_a_score


# recur = Recur(21)
# recur.calculate_scores()
# print recur.prob_score_lte_given_card(5, 8)

# recur = Recur(1000)
# recur.calculate_scores()
# print recur.prob_score_lte_given_card(5, 8)

## Because N = 1000 would exceed the maximum recursion depth, I'm going to
## approach the problem in a Monte Carlo sort of way. It won't be precisely
## correct but it should approach something resembling correctness

import numpy as np

cardvals = [1, 2, 4, 8, 16, 32, 64]

def draw_card(N):
    """
    Draw a card at random and add it to a hand. When the sum of card values in
    the hand is greater than or equal to N, stop drawing and return the hand
    and the sum.

    Inputs
    --------
    N : The desired number that the sum of a hand should greater than or equal
        to when cards stop being drawn.

    Outputs
    ________
    the_sum : The numerical sum of card values in the hand
    the_hand : The cards themselves held in the hand
    """
    the_hand = []
    the_sum = 0

    while the_sum < N:
        indx = np.random.randint(7)
        the_sum += cardvals[indx]
        the_hand.append(cardvals[indx])

    return the_sum, the_hand

trials = 10000001
N = 1000#21
hands = np.zeros(trials, dtype=list)
scores = np.zeros(trials)

for ii in range(trials):
    result = draw_card(N)
    scores[ii] = result[0] - N
    hands[ii] = result[1]

num_score_lt5 = sum([1 for score in scores if score <= 5])
num_drew_8 = sum([1 for hand in hands if 8 in hand])
num_score_lt5_if_drew_8 = 0

for ii in range(len(hands)):
    if 8 in hands[ii]:
        if scores[ii] <= 5:
            num_score_lt5_if_drew_8 += 1

prob_score_lt_5_given_drew_8 = float(num_score_lt5_if_drew_8) / num_drew_8

def draw_card_modified(N):
    """
    The same as draw_card, except the Ace can have either the value of 1 or 11

    Inputs
    --------
    N : The desired number that the sum of a hand should greater than or equal
        to when cards stop being drawn.

    Outputs
    ________
    the_sum : The numerical sum of card values in the hand
    the_hand : The cards themselves held in the hand
    """
    the_hand = []
    the_sum = 0
    while the_sum < N:
        indx = np.random.randint(7)
        card = cardvals[indx]
        if card == 1:
            if the_sum + 1 == N:
                card = 1

            else:
                card = 11

        the_hand.append(card)
        the_sum = sum(the_hand)

    return the_sum, the_hand

trials = 10000001
hands = np.zeros(trials, dtype=list)
scores = np.zeros(trials)

N = 1000#21
np.random.seed(42)
for ii in range(trials):
    result = draw_card_modified(N)
    scores[ii] = result[0] - N
    hands[ii] = result[1]

print np.round(sum(scores)/float(trials), 10), np.std(scores)


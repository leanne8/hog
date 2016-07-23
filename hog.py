"""The Game of Hog."""

from dice import four_sided, six_sided, make_test_dice
from ucb import main, trace, log_current_line, interact

GOAL_SCORE = 100 # The goal of Hog is to score 100 points.

######################
# Phase 1: Simulator #
######################

def roll_dice(num_rolls, dice=six_sided):
    """Roll DICE for NUM_ROLLS times. Return either the sum of the outcomes,
    or 1 if a 1 is rolled (Pig out). This calls DICE exactly NUM_ROLLS times.

    num_rolls:  The number of dice rolls that will be made; at least 1.
    dice:       A zero-argument function that returns an integer outcome.
    """
    # These assert statements ensure that num_rolls is a positive integer.
    assert type(num_rolls) == int, 'num_rolls must be an integer.'
    assert num_rolls > 0, 'Must roll at least once.'
    rolling = False
    sum, i = 0, 0
    k = 0 
    while i < num_rolls:
        k = dice()
        sum = sum + k
        if k == 1:
            rolling = True
        i = i + 1
    if rolling:
        return 1
    else:
        return sum


def take_turn(num_rolls, opponent_score, dice=six_sided):
    """Simulate a turn rolling NUM_ROLLS dice, which may be 0 (Free bacon).

    num_rolls:       The number of dice rolls that will be made.
    opponent_score:  The total score of the opponent.
    dice:            A function of no args that returns an integer outcome.
    """
    assert type(num_rolls) == int, 'num_rolls must be an integer.'
    assert num_rolls >= 0, 'Cannot roll a negative number of dice.'
    assert num_rolls <= 10, 'Cannot roll more than 10 dice.'
    assert opponent_score < 100, 'The game should be over.'

    if num_rolls == 0:
        return  max((opponent_score // 10), (opponent_score % 10)) +1
            
    else:
        return roll_dice(num_rolls, dice) 

def select_dice(score, opponent_score):
    """Select six-sided dice unless the sum of SCORE and OPPONENT_SCORE is a
    multiple of 7, in which case select four-sided dice (Hog wild).
    """
    if (score + opponent_score) % 7 ==0:
        return four_sided
    else:
        return six_sided

def is_prime(n):
    """Return True if a non-negative number N is prime, otherwise return
    False. 1 is not a prime number!
    """
    assert type(n) == int, 'n must be an integer.'
    assert n >= 0, 'n must be non-negative.'
    k = 2

    if n < 2:
        return False
    while k < n:
        if n % k == 0:
            return False
        k = k +1
    return True

def other(who):
    """Return the other player, for a player WHO numbered 0 or 1.

    >>> other(0)
    1
    >>> other(1)
    0
    """
    return 1 - who

def play(strategy0, strategy1, score0=0, score1=0, goal=GOAL_SCORE):
    """Simulate a game and return the final scores of both players, with
    Player 0's score first, and Player 1's score second.

    A strategy is a function that takes two total scores as arguments
    (the current player's score, and the opponent's score), and returns a
    number of dice that the current player will roll this turn.

    strategy0:  The strategy function for Player 0, who plays first
    strategy1:  The strategy function for Player 1, who plays second
    score0   :  The starting score for Player 0
    score1   :  The starting score for Player 1
    """

    who = 0

    current_score = 0
    while (score0 < goal and score1 < goal):
        

        if who == 0:
            num = strategy0(score0, score1)
            dice = select_dice(score0, score1)
            current_score = take_turn(num, score1, dice)
            score0 += current_score
            who = other(who)
        elif who == 1:
            num = strategy1(score1, score0)
            dice = select_dice(score1, score0)
            current_score = take_turn(num, score0, dice)
            score1 += current_score   
            who = other(who)
        #prime rule
        if is_prime(score0 + score1):
            if score0 < score1:
                score1 += current_score
            elif score1 < score0:
                score0 += current_score
            elif score1 == score0:
                continue
    return score0, score1
#######################
# Phase 2: Strategies #
#######################

def always_roll(n):
    """Return a strategy that always rolls N dice.

    A strategy is a function that takes two total scores as arguments
    (the current player's score, and the opponent's score), and returns a
    number of dice that the current player will roll this turn.

    >>> strategy = always_roll(5)
    >>> strategy(0, 0)
    5
    >>> strategy(99, 99)
    5
    """
    def strategy(score, opponent_score):
        return n
    return strategy

# Experiments

def make_averaged(fn, num_samples=1000):
    """Return a function that returns the average_value of FN when called.

    To implement this function, you will have to use *args syntax, a new Python
    feature introduced in this project.  See the project description.

    >>> dice = make_test_dice(3, 1, 5, 6)
    >>> averaged_dice = make_averaged(dice, 1000)
    >>> averaged_dice()
    3.75
    >>> make_averaged(roll_dice, 1000)(2, dice)
    6.0

    In this last example, two different turn scenarios are averaged.
    - In the first, the player rolls a 3 then a 1, receiving a score of 1.
    - In the other, the player rolls a 5 and 6, scoring 11.
    Thus, the average value is 6.0.
    """
    def average_value(*args):
        sum, i = 0, 1
       
        while i <= num_samples:
            sum += fn(*args)
            i += 1
        return sum / num_samples
    return average_value


def max_scoring_num_rolls(dice=six_sided):
    """Return the number of dice (1 to 10) that gives the highest average turn
    score by calling roll_dice with the provided DICE.  Assume that dice always
    return positive outcomes.

    >>> dice = make_test_dice(3)
    >>> max_scoring_num_rolls(dice)
    10
    """
    maxx = 0
    average = make_averaged(roll_dice, 1000)
    i, x = 0, 1
    while (i < 10):
        y = average(i+1, dice)
        if y > maxx:
            maxx = y
            x = i+1
        i += 1
    return x


def winner(strategy0, strategy1):
    """Return 0 if strategy0 wins against strategy1, and 1 otherwise."""
    score0, score1 = play(strategy0, strategy1)
    if score0 > score1:
        return 0
    else:
        return 1

def average_win_rate(strategy, baseline=always_roll(5)):
    """Return the average win rate (0 to 1) of STRATEGY against BASELINE."""
    win_rate_as_player_0 = 1 - make_averaged(winner)(strategy, baseline)
    win_rate_as_player_1 = make_averaged(winner)(baseline, strategy)
    return (win_rate_as_player_0 + win_rate_as_player_1) / 2 # Average results

def run_experiments():
    """Run a series of strategy experiments and report results."""
    if True: # Change to False when done finding max_scoring_num_rolls
        six_sided_max = max_scoring_num_rolls(six_sided)
        print('Max scoring num rolls for six-sided dice:', six_sided_max)
        four_sided_max = max_scoring_num_rolls(four_sided)
        print('Max scoring num rolls for four-sided dice:', four_sided_max)

    if False: # Change to True to test always_roll(8)
        print('always_roll(8) win rate:', average_win_rate(always_roll(8)))

    if False: # Change to True to test bacon_strategy
        print('bacon_strategy win rate:', average_win_rate(bacon_strategy))

    if False: # Change to True to test prime_strategy
        print('prime_strategy win rate:', average_win_rate(prime_strategy))

    if False: # Change to True to test final_strategy
        print('final_strategy win rate:', average_win_rate(final_strategy))

    "*** You may add additional experiments as you wish ***"

# Strategies

def bacon_strategy(score, opponent_score, margin=8, num_rolls=5):
    """This strategy rolls 0 dice if that gives at least MARGIN points,
    and rolls NUM_ROLLS otherwise.
    """
    if max((opponent_score // 10), (opponent_score % 10)) +1 >= margin:
        return 0
    else:
        return num_rolls


def prime_strategy(score, opponent_score, margin=8, num_rolls=5):
    """This strategy rolls 0 dice when it results in a beneficial boost and 
    rolls NUM_ROLLS if rolling 0 dice gives the opponent a boost. It also 
    rolls 0 dice if that gives at least MARGIN points and rolls NUM_ROLLS
    otherwise.
    """
    margin_test = max((opponent_score // 10), (opponent_score % 10)) +1
    test_score = score + opponent_score + margin_test
    if not is_prime(score + opponent_score):
        if is_prime(test_score) and (test_score - opponent_score > opponent_score):
            return 0
        else:
            return num_rolls
    else:
        if margin_test >= margin:
            return 0
        else:
            return num_rolls


def final_strategy(score, opponent_score):
    margin = 10
    margin_test = max((opponent_score // 10), (opponent_score % 10)) +1
    test_score = score + opponent_score + margin_test

    if(opponent_score < 10):
        marg = opponent_score - 1
    else:
        marg = abs((opponent_score // 10) - (opponent_score % 10)) - 1


    if max((opponent_score//10), (opponent_score %10)) + 1 >= margin:
        return 0
    if score > opponent_score and (100 - score) < 15 :
        return 3
    elif score > opponent_score and (100 - score) > 85:        
        return 3
    elif score > opponent_score and (100 - score) > 90:        
        return 2
    elif score < opponent_score and (100 - opponent_score) < 30:
        return 7
    elif score < opponent_score and (100 - opponent_score) > marg:
        return 6
    elif not is_prime(score + opponent_score):
        if is_prime(test_score) and (test_score - opponent_score > opponent_score):
            return 0
        else:
            return 4
    elif is_prime(score + opponent_score):
        if margin_test >= margin:
            return 0
        else:
            return 4
    else:
        return 5


##########################
# Command Line Interface #
##########################

# Note: Functions in this section do not need to be changed.  They use features
#       of Python not yet covered in the course.


@main
def run(*args):
    """Read in the command-line argument and calls corresponding functions.

    This function uses Python syntax/techniques not yet covered in this course.
    """
    import argparse
    parser = argparse.ArgumentParser(description="Play Hog")
    parser.add_argument('--run_experiments', '-r', action='store_true',
                        help='Runs strategy experiments')
    args = parser.parse_args()

    if args.run_experiments:
        run_experiments()

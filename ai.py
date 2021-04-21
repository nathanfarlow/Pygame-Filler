import math
import time

from numpy import random

from filler import Filler

def heuristic(filler, is_max):

    winner = filler.get_winner()

    if winner in {0, 1}:
        neg = (is_max and winner != 0) or (not is_max and winner == 1)
        return math.inf * (-1 if neg else 1)

    return filler.get_score(0) - filler.get_score(1)

def minimax(filler, depth, alpha=-math.inf, beta=math.inf):

    is_max = not filler.turn

    possible_moves = set(range(filler.num_colors)) - {filler.get_color(0), filler.get_color(1)}

    best = None
    for move in possible_moves:
        new_filler = filler.copy()
        new_filler.play(move)

        if depth > 1:
            value, _ = minimax(new_filler, depth - 1, alpha, beta)
        else:
            value = heuristic(new_filler, is_max)

        if (
            best is None
            or is_max and value > best[0]
            or not is_max and value < best[0]
        ):
            best = (value, move)

        if is_max:
            alpha = max(alpha, value)
        else:
            beta = min(beta, value)

        if alpha >= beta:
            break

    return best

def get_minimax_move(filler, callback, exit_event):

    print(f'Starting alphabeta search for player {int(filler.turn)}')
    start = time.monotonic()
    value, move = minimax(filler, 12)
    end = time.monotonic()
    print(f'Found move {move} with value {value} in {end - start} seconds')

    callback(move)

def get_random_move(filler, callback, exit_event):
    possible_moves = set(range(filler.num_colors)) - {filler.get_color(0), filler.get_color(1)}
    callback(random.choice(list(possible_moves)))

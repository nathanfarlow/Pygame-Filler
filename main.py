import time
import argparse

from filler import Filler, FillerUI
from ai import get_minimax_move, get_random_move


if __name__ == '__main__':

    player_choices = {
        'human': None,
        'minimax': get_minimax_move,
        'random': get_random_move
    }

    parser = argparse.ArgumentParser()
    parser.add_argument('--player1', dest='player1', default='human', choices=player_choices.keys(), help='The input source for player1 moves')
    parser.add_argument('--player2', dest='player2', default='human', choices=player_choices.keys(), help='The input source for player2 moves')
    parser.add_argument('--width', dest='width', type=int, default=8, help='The width of the game board')
    parser.add_argument('--height', dest='height', type=int, default=7, help='The height of the game board')
    args = parser.parse_args()

    filler = Filler(args.width, args.height)
    g = FillerUI(filler, player1_delegate=player_choices[args.player1], player2_delegate=player_choices[args.player2])

    while not g.is_done():
        g.draw()
        g.update()
        time.sleep(1/30)

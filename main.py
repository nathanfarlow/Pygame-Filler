import time
from filler import Filler, FillerUI
from ai import get_minimax_move, get_random_move

if __name__ == '__main__':
    filler = Filler(8, 7, 6)
    g = FillerUI(filler, player2_delegate=get_minimax_move)

    while not g.is_done():
        g.draw()
        g.update()
        time.sleep(1/30)
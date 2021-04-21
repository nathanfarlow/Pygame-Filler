import time
from filler import Filler, FillerUI

if __name__ == '__main__':
    filler = Filler(8, 7, 6)
    g = FillerUI(filler)

    while not g.is_done():
        g.draw()
        g.update()
        time.sleep(1/30)
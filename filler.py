import time
import math
import copy
import threading

import numpy as np

import pygame
from pygame.locals import *


class Filler:

    def __init__(self, w, h):
        self.w = w
        self.h = h
        self.num_colors = 6
        self.grid = np.random.randint(0, self.num_colors, (h, w))
        self.turn = False
        self.start_pos = ((self.w - 1, 0), (0, self.h - 1))
        self.score = [0, 0]

        # Initialize inital counts
        self.play(self.get_color(self.turn))
        self.play(self.get_color(self.turn))

    def __play(self, start_color, new_color, x, y, visited):

        # Simple DFS to change color and recompute score

        visited.add((x, y))

        if self.grid[y, x] != start_color:
            # We met a boundary node we do not own yet

            # If it's not the new color, we do nothing
            if self.grid[y, x] != new_color:
                return
            
            # If it is the new color, we continue DFS'ing, but
            # we don't update colors. This is just to count up
            # these nodes.
            visited = set(visited)
            start_color = new_color
        
        self.grid[y, x] = new_color
        self.score[self.turn] += 1

        adjacent = [(x - 1, y), (x + 1, y),
                    (x, y - 1), (x, y + 1)]
        
        for x, y in adjacent:
            if (x >= 0 and x < self.w
                    and y >= 0 and y < self.h
                    and (x, y) not in visited):
                self.__play(start_color, new_color, x, y, visited)

    def play(self, color):
        self.score[self.turn] = 0
        start = self.start_pos[self.turn]
        self.__play(self.get_color(self.turn), color, *start, set())
        self.turn = not self.turn

    def get_score(self, player):
        return self.score[player]

    def get_color(self, player):
        start = self.start_pos[player]
        return self.grid[start[1], start[0]]

    def get_winner(self):
        # -1 if no winner, 0 if player 1 wins, 1 if player 2 wins, 2 if there is a tie

        to_win = math.ceil(self.w * self.h / 2)

        if max(self.score) < to_win:
            return -1

        return 2 if self.score[0] == self.score[1] else np.argmax(self.score)

    def copy(self):
        return copy.deepcopy(self)


class UIComponent():

    def __init__(self, x, y, w, h):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.enabled = True
    
    def update(self, events):
        pass

    def draw(self, screen):
        pass

    def enable(self):
        self.enabled = True

    def disable(self):
        self.enabled = False

    def is_in_view(self, x, y):
        return (
            x >= self.x and x < self.x + self.w
            and y >= self.y and y < self.y + self.h
        )

    def normalize_in_view(self, x, y):
        return ((x - self.x) / self.w, (y - self.y) / self.h)


class ColorPicker(UIComponent):

    def __init__(self, filler, colors, x, y, w, h):
        super().__init__(x, y, w, h)
        self.filler = filler
        self.colors = colors
        self.chosen = None
    
    def update(self, events):
        disabled = {self.filler.get_color(0), self.filler.get_color(1)}

        for event in events:
            if event.type == MOUSEBUTTONDOWN:
                x, y = pygame.mouse.get_pos()

                # Play selected color for human player
                if self.is_in_view(x, y):
                    u, _ = self.normalize_in_view(x, y)
                    chosen = math.floor(u * self.filler.num_colors)
                    if chosen not in disabled:
                        self.chosen = chosen

    def draw(self, screen):
        num_colors = self.filler.num_colors
        bw, bh = self.w // num_colors, self.h
        disabled = {self.filler.get_color(0), self.filler.get_color(1)}

        for i in range(num_colors):
            color = self.colors[i]
            if i in disabled:
                w, h = (bw / 2, bh / 2)
                pygame.draw.rect(screen, color, (self.x + i * bw + w / 2, self.y + h / 2, w, h))
            else:
                pygame.draw.rect(screen, color, (self.x + i * bw, self.y, bw, bh))

    def get_move(self, filler, callback, exit_event):

        # Async function that invokes callback() when
        # user decides move. asyncio would probably be better,
        # but this is convenient for minimax on another thread.

        while self.chosen is None:
            if exit_event.is_set():
                return
            
            time.sleep(1e-4)
        
        chosen = self.chosen
        self.chosen = None
        callback(chosen)


class GameBoard(UIComponent):

    keys = (K_r, K_g, K_y, K_b, K_p, K_l)

    def __init__(self, filler, colors, x, y, w, h):
        super().__init__(x, y, w, h)
        self.filler = filler
        self.colors = colors

        self.selected = np.zeros(2)

    def update(self, events):
        
        if not self.enabled:
            return

        for event in events:
            if event.type == MOUSEBUTTONDOWN:
                x, y = pygame.mouse.get_pos()

                # Move selection location
                if self.is_in_view(x, y):
                    u, v = self.normalize_in_view(x, y)
                    x_index = math.floor(u * self.filler.w)
                    y_index = math.floor(v * self.filler.h)
                    self.selected = np.array((x_index, y_index))

            elif event.type == KEYDOWN:

                # Move selection location
                self.selected += {
                    K_UP: (0, -1),
                    K_DOWN: (0, 1),
                    K_RIGHT: (1, 0),
                    K_LEFT: (-1, 0)
                }.get(event.key, (0, 0))

                # Update board color at selected location
                if event.key in self.keys:
                    self.filler.grid[self.selected[1], self.selected[0]] = self.keys.index(event.key)
                    self.selected[0] += 1

                    if self.selected[0] >= self.filler.w:
                        self.selected[1] += 1

                self.selected %= (self.filler.w, self.filler.h)

    def draw(self, screen):
        num_colors = self.filler.num_colors
        bw, bh = self.w // self.filler.w, self.h // self.filler.h

        for y in range(self.filler.h):
            for x in range(self.filler.w):
                color = self.colors[self.filler.grid[y, x]]
                pygame.draw.rect(screen, color, (x * bw, y * bh, bw, bh))

        x, y = self.selected
        pygame.draw.rect(screen, (0, 0, 0), (x * bw, y * bh, bw, bh), 4)


class FillerUI():

    SCREEN_WIDTH, SCREEN_HEIGHT = 500, 600

    colors = [(228, 74, 90), (172, 212, 100), (250, 226, 82),
                (88, 166, 239), (102, 77, 157), (65, 65, 65)]

    def __init__(self, filler, player1_delegate=None, player2_delegate=None):
        self.filler = filler

        sw, sh = self.SCREEN_WIDTH, self.SCREEN_HEIGHT
        self.board = GameBoard(filler, self.colors, 0, 0, sw, sh - 100)
        self.picker = ColorPicker(filler, self.colors, sw // 8, sh - 100 + 20, sw - sw // 8 * 2, 100 - 20 * 2)

        # Functions which obtain moves for a player
        self.delegates = [
            player1_delegate or self.picker.get_move,
            player2_delegate or self.picker.get_move
        ]

        self.done = False

        pygame.init()
        pygame.display.set_caption('Filler')
        pygame.font.init()
        
        self.font = pygame.font.SysFont('Comic Sans MS', 30)
        self.screen = pygame.display.set_mode((sw, sh))

        self.exit_event = threading.Event()
        self.get_next_move()

    def get_next_move(self):

        def callback(color):
            self.filler.play(color)
            self.get_next_move()
        
        delegate = self.delegates[self.filler.turn]
        threading.Thread(target=delegate, args=(self.filler, callback, self.exit_event)).start()

    def update(self):

        events = list(pygame.event.get())

        self.board.update(events)
        self.picker.update(events)
        
        for event in events:
            if event.type == QUIT:
                pygame.quit()
                self.exit_event.set()

    def draw(self):
        self.screen.fill((230, 230, 230))

        self.board.draw(self.screen)
        self.picker.draw(self.screen)

        text_color = (0, 0, 0)

        status = f'Waiting for player {int(self.filler.turn) + 1}...'
        text = self.font.render(status, True, text_color)
        x, y, w, h = text.get_rect()
        self.screen.blit(text, (self.SCREEN_WIDTH / 2 - w / 2, 10))

        text = self.font.render(f'Player 1 score: {self.filler.get_score(0)}', True, text_color)
        x, y, w, h = text.get_rect()
        self.screen.blit(text, (2, self.SCREEN_HEIGHT - h - 2))

        text = self.font.render(f'Player 2 score: {self.filler.get_score(1)}', True, text_color)
        x, y, w, h = text.get_rect()
        self.screen.blit(text, (self.SCREEN_WIDTH - w - 2, self.SCREEN_HEIGHT - h - 2))

        pygame.display.flip()
        pygame.display.update()
        
    def is_done(self):
        return self.exit_event.is_set()

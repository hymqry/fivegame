BOARD_SIZE = 15
EMPTY = 0
BLACK = 1
WHITE = 2


class Board:
    def __init__(self):
        self.grid = [EMPTY] * (BOARD_SIZE * BOARD_SIZE)

    def _index(self, row, col):
        return row * BOARD_SIZE + col

    def is_valid(self, row, col):
        return 0 <= row < BOARD_SIZE and 0 <= col < BOARD_SIZE and self.grid[self._index(row, col)] == EMPTY

    def in_bounds(self, row, col):
        return 0 <= row < BOARD_SIZE and 0 <= col < BOARD_SIZE

    def place(self, row, col, player):
        if not self.is_valid(row, col):
            return False
        self.grid[self._index(row, col)] = player
        return True

    def get(self, row, col):
        if not self.in_bounds(row, col):
            return -1
        return self.grid[self._index(row, col)]

    def is_full(self):
        return all(cell != EMPTY for cell in self.grid)

    def create_clone(self):
        b = Board()
        b.grid = self.grid[:]
        return b

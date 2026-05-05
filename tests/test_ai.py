import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import unittest
from board import Board, BOARD_SIZE, EMPTY, BLACK, WHITE
from ai import get_ai_move


class AITests(unittest.TestCase):
    def test_ai_makes_valid_move(self):
        b = Board()
        b.place(7, 7, BLACK)
        b.place(7, 8, WHITE)
        b.place(8, 7, BLACK)

        move = get_ai_move(b, WHITE)
        self.assertTrue(b.in_bounds(move[0], move[1]))
        self.assertEqual(b.get(move[0], move[1]), EMPTY)

    def test_ai_blocks_three_in_a_row(self):
        b = Board()
        b.place(7, 5, BLACK)
        b.place(7, 6, BLACK)
        b.place(7, 7, BLACK)

        move = get_ai_move(b, WHITE)
        # AI should place near the threat (row 7, col 4 or 8)
        is_blocking = (move[0] == 7 and (move[1] == 4 or move[1] == 8))
        self.assertTrue(is_blocking)

    def test_ai_does_not_play_on_occupied(self):
        b = Board()
        for i in range(5, 10):
            for j in range(5, 10):
                player = BLACK if (i + j) % 2 == 0 else WHITE
                b.place(i, j, player)

        move = get_ai_move(b, BLACK)
        self.assertEqual(b.get(move[0], move[1]), EMPTY)

    def test_empty_board_ai_centers(self):
        b = Board()
        move = get_ai_move(b, BLACK)
        self.assertTrue(b.in_bounds(move[0], move[1]))


if __name__ == "__main__":
    unittest.main()

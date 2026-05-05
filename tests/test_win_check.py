import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import unittest
from board import Board, BLACK, WHITE
from win_check import check_win


class WinCheckTests(unittest.TestCase):
    def test_horizontal_win(self):
        b = Board()
        b.place(7, 3, BLACK)
        b.place(7, 4, BLACK)
        b.place(7, 5, BLACK)
        b.place(7, 6, BLACK)
        b.place(7, 7, BLACK)
        self.assertTrue(check_win(b, 7, 7, BLACK))

    def test_vertical_win(self):
        b = Board()
        for i in range(3, 8):
            b.place(i, 5, WHITE)
        self.assertTrue(check_win(b, 7, 5, WHITE))

    def test_diagonal_down_right_win(self):
        b = Board()
        for i in range(5):
            b.place(i, i, BLACK)
        self.assertTrue(check_win(b, 4, 4, BLACK))

    def test_diagonal_up_right_win(self):
        b = Board()
        for i in range(5):
            b.place(4 - i, i, WHITE)
        self.assertTrue(check_win(b, 4, 0, WHITE))
        self.assertTrue(check_win(b, 0, 4, WHITE))

    def test_no_win_less_than_five(self):
        b = Board()
        b.place(7, 3, BLACK)
        b.place(7, 4, BLACK)
        b.place(7, 5, BLACK)
        b.place(7, 6, BLACK)
        self.assertFalse(check_win(b, 7, 6, BLACK))

    def test_no_win_on_empty_board(self):
        b = Board()
        b.place(7, 7, BLACK)
        self.assertFalse(check_win(b, 7, 7, BLACK))

    def test_win_at_boundary(self):
        b = Board()
        b.place(0, 0, BLACK)
        b.place(0, 1, BLACK)
        b.place(0, 2, BLACK)
        b.place(0, 3, BLACK)
        b.place(0, 4, BLACK)
        self.assertTrue(check_win(b, 0, 4, BLACK))

    def test_opponent_not_win(self):
        b = Board()
        for i in range(5):
            b.place(i, 0, BLACK)
        b.place(7, 7, WHITE)
        self.assertFalse(check_win(b, 7, 7, WHITE))


if __name__ == "__main__":
    unittest.main()

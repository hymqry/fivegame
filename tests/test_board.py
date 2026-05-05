import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import unittest
from board import Board, BOARD_SIZE, EMPTY, BLACK, WHITE


class BoardTests(unittest.TestCase):
    def test_board_init(self):
        b = Board()
        for i in range(BOARD_SIZE):
            for j in range(BOARD_SIZE):
                self.assertEqual(b.get(i, j), EMPTY)
        self.assertFalse(b.is_full())

    def test_place_valid(self):
        b = Board()
        self.assertTrue(b.place(7, 7, BLACK))
        self.assertEqual(b.get(7, 7), BLACK)

    def test_place_overwrite(self):
        b = Board()
        b.place(7, 7, BLACK)
        self.assertFalse(b.place(7, 7, WHITE))
        self.assertEqual(b.get(7, 7), BLACK)

    def test_place_out_of_bounds(self):
        b = Board()
        self.assertFalse(b.place(-1, 0, BLACK))
        self.assertFalse(b.place(15, 15, BLACK))
        self.assertFalse(b.place(0, 15, BLACK))

    def test_is_full(self):
        b = Board()
        for i in range(BOARD_SIZE):
            for j in range(BOARD_SIZE):
                player = BLACK if (i + j) % 2 == 0 else WHITE
                b.place(i, j, player)
        self.assertTrue(b.is_full())

    def test_clone(self):
        b = Board()
        b.place(3, 5, BLACK)
        b.place(7, 2, WHITE)
        c = b.create_clone()
        self.assertEqual(c.get(3, 5), BLACK)
        self.assertEqual(c.get(7, 2), WHITE)
        c.place(3, 5, WHITE)
        self.assertEqual(b.get(3, 5), BLACK)

    def test_in_bounds(self):
        b = Board()
        self.assertTrue(b.in_bounds(0, 0))
        self.assertTrue(b.in_bounds(14, 14))
        self.assertTrue(b.in_bounds(7, 7))
        self.assertFalse(b.in_bounds(-1, 0))
        self.assertFalse(b.in_bounds(15, 0))


if __name__ == "__main__":
    unittest.main()

from board import Board, BOARD_SIZE


def check_direction(board, row, col, player, dx, dy):
    count = 1
    for i in range(1, 5):
        r, c = row + dx * i, col + dy * i
        if board.in_bounds(r, c) and board.get(r, c) == player:
            count += 1
        else:
            break
    for i in range(1, 5):
        r, c = row - dx * i, col - dy * i
        if board.in_bounds(r, c) and board.get(r, c) == player:
            count += 1
        else:
            break
    return count


def check_win(board, row, col, player):
    if check_direction(board, row, col, player, 1, 0) >= 5:
        return True
    if check_direction(board, row, col, player, 0, 1) >= 5:
        return True
    if check_direction(board, row, col, player, 1, 1) >= 5:
        return True
    if check_direction(board, row, col, player, 1, -1) >= 5:
        return True
    return False

from board import Board, BOARD_SIZE, EMPTY, BLACK, WHITE
from win_check import check_win

SCORE_FIVE = 100000
SCORE_OPEN_FOUR = 10000
SCORE_HALF_FOUR = 5000
SCORE_OPEN_THREE = 1000
SCORE_HALF_THREE = 500
SCORE_OPEN_TWO = 100
SCORE_HALF_TWO = 50
SCORE_WIN = 1000000
CANDIDATE_LIMIT = 15
SEARCH_DEPTH = 4


def score_line(count, open_ends):
    if count >= 5:
        return SCORE_FIVE
    if count == 4 and open_ends >= 2:
        return SCORE_OPEN_FOUR
    if count == 4 and open_ends >= 1:
        return SCORE_HALF_FOUR
    if count == 3 and open_ends >= 2:
        return SCORE_OPEN_THREE
    if count == 3 and open_ends >= 1:
        return SCORE_HALF_THREE
    if count == 2 and open_ends >= 2:
        return SCORE_OPEN_TWO
    if count == 2 and open_ends >= 1:
        return SCORE_HALF_TWO
    return 0


def count_stones_on_board(board):
    cnt = 0
    for i in range(BOARD_SIZE):
        for j in range(BOARD_SIZE):
            if board.get(i, j) != EMPTY:
                cnt += 1
    return cnt


def find_first_stone(board):
    for i in range(BOARD_SIZE):
        for j in range(BOARD_SIZE):
            if board.get(i, j) != EMPTY:
                return (i, j)
    return (7, 7)


def is_near_stone(board, row, col, dist):
    for dr in range(-dist, dist + 1):
        for dc in range(-dist, dist + 1):
            if dr == 0 and dc == 0:
                continue
            r, c = row + dr, col + dc
            if board.in_bounds(r, c) and board.get(r, c) != EMPTY:
                return True
    return False


def get_candidates(board):
    candidates = []
    for i in range(BOARD_SIZE):
        for j in range(BOARD_SIZE):
            if board.get(i, j) != EMPTY:
                continue
            if is_near_stone(board, i, j, 2):
                candidates.append((i, j))
    return candidates


def calc_proximity_bonus(board, row, col, opponent, player):
    bonus = 0
    for dr in range(-2, 3):
        for dc in range(-2, 3):
            if dr == 0 and dc == 0:
                continue
            r, c = row + dr, col + dc
            if not board.in_bounds(r, c):
                continue
            v = board.get(r, c)
            if v == opponent:
                bonus += 15
            elif v == player:
                bonus += 8
    return bonus


def evaluate_position(board, row, col, player):
    opponent = WHITE if player == BLACK else BLACK
    score = 0
    dirs = [1, 0, 0, 1, 1, 1, 1, -1]

    for d in range(4):
        dx = dirs[d * 2]
        dy = dirs[d * 2 + 1]

        # Player count in this direction
        count = 1
        open_ends = 0

        blocked = False
        for i in range(1, 5):
            r, c = row + dx * i, col + dy * i
            if not board.in_bounds(r, c):
                blocked = True
                break
            v = board.get(r, c)
            if v == player:
                count += 1
            elif v == EMPTY:
                open_ends += 1
                break
            else:
                blocked = True
                break
        if not blocked:
            open_ends += 1

        blocked = False
        for i in range(1, 5):
            r, c = row - dx * i, col - dy * i
            if not board.in_bounds(r, c):
                blocked = True
                break
            v = board.get(r, c)
            if v == player:
                count += 1
            elif v == EMPTY:
                open_ends += 1
                break
            else:
                blocked = True
                break
        if not blocked:
            open_ends += 1

        score += score_line(count, open_ends)

        # Opponent threat scoring
        opp_count = 1
        opp_open_ends = 0

        blocked = False
        for i in range(1, 5):
            r, c = row + dx * i, col + dy * i
            if not board.in_bounds(r, c):
                blocked = True
                break
            v = board.get(r, c)
            if v == opponent:
                opp_count += 1
            elif v == EMPTY:
                opp_open_ends += 1
                break
            else:
                blocked = True
                break
        if not blocked:
            opp_open_ends += 1

        blocked = False
        for i in range(1, 5):
            r, c = row - dx * i, col - dy * i
            if not board.in_bounds(r, c):
                blocked = True
                break
            v = board.get(r, c)
            if v == opponent:
                opp_count += 1
            elif v == EMPTY:
                opp_open_ends += 1
                break
            else:
                blocked = True
                break
        if not blocked:
            opp_open_ends += 1

        if opp_count >= 5:
            score += SCORE_FIVE - 10000
        elif opp_count == 4 and opp_open_ends >= 2:
            score += 8000
        elif opp_count == 4 and opp_open_ends >= 1:
            score += 4000
        elif opp_count == 3 and opp_open_ends >= 2:
            score += 800

    score += calc_proximity_bonus(board, row, col, opponent, player)
    return score


def score_board(board, ai_player):
    """Full board evaluation using forward-direction scanning to avoid double-count."""
    score = 0
    dirs = [1, 0, 0, 1, 1, 1, 1, -1]

    for i in range(BOARD_SIZE):
        for j in range(BOARD_SIZE):
            cell = board.get(i, j)
            if cell == EMPTY:
                continue

            for d in range(4):
                dx = dirs[d * 2]
                dy = dirs[d * 2 + 1]

                # Skip if previous cell in this direction is the same color
                prev_r, prev_c = i - dx, j - dy
                if board.in_bounds(prev_r, prev_c) and board.get(prev_r, prev_c) == cell:
                    continue

                # Count consecutive stones in forward direction
                count = 0
                r, c = i, j
                while board.in_bounds(r, c) and board.get(r, c) == cell:
                    count += 1
                    r += dx
                    c += dy

                # Count open ends
                open_ends = 0
                end1_r, end1_c = i - dx, j - dy
                if board.in_bounds(end1_r, end1_c) and board.get(end1_r, end1_c) == EMPTY:
                    open_ends += 1
                if board.in_bounds(r, c) and board.get(r, c) == EMPTY:
                    open_ends += 1

                ls = score_line(count, open_ends)
                if cell == ai_player:
                    score += ls
                else:
                    score -= ls + ls // 10  # Opponent penalty slightly higher

    return score


def sort_candidates(board, candidates, player):
    """Sort candidates by score descending."""
    scored = []
    for mv in candidates:
        s = evaluate_position(board, mv[0], mv[1], player)
        scored.append((mv[0], mv[1], s))
    scored.sort(key=lambda x: -x[2])
    return [(r, c) for r, c, _ in scored]


def alpha_beta(board, depth, alpha, beta, is_maximizing, ai_player):
    a, b = alpha, beta
    candidate_moves = get_candidates(board)

    if not candidate_moves:
        return 0

    limit = min(len(candidate_moves), CANDIDATE_LIMIT)
    if is_maximizing:
        sorted_moves = sort_candidates(board, candidate_moves, ai_player)
    else:
        opponent = WHITE if ai_player == BLACK else BLACK
        sorted_moves = sort_candidates(board, candidate_moves, opponent)

    if depth <= 0:
        return score_board(board, ai_player)

    if is_maximizing:
        value = -SCORE_WIN * 10
        for idx in range(limit):
            mv = sorted_moves[idx]
            child = board.create_clone()
            child.place(mv[0], mv[1], ai_player)

            if check_win(child, mv[0], mv[1], ai_player):
                return SCORE_WIN + depth

            child_val = alpha_beta(child, depth - 1, a, b, False, ai_player)
            if child_val > value:
                value = child_val
            if value > a:
                a = value
            if a >= b:
                break
        return value
    else:
        value = SCORE_WIN * 10
        opponent = WHITE if ai_player == BLACK else BLACK
        for idx in range(limit):
            mv = sorted_moves[idx]
            child = board.create_clone()
            child.place(mv[0], mv[1], opponent)

            if check_win(child, mv[0], mv[1], opponent):
                return -SCORE_WIN - depth

            child_val = alpha_beta(child, depth - 1, a, b, True, ai_player)
            if child_val < value:
                value = child_val
            if value < b:
                b = value
            if a >= b:
                break
        return value


def get_ai_move(board, player):
    stones = count_stones_on_board(board)

    # Early game: first move, play near opponent's stone
    if stones <= 1:
        target_r, target_c = find_first_stone(board)
        for dr in range(-1, 2):
            for dc in range(-1, 2):
                if dr == 0 and dc == 0:
                    continue
                r, c = target_r + dr, target_c + dc
                if board.is_valid(r, c):
                    return (r, c)

    candidates = get_candidates(board)
    if not candidates:
        return (7, 7)

    sorted_moves = sort_candidates(board, candidates, player)
    limit = min(len(sorted_moves), CANDIDATE_LIMIT)

    best_score = -SCORE_WIN * 10
    best_move = sorted_moves[0]

    for idx in range(limit):
        mv = sorted_moves[idx]
        child = board.create_clone()
        child.place(mv[0], mv[1], player)

        # Check immediate win
        if check_win(child, mv[0], mv[1], player):
            return mv

        score = alpha_beta(child, SEARCH_DEPTH - 1, -SCORE_WIN * 10, SCORE_WIN * 10, False, player)
        if score > best_score:
            best_score = score
            best_move = mv

    return best_move

"""
Tic Tac Toe Player
"""

import math
import copy
import random
from pandas import *
from collections import Counter

X = "X"
O = "O"
EMPTY = None


# Define wins for tic-tac-toe
wins = [
    [(2, 0), (2, 1), (2, 2)],
    [(1, 0), (1, 1), (1, 2)],
    [(0, 0), (0, 1), (0, 2)],
    [(0, 0), (1, 0), (2, 0)],
    [(0, 1), (1, 1), (2, 1)],
    [(0, 2), (1, 2), (2, 2)],
    [(0, 0), (1, 1), (2, 2)],
    [(0, 2), (1, 1), (2, 0)]
]


def initial_state():
    """
    Returns starting state of the board.
    """
    return [[EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY]]


def player(board):
    """
    Returns player who has the next turn on a board.
    """
    x_count, o_count = 0, 0
    if board == initial_state():
        return X
    if terminal(board):
        return None
    else:
        for row_index, row in enumerate(board):
            for elem_index, index in enumerate(row):
                if index == X:
                    x_count += 1
                if index == O:
                    o_count += 1
    return O if x_count > o_count else X


def actions(board):
    """
    Returns set of all possible actions (i, j) available on the board.
    """
    actions = set()
    for row_index, row in enumerate(board):
        for elem_index, index in enumerate(row):
            if index == EMPTY:
                actions.add((row_index, elem_index))
    return actions


def result(board, action):
    """
    Returns the board that results from making move (i, j) on the board.
    """
    i, j = action
    next_player = player(board)
    copied_board = copy.deepcopy(board)

    if copied_board[i][j] != EMPTY:
        raise Exception("This spot is already filled!")
    copied_board[i][j] = next_player
    return copied_board


def winner(board):
    """
    Returns the winner of the game, if there is one.
    """
    winner = None
    possible_wins = generate_possible_wins(board)
    for pw in possible_wins:
        if all(letter == X for letter in pw):
            winner = X
        if all(letter == O for letter in pw):
            winner = O
    return winner


def terminal(board):
    """
    Returns True if game is over, False otherwise.
    """
    if winner(board) in (X, O):
        return True
    if all(EMPTY not in row for row in board):
        return True
    return False
    

def utility(board):
    """
    Returns 1 if X has won the game, -1 if O has won, 0 otherwise.
    """
    return 1 if winner(board) == X else -1 if winner(board) == O else 0


def minimax(board):
    """
    Returns the optimal action for the current player on the board.
    """
    act = []

    def minimax_helper(board, depth, maximizing_player):
        if depth == 0 or terminal(board):
            return utility(board)
        
        if maximizing_player:
            v = -math.inf
            for action in actions(board):
                current_v = minimax_helper(result(board, action), depth - 1, False)
                if current_v > v:
                    v = current_v
                    act.append(action)
            return v
        else:
            v = math.inf
            for action in actions(board):
                current_v = minimax_helper(result(board, action), depth - 1, True)
                if current_v < v:
                    v = current_v
                    act.append(action)
            return v
    
    if player(board) == "X":
        if board == initial_state():
            return (random.randrange(0,3), random.randrange(0,3))
        start = minimax_helper(board, 9, True)
    else:
        start = minimax_helper(board, 9, False)
    
    act_counter = Counter(act)
    return act_counter.most_common(1)[0][0]


def generate_possible_wins(board):
    possible_wins = []
    row = []
    copied_board = copy.deepcopy(board)
    for win in wins:
        for index in win:
            row.append(copied_board[index[0]][index[1]])
        possible_wins.append(row)
        row = []
    return possible_wins
#!/usr/bin/env python3
"""
Avalam agent.
Copyright (C) 2022, <<<<<<<<<<< YOUR NAMES HERE >>>>>>>>>>>
Polytechnique Montréal

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; version 2 of the License.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, see <http://www.gnu.org/licenses/>.

"""
from avalam import *

#logging
import os
import logging
logger = logging.getLogger("player")
logger.setLevel(logging.INFO)
file = os.path.join(os.path.dirname(os.path.realpath(__file__)), "player.log")
handler = logging.FileHandler(filename=file, encoding="utf-8", mode="w")
handler.setFormatter(logging.Formatter('%(asctime)s:%(message)s'))
logger.addHandler(handler)


def heuristique(board: Board):
    return board.get_score()

def minimax(depth, max_player: bool, board: Board):
    if depth == 0:
        return heuristique(board), None
    if max_player:
        maxEval = float('-inf')
        best_action = None
        for action in board.get_actions():
            new_board = board.clone()
            new_board.play_action(action)
            evaluation = minimax(depth-1, False, new_board)[0]
            maxEval = max(maxEval, evaluation)
            if maxEval == evaluation:
                best_action = action
        return maxEval, best_action
    else:
        minEval = float('inf')
        best_action = None
        for action in board.get_actions():
            new_board = board.clone()
            new_board.play_action(action)
            evaluation = minimax(depth-1, True, new_board)[0]
            minEval = min(minEval, evaluation)
            if minEval == evaluation:
                best_action = action
        return minEval, best_action

class MyAgent(Agent):

    """My Avalam agent."""

    def play(self, percepts: dict, player: int, step, time_left: float):
        """
        This function is used to play a move according
        to the percepts, player and time left provided as input.
        It must return an action representing the move the player
        will perform.
        :param percepts: dictionary representing the current board
            in a form that can be fed to `dict_to_board()` in avalam.py.
        :param player: the player to control in this step (-1 or 1)
        :param step: the current step number, starting from 1
        :param time_left: a float giving the number of seconds left from the time
            credit. If the game is not time-limited, time_left is None.
        :return: an action
            eg; (1, 4, 1 , 3) to move tower on cell (1,4) to cell (1,3)
        """
        board: Board = dict_to_board(percepts)
        if player == 1:
            best_action = minimax(2, True, board)
        else:
            best_action = minimax(2, False, board)
        print("percept:", percepts)
        print("player:", player)
        print("step:", step)
        print("time left:", time_left if time_left else '+inf')
        return best_action[1]


if __name__ == "__main__":
    agent_main(MyAgent())


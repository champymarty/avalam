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

class MinmaxAlphaBeta:
    def heuristique(self, board: Board):
        return board.get_score()

    def apply_min(self, depth, board: Board, alpha: float, beta: float):
        if depth == 0 or board.is_finished():
            return self.heuristique(board), None
        minEval = float('inf')
        best_action = None
        for action in board.get_actions():
            new_board = board.clone()
            new_board.play_action(action)
            evaluation = self.apply_max(depth-1, new_board, alpha, beta)[0]
            if evaluation < minEval:
                minEval = evaluation
                best_action = action
                beta = min(beta, minEval)
            if minEval <= alpha:
                return minEval, best_action
        return minEval, best_action

    def apply_max(self, depth, board: Board, alpha: float, beta: float):
        if depth == 0 or board.is_finished():
            return self.heuristique(board), None
        maxEval = float('-inf')
        best_action = None
        for action in board.get_actions():
            new_board = board.clone()
            new_board.play_action(action)
            evaluation = self.apply_min(depth-1, new_board, alpha, beta)[0]
            if evaluation > maxEval:
                maxEval = evaluation
                best_action = action
                alpha = max(alpha, maxEval)
            if maxEval >= beta:
                return maxEval, best_action
        return maxEval, best_action
    
    def run_minimax(self, depth, max_player: bool, board: Board):
        alpha = float('-inf')
        beta = float('inf')
        if max_player:
            return self.apply_max(depth, board, alpha, beta)
        else:
            return self.apply_min(depth, board, alpha, beta)

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
        algorithm = MinmaxAlphaBeta()
        if player == 1:
            best_action = algorithm.run_minimax(3, True, board)
        else:
            best_action = algorithm.run_minimax(3, False, board)
        print("percept:", percepts)
        print("player:", player)
        print("step:", step)
        print("time left:", time_left if time_left else '+inf')
        
        return best_action[1]


if __name__ == "__main__":
    agent_main(MyAgent())
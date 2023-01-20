#!/usr/bin/env python3
"""
Avalam agent.
Copyright (C) 2022, Raphael St-Jean, Charles Fakih
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
from custom_board import CustomBoard, dict_to_board_custom
from time import time
from datetime import datetime
import traceback

LOGING_ACTIVATED = False


#logging
import os
import logging
try:
    logger = logging.getLogger("player")
    logger.disabled = not LOGING_ACTIVATED
    if LOGING_ACTIVATED:
        logger.setLevel(logging.INFO)
        dir_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "logs")
        if not os.path.exists(dir_path):
            os.mkdir(dir_path)
        file = os.path.join(dir_path, f"{datetime.now()}_player.log")
        handler = logging.FileHandler(filename=file, encoding="utf-8", mode="w")
        handler.setFormatter(logging.Formatter('%(asctime)s:%(message)s'))
        logger.addHandler(handler)
except:
    print(traceback.format_exc())
    logger.disabled = True

        
class MinmaxAlphaBetaIterativeDepth:
        
    def __init__(self) -> None:
        self.start_time = None
        self.remaining_time = None
        self.max_depth_reached = False
        self.first_run = True
        self.logger = logger 
    
    def was_max_depth_reached(self) -> bool:
        return self.max_depth_reached
    
    def get_heuristique(self, board: CustomBoard):
        return self.heuristique(board)
    
    def heuristique(self, board: CustomBoard):
        score, score_mouvement_tower, score_max_height = board.get_scores()
        return score + 0.2 * score_mouvement_tower + 0.5 * score_max_height
    

    def apply_min(self, depth, board: CustomBoard, alpha: float, beta: float):
        if time() - self.start_time > self.remaining_time and not self.first_run:
            return None, None
        if board.is_finished():
            self.max_depth_reached = True
            return self.get_heuristique(board), None
        if depth == 0:
            return self.get_heuristique(board), None
        minEval = float('inf')
        best_action = None
        for action in board.get_actions():
            new_board = board.clone()
            new_board.play_action(action)
            evaluation = self.apply_max(depth - 1, new_board, alpha, beta)[0]
            if evaluation is None:
                return None, None
            if evaluation < minEval:
                minEval = evaluation
                best_action = action
                beta = min(beta, minEval)
            if minEval <= alpha:
                return minEval, best_action
        return minEval, best_action

    def apply_max(self, depth, board: CustomBoard, alpha: float, beta: float):
        if time() - self.start_time > self.remaining_time and not self.first_run:
            return None, None
        if board.is_finished():
            self.max_depth_reached = True
            return self.get_heuristique(board), None
        if depth == 0:
            return self.get_heuristique(board), None
        maxEval = float('-inf')
        best_action = None
        for action in board.get_actions():
            new_board = board.clone()
            new_board.play_action(action)
            evaluation = self.apply_min(depth - 1, new_board, alpha, beta)[0]
            if evaluation is None:
                return None, None
            if evaluation > maxEval:
                maxEval = evaluation
                best_action = action
                alpha = max(alpha, maxEval)
            if maxEval >= beta:
                return maxEval, best_action
        return maxEval, best_action
    
    def _try_minmax(self, depth: int, remaining_time: float, max_player: bool, board: CustomBoard):
        alpha = float('-inf')
        beta = float('inf')
        best_move = None
        self.start_time = time()
        self.remaining_time = remaining_time
        if max_player:
            best_move = self.apply_max(depth, board, alpha, beta)[1]
        else:
            best_move = self.apply_min(depth, board, alpha, beta)[1]
        return best_move
    
    def run_minimax(self, min_depth, max_time: float, max_player: bool, board: CustomBoard):
        self.logger.info(f"Run initial minmax with {max_time} secondes available")
        self.logger.info(f"Run initial minmax with dept {min_depth}")
        
        start_time = time()
        remaining_time = max_time - ( time() - start_time )
        best_move = self._try_minmax(min_depth, remaining_time, max_player, board)
        self.logger.info(f"Done ! Move: {best_move}")
        
        remaining_time = max_time - ( time() - start_time )
        if remaining_time/max_time < 0.7:
            return best_move
        
        self.first_run = False
        depth = min_depth + 1
        while remaining_time > 0 and not self.was_max_depth_reached():
            self.logger.info(f"Run minmax with dept {depth}")
            start_time_dept = time()
            best_move_tmp = self._try_minmax(depth, remaining_time, max_player, board)
            deltatime_dept = time() - start_time_dept
            self.logger.info(f"Done ! Move: {best_move_tmp}")
            
            if best_move_tmp is not None:
                # the best move is the move selected with the biggest dept
                best_move = best_move_tmp
            else:
                self.logger.info(f"Time ran out, exiting dept {depth} try")
                break
            
            remaining_time = max_time - ( time() - start_time )
            if deltatime_dept * 1.5 > remaining_time:
                # next dept have no chance to complete in time
                self.logger.info(f"Not trying next dept. Remaining time: {remaining_time}   last dept time: {deltatime_dept}")
                break
            depth += 1
        return best_move
    
class MyAgent(Agent):

    """My Avalam agent."""
        
    def __init__(self) -> None:
        super().__init__()
        self.usual_time = None
        self.round = 0
        self.logger = logger

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
        try:
            self.round += 1
            self.logger.info(f"Play of the bot: {self.round}")
            start = time()
            if self.usual_time is None:
                self.usual_time = time_left / 20

            self.logger.info(f"Time left for move: {time_left}")
            board: CustomBoard = dict_to_board_custom(percepts)
            algorithm = MinmaxAlphaBetaIterativeDepth()
            
            max_player = False
            if player == 1:
                max_player = True
            
            if self.usual_time > time_left:
                if time_left >= self.usual_time * 2/3:
                    best_action = algorithm.run_minimax(2, time_left * 2/9, max_player, board)
                elif time_left >= self.usual_time * 4/9:
                    best_action = algorithm.run_minimax(1, time_left * 1/9, max_player, board)
                elif time_left >= self.usual_time * 1/9:
                    best_action = algorithm.run_minimax(1, time_left * 1/18, max_player, board)
                else:
                    best_action = algorithm.run_minimax(1, time_left * 1/45, max_player, board)
            else:
                # a lot if time remaining
                best_action = algorithm.run_minimax(3, self.usual_time, max_player, board)
            
            self.logger.info(f"Time to select move: {time() - start}")
            self.logger.info(f"Total Time left after move: {time_left - (time() - start)}")
            self.logger.info(f"Move chosen: {best_action}\n")
            return best_action
        except:
            self.logger.info(traceback.format_exc())


if __name__ == "__main__":
    agent_main(MyAgent())
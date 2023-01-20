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
import math
import random
from typing import List, Tuple
from avalam import *
import numpy as np
import sys

#logging
import os
import logging
logger = logging.getLogger("player")
logger.setLevel(logging.INFO)
file = os.path.join(os.path.dirname(os.path.realpath(__file__)), "player.log")
handler = logging.FileHandler(filename=file, encoding="utf-8", mode="w")
handler.setFormatter(logging.Formatter('%(asctime)s:%(message)s'))
logger.addHandler(handler)

def rollout_policy(possible_moves, current_board: Board, player: int):
    # TOOOOOOOOOO SLOW      :(
    if player == 1:
        selected_score = sys.maxsize * 2 + 1
    else:
        selected_score = -(sys.maxsize * 2 + 1)
    selected_move = None
    for possible_move in possible_moves:
        new_board = current_board.clone()
        new_board.play_action(possible_move)
        score = new_board.get_score()
        if player == 1:
            if score < selected_score:
                selected_score = score
                selected_move = possible_move
        else:
            if score > selected_score:
                selected_score = score
                selected_move = possible_move
    if selected_move is None:
        logger.error("No move selected ... FALLING bacl to random")
        return random.choice(possible_moves)
    return selected_move

class MonteCarloTreeSearchNode():
    player_number = 1
    
    def __init__(self, board: Board, parent=None, parent_action=None):
        self.state: Board = board
        self.parent: MonteCarloTreeSearchNode = parent
        self.parent_action = parent_action
        self.children: List[MonteCarloTreeSearchNode] = []
        self._number_of_visits = 0
        self.points = 0
        self.untried_actions()
        
    def rollout_policy_random(self, possible_moves):
        return random.choice(possible_moves)

    def untried_actions(self) -> List[Tuple]:
        """
        Returns the list of untried actions from a given state. 
        For the first turn of our game there are 81 possible actions. 
        For the second turn it is 8 or 9. This varies in our game.
        """
        self._untried_actions: List[Tuple] = list(self.state.get_actions())
        return self._untried_actions
        
    def q(self) -> int:
        """Returns score of the node"""
        return self.points
    
    def n(self) -> int:
        """Returns the number of times that node was visited."""
        return self._number_of_visits
    
    def expand(self):
        """
        From the present state, next state is generated depending on the action which is carried out. 
        In this step all the possible child nodes corresponding to generated states are appended to
        the children array and the child_node is returned. The states which are possible from the present
        state are all generated and the child_node corresponding to this generated state is returned.
        """
        action = self._untried_actions.pop()
        child_node = self.move(action)

        self.children.append(child_node)
        return child_node
    
    def is_terminal_node(self) -> bool:
        """
        This is used to check if the current node is terminal or not. Terminal node is reached when the game is over.
        """
        return self.state.is_finished()
    
    def rollout(self):
        """
        From the current state, entire game is simulated till there is an outcome for the game.
        This outcome of the game is returned. For example if it results in a win, the outcome is 1.
        Otherwise it is -1 if it results in a loss. And it is 0 if it is a tie. If the entire game is randomly simulated,
        that is at each turn the move is randomly selected out of set of possible moves, it is called light playout.
        """
        current_rollout_state = self
        
        while not current_rollout_state.is_game_over():
            
            possible_moves = current_rollout_state.get_legal_actions()
            if len(possible_moves) == 0 :
                break
            action = self.rollout_policy_random(possible_moves)
            # action = rollout_policy(possible_moves, current_rollout_state.state, MonteCarloTreeSearchNode.player_number)
            
            current_rollout_state = current_rollout_state.move(action)
            
        return current_rollout_state.game_result()
    
    def backpropagate(self, result: int):
        """
        In this step all the statistics for the nodes are updated. 
        Untill the parent node is reached, the number of visits for each node is incremented by 1. 
        If the result is 1, that is it resulted in a win, then the win is incremented by 1. 
        Otherwise if result is a loss, then loss is incremented by 1.
        """
        self._number_of_visits += 1.
        self.points += result
        if self.parent is not None:
            self.parent.backpropagate(result)
            
    def is_fully_expanded(self):
        """
        All the actions are poped out of _untried_actions one by one. 
        When it becomes empty, that is when the size is zero, it is fully expanded.
        """
        return len(self._untried_actions) == 0
    
    def best_child(self, c_param=1.41):
        """
        Once fully expanded, this function selects the best child out of the children array. 
        The first term in the formula corresponds to exploitation and the second term corresponds to exploration.
        """
        choices_weights = [(c.q() / c.n()) + c_param * math.sqrt((2 * math.log(self.n()) / c.n())) for c in self.children]
        return self.children[np.argmax(choices_weights)]
    
    def _tree_policy(self):
        """
        Selects node to run rollout.
        """
        current_node = self
        while not current_node.is_terminal_node():
            
            if not current_node.is_fully_expanded():
                return current_node.expand()
            else:
                current_node = current_node.best_child()
        return current_node
    
    def get_legal_actions(self): 
        '''
        Constructs a list of all
        possible actions from current state.
        Returns a list.
        '''
        return list(self.state.get_actions())
    
    def best_action(self):
        """
        This is the best action function which returns the node corresponding to best possible move. 
        The step of expansion, simulation and backpropagation are carried out by the code above.
        """
        simulation_no = 1000
        
        
        for i in range(simulation_no):
            v = self._tree_policy()
            reward = v.rollout()
            v.backpropagate(reward)
        
        return self.best_child()
    
    def is_game_over(self):
        '''
            return if game over in that state
        '''
        self.state.is_finished()
    
    def move(self, action):
        '''
        Modify according to your game or 
        needs. Changes the state of your 
        board with a new value. For a normal
        Tic Tac Toe game, it can be a 3 by 3
        array with all the elements of array
        being 0 initially. 0 means the board 
        position is empty. If you place x in
        row 2 column 3, then it would be some 
        thing like board[2][3] = 1, where 1
        represents that x is placed. Returns 
        the new state after making a move.
        '''
        new_board = self.state.clone()
        new_board.play_action(action)
        return MonteCarloTreeSearchNode(new_board, parent=self, parent_action=action)
    
    def game_result(self):
        """
        Modify according to your game or 
        needs. Returns 1 or 0 or -1 depending
        on your state corresponding to win,
        tie or a loss.
        """
        score = self.state.get_score()
        if score == 0:
            return 0
        
        if MonteCarloTreeSearchNode.player_number > 0: # player 1 -> red
            return score
        else: # player -1 -> Yellow
            return -score
        
    def __eq__(self, other):
        return self.state.m == other.state.m
        
class MyAgent(Agent):

    """My Avalam agent."""
    def __init__(self):
        self.root: MonteCarloTreeSearchNode = None
    
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
        current_state: Board = dict_to_board(percepts)
        MonteCarloTreeSearchNode.player_number = player
        
        start_node = MonteCarloTreeSearchNode(current_state)
        print("percept:", percepts)
        print("player:", player)
        print("step:", step)
        print("time left:", time_left if time_left else '+inf')
        return start_node.best_action().parent_action
        
        


if __name__ == "__main__":
    agent_main(MyAgent())


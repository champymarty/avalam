from avalam import Board

class CustomBoard(Board):

    # initial_board = array(Board.initial_board)
    
    def __init__(self, percepts=Board.initial_board, max_height=Board.max_height, invert=False):
        super().__init__(percepts, max_height, invert)
    
    def clone(self):
        """Return a clone of this object."""
        return CustomBoard(self.m)
    
    def get_scores(self):
        score = 0
        score_mov = 0
        score_max_height = 0
        for i in range(self.rows):
            for j in range(self.columns):
                if self.m[i][j] == 0:
                    continue
                is_mouvable = self.is_tower_movable(i, j)
                is_max_height = abs(self.m[i][j]) == self.max_height
                delta = 1
                if self.m[i][j] < 0:
                    delta = -1
                    
                score += delta
                if is_max_height:
                    score_max_height += delta
                elif not is_mouvable:
                    score_mov += delta
        return score, score_mov, score_max_height

def dict_to_board_custom(dictio):
    """Return a clone of the board object encoded as a dictionary."""
    clone_board = CustomBoard()
    clone_board.m = dictio['m']
    clone_board.rows = dictio['rows']
    clone_board.max_height = dictio['max_height']

    return clone_board    
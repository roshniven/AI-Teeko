import random
import copy
import numpy as np

class TeekoPlayer:
    """ An object representation for an AI game player for the game Teeko.
    """
    board = [[' ' for j in range(5)] for i in range(5)]
    pieces = ['b', 'r']
    player = None

    def __init__(self):
        """ Initializes a TeekoPlayer object by randomly selecting red or black as its
        piece color.
        """
        self.my_piece = random.choice(self.pieces)
        self.opp = self.pieces[0] if self.my_piece == self.pieces[1] else self.pieces[1]


    def make_move(self, state):
        """ Selects a (row, col) space for the next move. You may assume that whenever
        this function is called, it is this player's turn to move.

        Args:
            state (list of lists): should be the current state of the game as saved in
                this TeekoPlayer object. Note that this is NOT assumed to be a copy of
                the game state and should NOT be modified within this method (use
                place_piece() instead). Any modifications (e.g. to generate successors)
                should be done on a deep copy of the state.

                In the "drop phase", the state will contain less than 8 elements which
                are not ' ' (a single space character).

        Return:
            move (list): a list of move tuples such that its format is
                    [(row, col), (source_row, source_col)]
                where the (row, col) tuple is the location to place a piece and the
                optional (source_row, source_col) tuple contains the location of the
                piece the AI plans to relocate (for moves after the drop phase). In
                the drop phase, this list should contain ONLY THE FIRST tuple.

        Note that without drop phase behavior, the AI will just keep placing new markers
            and will eventually take over the board. This is not a valid strategy and
            will earn you no points.
        """

        player = self.my_piece
        number_pieces = sum(i.count(self.my_piece) for i in state)
        drop_phase = number_pieces < 4

        if not drop_phase:
            _, state_b = self.find_max(state, 0, 3)
            pos = np.argwhere(np.array(state_b) != np.array(state))

            if state[pos[0][0]][pos[0][1]] != ' ':
                r, c = pos[1][0], pos[1][1]
                r_org, c_org = pos[0][0], pos[0][1]
            else:
                r, c = pos[0][0], pos[0][1]
                r_org, c_org = pos[1][0], pos[1][1]
            return [(int(r), int(c)), (int(r_org), int(c_org))]

        can_move = np.argwhere(np.array(state) == ' ')
        pos_new = can_move[np.random.choice(can_move.shape[0])]
        r, c = pos_new[0], pos_new[1]
        return [(int(r), int(c))]


    def get_successors(self, state, piece):
        number_pieces = sum(i.count(self.my_piece) for i in state)
        drop_phase = number_pieces < 4
        move = []

        if drop_phase:
            for r, c in np.argwhere(np.array(state) == " "):
                deep_copy = copy.deepcopy(state)
                deep_copy[r][c] = piece
                move.append(deep_copy)
        else:
            for r, c in np.argwhere(piece == np.array(state)):
                for i, j in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                    if 0<=r+i<=4 and 0<=c+j<=4 and state[r+i][c+j] == " ":
                        deep_copy = copy.deepcopy(state)
                        deep_copy[r][c] = " "
                        deep_copy[r+i][c+j] = piece
                        move.append(deep_copy)
        return move


    def find_min(self, state, d, max_d):
        state_b = None
        val_b = float('-inf')
        if d >= max_d or self.game_value(state) != 0:
            return self.heuristic_game_value(state, self.opp), state

        for s in self.get_successors(state, self.opp):
            v, _ = self.find_max(s, d+1, max_d)
            if v > val_b:
                val_b = v
                state_b = s
        if state_b is not None:
            return val_b, state_b
        return self.heuristic_game_value(state, self.opp), state


    def find_max(self, state, d, max_d):
        state_b = None
        val_b = float('-inf')
        if d >= max_d or self.game_value(state) != 0:
            return self.heuristic_game_value(state, self.my_piece), state

        for s in self.get_successors(state, self.my_piece):
            v, _ = self.find_min(s, d+1, max_d)
            if v > val_b:
                val_b = v
                state_b = s
        if state_b is not None:
            return val_b, state_b
        return self.heuristic_game_value(state, self.my_piece), state


    def opponent_move(self, move):
        """ Validates the opponent's next move against the internal board representation.
        You don't need to touch this code.

        Args:
            move (list): a list of move tuples such that its format is
                    [(row, col), (source_row, source_col)]
                where the (row, col) tuple is the location to place a piece and the
                optional (source_row, source_col) tuple contains the location of the
                piece the AI plans to relocate (for moves after the drop phase). In
                the drop phase, this list should contain ONLY THE FIRST tuple.
        """
        if len(move) > 1:
            source_row = move[1][0]
            source_col = move[1][1]
            if source_row != None and self.board[source_row][source_col] != self.opp:
                self.print_board()
                print(move)
                raise Exception("You don't have a piece there!")
            if abs(source_row - move[0][0]) > 1 or abs(source_col - move[0][1]) > 1:
                self.print_board()
                print(move)
                raise Exception('Illegal move: Can only move to an adjacent space')
        if self.board[move[0][0]][move[0][1]] != ' ':
            raise Exception("Illegal move detected")
        self.place_piece(move, self.opp)


    def place_piece(self, move, piece):
        """ Modifies the board representation using the specified move and piece

        Args:
            move (list): a list of move tuples such that its format is
                    [(row, col), (source_row, source_col)]
                where the (row, col) tuple is the location to place a piece and the
                optional (source_row, source_col) tuple contains the location of the
                piece the AI plans to relocate (for moves after the drop phase). In
                the drop phase, this list should contain ONLY THE FIRST tuple.

                This argument is assumed to have been validated before this method
                is called.
            piece (str): the piece ('b' or 'r') to place on the board
        """
        if len(move) > 1:
            self.board[move[1][0]][move[1][1]] = ' '
        self.board[move[0][0]][move[0][1]] = piece


    def print_board(self):
        """ Formatted printing for the board """
        for row in range(len(self.board)):
            line = str(row)+": "
            for cell in self.board[row]:
                line += cell + " "
            print(line)
        print("   A B C D E")


    def game_value(self, state):
        """ Checks the current board status for a win condition

        Args:
        state (list of lists): either the current state of the game as saved in
            this TeekoPlayer object, or a generated successor state.

        Returns:
            int: 1 if this TeekoPlayer wins, -1 if the opponent wins, 0 if no winner

        TODO: complete checks for diagonal and box wins
        """
        # check horizontal wins
        for row in state:
            for i in range(2):
                if row[i] != ' ' and row[i] == row[i+1] == row[i+2] == row[i+3]:
                    return 1 if row[i] == self.my_piece else -1

        # check vertical wins
        for col in range(5):
            for i in range(2):
                if state[i][col] != ' ' and state[i][col] == state[i+1][col] == state[i+2][col] == state[i+3][col]:
                    return 1 if state[i][col] == self.my_piece else -1

        # check diagonal wins
        diagonals = [
        [(0, 0), (1, 1), (2, 2), (3, 3)],
        [(1, 1), (2, 2), (3, 3), (4, 4)],
        [(0, 4), (1, 3), (2, 2), (3, 1)],
        [(1, 3), (2, 2), (3, 1), (4, 0)]
        ]

        for diagonal in diagonals:
            piece = state[diagonal[0][0]][diagonal[0][1]]
            if piece != ' ' and all(state[i][j] == piece for i, j in diagonal):
                return 1 if piece == self.my_piece else -1

        # check box wins
        for i in range(4):
            for j in range(4):
                if state[i][j] != ' ' and state[i][j] == state[i+1][j] == state[i][j+1] == state[i+1][j+1]:
                    if self.my_piece == state[i][j]:
                        return 1
                    else:
                        return -1

        return 0 # no winner yet


    def heuristic_game_value(self, state, piece):
        player = []
        opp = []
        val = (2, 2)
        if self.game_value(state) != 0:
            return 1000 if self.game_value(state) == 1 else -1000

        for r, c in np.argwhere(self.my_piece == np.array(state)):
            player.append(abs(r - val[0]) + abs(c - val[1]))
        for r, c in np.argwhere(self.opp == np.array(state)):
            opp.append(abs(r - val[0]) + abs(c - val[1]))
        player_avg = sum(player)/len(player) if player else 0
        opp_avg = sum(opp)/len(opp) if opp else 0
        return ((10 - player_avg) - (10 - opp_avg)) / 10


############################################################################
#
# THE FOLLOWING CODE IS FOR SAMPLE GAMEPLAY ONLY
#
############################################################################
def main():
    print('Hello, this is Samaritan')
    ai = TeekoPlayer()
    piece_count = 0
    turn = 0

    # drop phase
    while piece_count < 8 and ai.game_value(ai.board) == 0:

        # get the player or AI's move
        if ai.my_piece == ai.pieces[turn]:
            ai.print_board()
            move = ai.make_move(ai.board)
            ai.place_piece(move, ai.my_piece)
            print(ai.my_piece+" moved at "+chr(move[0][1]+ord("A"))+str(move[0][0]))
        else:
            move_made = False
            ai.print_board()
            print(ai.opp+"'s turn")
            while not move_made:
                player_move = input("Move (e.g. B3): ")
                while player_move[0] not in "ABCDE" or player_move[1] not in "01234":
                    player_move = input("Move (e.g. B3): ")
                try:
                    ai.opponent_move([(int(player_move[1]), ord(player_move[0])-ord("A"))])
                    move_made = True
                except Exception as e:
                    print(e)

        # update the game variables
        piece_count += 1
        turn += 1
        turn %= 2

    # move phase - can't have a winner until all 8 pieces are on the board
    while ai.game_value(ai.board) == 0:

        # get the player or AI's move
        if ai.my_piece == ai.pieces[turn]:
            ai.print_board()
            move = ai.make_move(ai.board)
            ai.place_piece(move, ai.my_piece)
            print(ai.my_piece+" moved from "+chr(move[1][1]+ord("A"))+str(move[1][0]))
            print("  to "+chr(move[0][1]+ord("A"))+str(move[0][0]))
        else:
            move_made = False
            ai.print_board()
            print(ai.opp+"'s turn")
            while not move_made:
                move_from = input("Move from (e.g. B3): ")
                while move_from[0] not in "ABCDE" or move_from[1] not in "01234":
                    move_from = input("Move from (e.g. B3): ")
                move_to = input("Move to (e.g. B3): ")
                while move_to[0] not in "ABCDE" or move_to[1] not in "01234":
                    move_to = input("Move to (e.g. B3): ")
                try:
                    ai.opponent_move([(int(move_to[1]), ord(move_to[0])-ord("A")),
                                    (int(move_from[1]), ord(move_from[0])-ord("A"))])
                    move_made = True
                except Exception as e:
                    print(e)

        # update the game variables
        turn += 1
        turn %= 2

    ai.print_board()
    if ai.game_value(ai.board) == 1:
        print("AI wins! Game over.")
    else:
        print("You win! Game over.")


if __name__ == "__main__":
    main()

# Author: Ryan McKenzie
# Date: 5/24/2020
# Description: This program simulates the game Gess in an object-oriented fashion.


class Board:
    """The Board class defines the game space and shows the area and its pieces,
        providing the framing for the pieces and the matrix the game is played on"""

    def __init__(self):
        """The Board initializes with the game's startup locations arranged on a
        grid with alphabetic labels"""
        self._board_area = [[" " for i in range(20)] for j in range(20)]

        # Starting setup for board includes these coordinates black, and their mirror white
        black_start = [(1, 2), (2, 2), (2, 1), (2, 3), (3, 2), (4, 1), (4, 3), (5, 2), (6, 1), (6, 3), (7, 1),
                       (7, 2), (7, 3), (8, 1), (8, 2), (8, 3), (9, 1), (9, 2), (9, 3), (10, 1), (10, 2), (10, 3),
                       (11, 1), (11, 3), (12, 1), (12, 2), (12, 3), (13, 1), (13, 3), (14, 2), (15, 1), (15, 3),
                       (16, 2), (17, 1), (17, 2), (17, 3), (18, 2), (2, 6), (5, 6), (8, 6), (11, 6),
                       (14, 6), (17, 6)]

        # Border points set for clearing out stones that move beyond the border
        self._border = set((0, i) for i in range(20)) | set((19, i) for i in range(20))
        self._border = self._border | set((i, 0) for i in range(20)) | set((i, 19) for i in range(20))

        # Fill black and white stones
        for coord in black_start:
            self._board_area[coord[0]][coord[1]] = "B"
            self._board_area[coord[0]][-coord[1] - 1] = "W"

        # Alphabetic indexing of board for alpha-numeric movement inputs
        self._locmap = dict(zip("abcdefghijklmnopqrst", range(20)))

    def display(self):
        """The display method generates the board sideways"""
        for row in self._board_area:
            print(row, end="\n")

    def get_board_area(self):
        """Returns the area array of the board"""
        return self._board_area

    def get_map(self):
        """Returns location map for alphabetic indexing of board,
        to convert alphabetic input to numeric"""
        return self._locmap

    def get_border(self):
        """Returns the set of board point which make up the border of the board"""
        return self._border


class Piece:
    """Piece class defines the 3x3 area 'piece' used for the game and handles
        operations on the selected piece, including its valid movements and
        its physical relocation concept."""

    def __init__(self, center, game_board):
        """The piece class initializes with a defined center and the area around it."""
        self._center = center
        self._x_coord = center[0]
        self._y_coord = center[1]
        self._area = {(self._x_coord + i, self._y_coord + j) for i in range(-1, 2) for j in range(-1, 2)}
        self._board = game_board.get_board_area()

        # self._filled represents the filled directionality points of the area
        #   (0,0) should not be in the filled set, as it is not valid for movement
        self._filled = {(pos[0] - self._x_coord, pos[1] - self._y_coord)
                        for pos in self._area if self._board[pos[0]][pos[1]] != " "} - {(0, 0)}

        # If the center point is filled, movement is not limited
        if self._board[self._x_coord][self._y_coord] != " ":
            self._unlimited = True

        else:
            self._unlimited = False

    def get_area(self):
        """Returns all (x, y) points in the piece's area as a set"""
        return self._area

    def get_area_contents(self):
        """Returns all types of stones or lack of stones in the piece's area"""
        types = set()

        # Iterates through self._area and adds values to return set
        for point in self._area:
            types.add(self._board[point[0]][point[1]])

        return types

    def valid_moves(self):
        """Returns available moves given the piece structure and game board
        as a set of potential (x, y) locations"""
        valid = set()

        # If the center is filled, so unlimited movement is allowed
        if self._unlimited is True:

            # For each value of filled, add that value to the center until the value is out of bounds
            #   to acquire each movement point that can result
            for pos in self._filled:
                loc = self._center
                while 0 < loc[0] < 20 and 0 < loc[1] < 20:
                    loc = (loc[0] + pos[0], loc[1] + pos[1])
                    valid.add(loc)

        else:
            # If the movement is limited, only allow movement up to 3 spaces
            loc = self._center
            for pos in self._filled:
                if 0 < loc[0] + pos[0] < 20 and 0 < loc[1] + pos[1] < 20:
                    valid.add((loc[0] + pos[0], loc[1] + pos[1]))
                if 0 < loc[0] + 2 * pos[0] < 20 and 0 < loc[1] + 2 * pos[1] < 20:
                    valid.add((loc[0] + 2 * pos[0], loc[1] + 2 * pos[1]))
                if 0 < loc[0] + 3 * pos[0] < 20 and 0 < loc[1] + 3 * pos[1] < 20:
                    valid.add((loc[0] + 3 * pos[0], loc[1] + 3 * pos[1]))

        return valid

    def move(self, location):
        """move method moves area by displacement, using a dictionary to map each point to
        its new location, then moving as a unit to prevent multiple replacements."""
        disp_x = location[0] - self._x_coord
        disp_y = location[1] - self._y_coord
        board = self._board

        # Instantiate dictionary of displaced locations to value they will take
        mov_map = dict()
        for position in self._area:
            mov_map[(position[0] + disp_x, position[1] + disp_y)] = board[position[0]][position[1]]

        # Clear previous locations
        for position in self._area:
            board[position[0]][position[1]] = " "

        # Place stones to displaced location
        for position in self._area:
            board[position[0] + disp_x][position[1] + disp_y] = \
                mov_map[(position[0] + disp_x, position[1] + disp_y)]

        # Return the new stone locations for processing
        return set(mov_map.keys())


class GessGame:
    """The GessGame class handles the initialization and running of the game. It
        includes calls to the Piece class and Board class to create the board and
        the pieces, and handles the piece's overall movement rules, win scenarios,
        resignation and game loop."""
    def __init__(self):
        """Initializes GessGame data members"""
        self._game_state = "UNFINISHED"
        self._current_player = "BLACK"
        self._game_board = Board()

    def get_game_state(self):
        """Returns current game state, either UNFINISHED,
            WHITE_WON, or BLACK_WON"""
        return self._game_state

    def resign_game(self):
        """Current player resigns, so opposite player wins"""
        if self._current_player == "BLACK":
            self._game_state = "WHITE_WON"

        else:
            self._game_state = "BLACK_WON"

    def show_board(self):
        """Shows the game board in the output window"""
        self._game_board.display()

    def check_obstruction(self, start_x, start_y, end_x, end_y, piece):
        """Check_obstruction will check a valid move in the make_move function to assure
            the move does not encounter another piece during its movement toward its
            destination, and would otherwise invalidate the move in make_move()"""

        # Displacement for any single point in the area
        disp_x = end_x - start_x
        disp_y = end_y - start_y

        # Piece's area to shift for obstructions
        space = piece.get_area()

        # Game board area, initialize check spaces for while loop
        board_space = self._game_board.get_board_area()
        check_x = 0
        check_y = 0

        # Assign correct shift value for displacement
        if disp_x > 0:
            shift_x = 1
        elif disp_x == 0:
            shift_x = 0
        else:
            shift_x = -1

        if disp_y > 0:
            shift_y = 1
        elif disp_y == 0:
            shift_y = 0
        else:
            shift_y = -1

        # For each point in space
        for point in space:
            scale = 1
            # Gradually shift values in piece area up to displacement and check if the space is occupied
            while (check_x, check_y) != (point[0] + disp_x, point[1] + disp_y):
                check_x = point[0] + shift_x * scale
                check_y = point[1] + shift_y * scale

                # If an obstruction is found, and it is not a piece meant to be captured
                #   ie, a piece in the end-position, return True
                if ((check_x, check_y) not in space) and board_space[check_x][check_y] != " ":
                    if (check_x, check_y) != (point[0] + disp_x, point[1] + disp_y):
                        return True
                scale += 1
        # Return False if not obstructed
        return False

    def check_win(self):
        """Checks for the black and white ring. If one side is missing its ring,
            that side will be set to lose."""

        # Sets rings initially to False
        black_ring = False
        white_ring = False

        # Gets board
        board = self._game_board.get_board_area()

        # Iterate through stone-holding points
        for i in range(1, 19):
            for j in range(1, 19):
                # Get the surroundings of each point
                surround = {board[i+1][j], board[i-1][j], board[i+1][j+1], board[i+1][j-1], board[i-1][j],
                            board[i-1][j-1], board[i-1][j+1], board[i][j-1]}

                # If the point is empty and surrounded by "B", there's a black ring
                if board[i][j] == " " and surround == {"B"}:
                    black_ring = True

                # If the point is empty and surrounded by "W", there's a white ring
                if board[i][j] == " " and surround == {"W"}:
                    white_ring = True

        if not black_ring:
            return "WHITE_WON"

        if not white_ring:
            return "BLACK_WON"

        return "UNFINISHED"

    def make_move(self, start_center, end_center):
        """Make move moves some given piece to another location and handles erasures.
            It validates the input to check for possible invalidation of the move of
            any type. """

        # Game must be unfinished
        if self._game_state != "UNFINISHED":
            return False

        # Starting point cannot be on the border of the board
        if start_center[0] == "a" or start_center[0] == "t" or int(start_center[1:]) >= 20 or \
                int(start_center[1:]) <= 0:
            return False

        # End center cannot be on the border (though edge pieces can)
        if end_center[0] == "a" or end_center[0] == "t" or int(end_center[1:]) >= 20 or \
                int(end_center[1:]) <= 0:
            return False

        # start_x is set using a dictionary conversion of the letter row to the numerical row
        start_x = self._game_board.get_map()[start_center[0]]
        start_y = int(start_center[1:]) - 1
        moving_piece = Piece((start_x, start_y), self._game_board)

        # No piece can contain black and white stones
        if "B" in moving_piece.get_area_contents() and "W" in moving_piece.get_area_contents():
            return False

        # Black cannot move white stones
        if self._current_player == "BLACK" and "W" in moving_piece.get_area_contents():
            return False

        # White cannot move black stones
        if self._current_player == "WHITE" and "B" in moving_piece.get_area_contents():
            return False

        end_x = self._game_board.get_map()[end_center[0]]
        end_y = int(end_center[1:]) - 1

        # If end point tuple is not in set of valid moves for point, return invalid
        if (end_x, end_y) not in moving_piece.valid_moves():
            return False

        if self.check_obstruction(start_x, start_y, end_x, end_y, moving_piece):
            return False

        # Assign the returned set to a variable
        new = moving_piece.move((end_x, end_y))

        # Iterate through new points, if any our in the border, delete them
        for stone in new:
            if stone in self._game_board.get_border():
                self._game_board.get_board_area()[stone[0]][stone[1]] = " "

        self._game_state = self.check_win()

        # If the game will be continuing
        if self._game_state == "UNFINISHED":

            # Reverse the current player
            if self._current_player == "BLACK":
                self._current_player = "WHITE"
            else:
                self._current_player = "BLACK"

        # Return True
        return True




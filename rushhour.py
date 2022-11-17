from operator import itemgetter
from copy import deepcopy

class RushHour:
    """
        RushHour class represents an 6x6 rush-hour type puzzle. ...
    """

    ACTIONS = ['up', 'right', 'down', 'left']

    def __init__(self, p):
        self.string_puzzle = None
        self.board = [['.','.','.','.','.','.'],
                      ['.','.','.','.','.','.'],
                      ['.','.','.','.','.','.'],
                      ['.','.','.','.','.','.'],
                      ['.','.','.','.','.','.'],
                      ['.','.','.','.','.','.']]
        self.fuel = {}
        self.initialize_game(p)

    def set_new_state(self, string, board, fuel):
        self.string_puzzle = string
        self.board = board
        self.fuel = fuel

    # initializes the state of the game
    def initialize_game(self, p):
        self.string_puzzle = p[0]

        # set the game board according to the list
        a_coordinates = []
        list_index = 0
        for y in range(0, 6):
            for x in range(0, 6):
                self.board[x][y] = self.string_puzzle[list_index]
                if (self.string_puzzle[list_index] == 'A'): a_coordinates.append((x, y)) # save ambulance coordinates
                if (self.board[x][y] not in self.fuel) and (self.board[x][y] != '.'):
                    self.fuel[self.board[x][y]] = 100
                list_index += 1
        
        # check if Ambulance (A) is horizontal in the middle of the board
        is_a_valid = all([True if coordinate[1] == 2 else False for coordinate in a_coordinates])
        if not is_a_valid: raise ValueError('Ambulance not properly placed on the board')

        # modify fuel levels if provided
        if len(p) > 1:
            for fuel_info in p[1:]:
                car = fuel_info[0]
                fuel_amount = int(fuel_info[1:])
                self.fuel[car] = fuel_amount
    
    # returns string representation from board representation
    def generate_string_from_board(self, board):
        string = ""
        for y in range(0, 6):
            for x in range(0, 6):
                string = string + board[x][y]
        return string

    # returns board representation from string representation
    def generate_board_from_string(self, string):
        board = [['.','.','.','.','.','.'],
                 ['.','.','.','.','.','.'],
                 ['.','.','.','.','.','.'],
                 ['.','.','.','.','.','.'],
                 ['.','.','.','.','.','.'],
                 ['.','.','.','.','.','.']]
        list_index = 0
        for y in range(0, 6):
            for x in range(0, 6):
                board[x][y] = string[list_index]
                list_index += 1
        return board

    # returns coordinates for specific car
    def get_car_coordinates(self, car, board=None):
        if board is None:
            board = self.board
        car_coordinates = []
        for y in range(0, 6):
            for x in range(0, 6):
                if board[x][y] == car: car_coordinates.append((x, y))
        return car_coordinates

    # draws the board
    def draw_board(self, board=None):
        if board is None:
            board = self.board
        print()
        for y in range(0, 6):
            for x in range(0, 6):
                print(F'{board[x][y]}', end="")
            print()
        print()

    # validates move
    def is_valid(self, car, action, moves, fuel=None, board=None):
        if board is None:
            board = self.board
        if fuel is None:
            fuel = self.fuel

        # invalid inputs
        if ((car not in fuel) or 
            (action not in self.ACTIONS) or
            (not str(moves).isdigit()) or (moves < 1)):
            return False

        if fuel[car] < moves: # car has insufficient fuel
            return False

        # get car coordinates on board
        car_coordinates = self.get_car_coordinates(car, board)

        is_vertical = all([True if coordinate[0] == car_coordinates[0][0] else False for coordinate in car_coordinates]) # check if car is vertical
        
        if action == 'up':
            if not is_vertical:
                return False
            # find coordinate with the lowest y value
            coordinate = min(car_coordinates,key=itemgetter(1))
            if (coordinate[1] == 0) or (coordinate[1] - moves < 0): # invalid moves (out of board)
                return False
            # another car is obstructing the move
            for i in range(1, moves + 1):
                if board[coordinate[0]][coordinate[1] - i] != '.':
                    return False
        elif action == 'right':
            if is_vertical:
                return False
            # find coordinate with the highest x value
            coordinate = max(car_coordinates,key=itemgetter(0))
            if (coordinate[0] == 5) or (coordinate[0] + moves > 5): # invalid moves (out of board)
                return False
            # another car is obstructing the move
            for i in range(1, moves + 1):
                if board[coordinate[0] + i][coordinate[1]] != '.':
                    return False
        elif action == 'down':
            if not is_vertical:
                return False
            # find coordinate with the highest y value
            coordinate = max(car_coordinates,key=itemgetter(1))
            if (coordinate[1] == 5) or (coordinate[1] + moves > 5): # invalid moves (out of board)
                return False
            # another car is obstructing the move
            for i in range(1, moves + 1):
                if board[coordinate[0]][coordinate[1] + i] != '.':
                    return False
        elif action == 'left':
            if is_vertical:
                return False
            # find coordinate with the lowest x value
            coordinate = min(car_coordinates,key=itemgetter(0))
            if (coordinate[0] == 0) or (coordinate[0] - moves < 0): # invalid moves (out of board)
                return False
            # another car is obstructing the move
            for i in range(1, moves + 1):
                if board[coordinate[0] - i][coordinate[1]] != '.':
                    return False
                    
        return True

    # checks if the game is done
    def is_end(self, board=None):
        if board is None:
            board = board
        # get coordinates of Ambulance (A)
        a_coordinates = self.get_car_coordinates('A', board)
        x_coordinate = max(a_coordinates,key=itemgetter(0))[0] # A's highest x-coordinate value
        if (x_coordinate == 5): return True
        else: return False

    """
        Returns (string, board, fuel) resulting from applying a specific action.
        If action is not allowed, returns None
    """
    def preview_action(self, car, action, moves, fuel=None, board=None,):
        if board is None:
            board = self.board
        if fuel is None:
            fuel = self.fuel

        if self.is_valid(car, action, moves, fuel, board):
            board_preview = deepcopy(board)
            fuel_preview = deepcopy(fuel)

            # get car coordinates on board
            car_coordinates = self.get_car_coordinates(car, board)

            # replace current car coordinates with empty space
            for coordinate in car_coordinates:
                board_preview[coordinate[0]][coordinate[1]] = '.'

            # handle new movement change
            if action == 'up':
                for coordinate in car_coordinates:
                    board_preview[coordinate[0]][coordinate[1] - moves] = car
            elif action == 'right':
                for coordinate in car_coordinates:
                    board_preview[coordinate[0] + moves][coordinate[1]] = car
                # remove car (except car 'A') if in valet position
                new_coordinates = self.get_car_coordinates(car, board_preview)
                x_coordinate = max(new_coordinates,key=itemgetter(0))[0] # car's highest x-coordinate value
                if ((all([True if coordinate[1] == 2 else False for coordinate in new_coordinates])) # car is in middle row
                    and (x_coordinate == 5) # car is all the way right
                    and (car != 'A')): # car is not ambulance
                    for coordinate in new_coordinates:
                        board_preview[coordinate[0]][coordinate[1]] = '.' # replace new car coordinates with empty space
            elif action == 'down':
                for coordinate in car_coordinates:
                    board_preview[coordinate[0]][coordinate[1] + moves] = car
            else:  # left
                for coordinate in car_coordinates:
                    board_preview[coordinate[0] - moves][coordinate[1]] = car

            # update other preview components
            fuel_preview[car] = fuel_preview[car] - moves
            string_preview = self.generate_string_from_board(board_preview)

            return string_preview, board_preview, fuel_preview
        else:
            return None

# Runner
if __name__ == '__main__':
    # 2.2 Dealing with input file
    puzzles_file = open('sample-input.txt', 'r')
    lines = [line.strip() for line in puzzles_file.readlines() if line.strip()] # Removes empty lines
    puzzles_file.close()

    for line in lines:
        if not line.startswith('#'): # skips over comment lines
            game = RushHour(line.split())
            game.draw_board()
            # string, board, fuel = game.preview_action('A', 'right', 1)
            # game.draw_board(board)
            # print(game.is_valid('L', 'right', 1))

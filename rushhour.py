from operator import itemgetter
from copy import deepcopy
import time

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
        self.cars = []
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
                if (self.string_puzzle[list_index] not in self.cars) and (self.string_puzzle[list_index] != "."): self.cars.append(self.string_puzzle[list_index]) # add car to car list
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

    # prints the board
    def print_board(self, board=None):
        if board is None:
            board = self.board
        print()
        for y in range(0, 6):
            for x in range(0, 6):
                print(F'{board[x][y]}', end="")
            print()
        print()
    
    # converts board to string
    def stringify_board(self, string_puzzle=None):
        if string_puzzle is None:
            string_puzzle = self.string_puzzle
        return f'{"".join(string_puzzle[:6])}\n' \
               f'{"".join(string_puzzle[6:12])}\n' \
               f'{"".join(string_puzzle[12:18])}\n' \
               f'{"".join(string_puzzle[18:24])}\n' \
               f'{"".join(string_puzzle[24:30])}\n' \
               f'{"".join(string_puzzle[30:36])}\n' \

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
            board = self.board
        # get coordinates of Ambulance (A)
        a_coordinates = self.get_car_coordinates('A', board)
        x_coordinate = max(a_coordinates,key=itemgetter(0))[0] # A's highest x-coordinate value
        if (x_coordinate == 5): return True
        else: return False

    """
        Returns (string, board, fuel) resulting from applying a specific action.
        If action is not allowed, returns None
    """
    def preview_action(self, car, action, moves, fuel=None, board=None):
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

class UCSNode:
    """
    Node class are the nodes used by SearchTree to build a search space of the Puzzle.
    """
    def __init__(self, string_puzzle, board, fuel, parent, car, action, moves, g, h):
        self.string_puzzle = string_puzzle
        self.board = board
        self.fuel = fuel
        self.parent = parent
        self.children = []
        self.car = car
        self.action = action
        self.moves = moves
        self.g = g  # actual path cost to current node
        self.h = h  # predicted cost to goal (heuristic)
        self.f = g + h

    def set_children(self, children):
        self.children(children)

class UCSSearchTree:

    ACTIONS = ['up', 'right', 'down', 'left']

    def __init__(self, initial_state, puzzle_number):
        self.id = puzzle_number
        self.puzzle = RushHour(initial_state) # create puzzle instance
        self.root = UCSNode(self.puzzle.string_puzzle, self.puzzle.board, self.puzzle.fuel, None, None, None, None, 0, 0)  # set root node
        self.open = [self.root]
        self.closed = []

    def uniform_cost_search(self):
        # initialize output files
        search_filename = "ucs-search-" + str(self.id) + ".txt"
        solution_filename = "ucs-sol-" + str(self.id) + ".txt"
        search_file = open(search_filename, "w")
        solution_file = open(solution_filename, "w")

        solution_file.write("Initial board configuration: " + self.puzzle.string_puzzle + "\n\n")
        solution_file.write(self.puzzle.stringify_board() + "\n")
        solution_file.write("Car fuel available: " + str(self.puzzle.fuel) + "\n")

        start = time.time()
        while True:
            if self.puzzle.is_end(self.open[0].board): # reached goal
                solution_file.write(F'Runtime: {round(time.time() - start, 7)}s \n')
                #### WRITE OTHER SOLUTION PARAMS
                break
            else:
                all_children = self.generate_all_children_ucs(self.open[0])
                ### check if state has already been visited in closed or if same state of lower cost already exists in open
                ### delete from all_children if true
                ### add rest of all children to open
                ### sort open by lowest g

                ### if open is empty return no solution
                break
        search_file.close()
        solution_file.close()
        return

    def generate_all_children_ucs(self, node):
        children = []
        for car in self.puzzle.cars:
            for action in self.ACTIONS:
                while True:
                    move_counter = 1
                    child = self.puzzle.preview_action(car, action, move_counter, node.fuel, node.board)
                    if child == None: break # changes action for car if move is not valid

                    # adds new children (cost is always +1 no matter the distance)
                    # no heuristic in ucs (h = 0)
                    else: children.append(UCSNode(child[0], child[1], child[2], node, car, action, move_counter, (node.g + 1), 0)) 
                    move_counter += 1
        node.set_children(children)
        return children
    
    def run(self):
        self.uniform_cost_search()

# Runner
if __name__ == '__main__':
    # 2.2 Dealing with input file
    puzzles_file = open('sample-input.txt', 'r')
    lines = [line.strip() for line in puzzles_file.readlines() if line.strip()] # Removes empty lines
    puzzles_file.close()

    for line in lines:
        if not line.startswith('#'): # skips over comment lines
            puzzle_counter = 1
            game = UCSSearchTree(line.split(), puzzle_counter)
            game.run()
            puzzle_counter += 1
            # string, board, fuel = game.preview_action('A', 'right', 1)
            # game.draw_board(board)
            # print(game.is_valid('L', 'right', 1))

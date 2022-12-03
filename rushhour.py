from operator import itemgetter, attrgetter
from copy import deepcopy
import os.path
import time
import csv

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

    # returns coordinates for specific car
    def get_car_coordinates(self, car, board=None):
        if board is None:
            board = self.board
        car_coordinates = []
        for y in range(0, 6):
            for x in range(0, 6):
                if board[x][y] == car: car_coordinates.append((x, y))
        return car_coordinates

    # TO HELP WITH DEBUGGING
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

class SearchNode:
    """
    SearchNodes are the nodes used by UCSSearchTree to build a UCS search space for the puzzle.
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
    
    def set_h(self, h):
        self.h = h
        self.f = self.g + h

    def set_children(self, children):
        self.children = children

class UCSSearchTree:

    ACTIONS = ['up', 'right', 'down', 'left']

    def __init__(self, initial_state, puzzle_number):
        self.id = puzzle_number
        self.puzzle = RushHour(initial_state) # create puzzle instance
        self.root = SearchNode(self.puzzle.string_puzzle, self.puzzle.board, self.puzzle.fuel, None, None, None, None, 0, 0)  # set root node
        self.open = [self.root] # list of open nodes
        self.closed = [] # list of closed nodes
        self.visited = [] # list of visited puzzle strings states (for easier search)
        self.solution_path = [] # list of nodes in the solution path

    """
    Searches for puzzle solution with the uniform cost search algorithm.
    Writes solution (if any) to solution file and search path to search file.
    Returns (as a list):
        Length of the solution (0 if no solution)
        Length of the Search Path
        Execution Time
    """
    def uniform_cost_search(self):
        # initialize output files
        current_directory = os.path.dirname(os.path.realpath(__file__))
        output_directory = "outputs"
        search_filename = "ucs-search-" + str(self.id) + ".txt"
        solution_filename = "ucs-sol-" + str(self.id) + ".txt"
        search_file = open(os.path.join(current_directory, output_directory, search_filename), "w")
        solution_file = open(os.path.join(current_directory, output_directory, solution_filename), "w")

        start = time.time()
        execution_time = 0

        while True:
            if self.puzzle.is_end(self.open[0].board): # REACHED GOAL
                solution_file.write("Initial board configuration: " + self.puzzle.string_puzzle + "\n\n")
                solution_file.write(self.puzzle.stringify_board() + "\n")
                solution_file.write("Car fuel available: " + str(self.puzzle.fuel) + "\n")
                execution_time = round(time.time() - start, 4)
                solution_file.write(F'Runtime: {execution_time}s \n')
                current_node = self.open[0]
                search_file.write(str(current_node.f) + " " + str(current_node.g) + " " + str(current_node.h) + " " + current_node.string_puzzle)
                
                # compute solution path
                while True:
                    self.solution_path.append(current_node)
                    if current_node.parent == None: break
                    else: current_node = current_node.parent
                self.solution_path.reverse()
                self.solution_path.pop(0) # removes root node from solution path

                # write solutions to file
                solution_file.write("Search path length: " + str(len(self.closed)) + " states\n")
                solution_file.write("Solution path length: " + str(len(self.solution_path)) + " moves\n")
                solution_file.write("Solution path: ")
                for node in self.solution_path:
                    solution_file.write(node.car + " " + node.action + " " + str(node.moves) + "; ")
                solution_file.write("\n\n")
                for node in self.solution_path:
                    solution_file.write(node.car + " " + node.action + " " + str(node.moves) + "             " + str(node.fuel[node.car]) + " " + node.string_puzzle + "\n")
                solution_file.write("\n")
                solution_file.write(self.puzzle.stringify_board(self.open[0].string_puzzle))
                break
            else:
                # removes this node from the open list if list contains another similar state of lower or same cost
                if self.has_lower_cost_in_open(self.open[0]) or self.open[0].string_puzzle in self.visited:
                    self.open.pop(0)
                    if len(self.open) == 0: # no solution can be found
                        execution_time = round(time.time() - start, 4)
                        solution_file.write("no solution")
                        break
                    continue

                children = self.generate_all_children_ucs(self.open[0]) # generate all unvisited children

                # add children to visit to open
                for child in children:
                    self.open.append(child)

                # sort open by lowest g
                self.open.sort(key=attrgetter('g'))

                # close current node
                visited_node = self.open.pop(0)
                self.closed.append(visited_node)
                self.visited.append(visited_node.string_puzzle)

                # add searched node to search file
                current_search = str(visited_node.f) + " " + str(visited_node.g) + " " + str(visited_node.h) + " " + visited_node.string_puzzle
                search_file.write(current_search + "\n")

                if len(self.open) == 0: # no solution can be found
                    execution_time = round(time.time() - start, 4)
                    solution_file.write("no solution")
                    break
        search_file.close()
        solution_file.close() 
        return [len(self.solution_path), len(self.closed), execution_time]

    def generate_all_children_ucs(self, node: SearchNode):
        children = []
        for car in self.puzzle.cars:
            for action in self.ACTIONS:
                move_counter = 1
                while True:
                    child = self.puzzle.preview_action(car, action, move_counter, node.fuel, node.board)
                    if child == None: break # changes action for car if move is not valid
                    # adds new children (cost is always +1 no matter the distance)
                    # no heuristic in ucs (h = 0)
                    child_node = SearchNode(child[0], child[1], child[2], node, car, action, move_counter, (node.g + 1), 0)

                    is_parent_node = (child_node.string_puzzle == node.string_puzzle)
                    has_been_visited = (child_node.string_puzzle in self.visited)
                    if ((not is_parent_node) and # do not append parent
                        (not has_been_visited)): # has not already been visited
                        children.append(child_node) 
                    move_counter += 1
        node.set_children(children)
        return children
    
    def has_lower_cost_in_open(self, node: SearchNode):
        skip_first = True
        for open_node in self.open:
            # skips the first place (since this method is called from the first node in open always)
            # don't want to compare it to itself
            if skip_first:
                skip_first = False
                continue
            if (open_node.string_puzzle == node.string_puzzle) and (open_node.g <= node.g):
                return True
        return False
    
    def run(self):
        return self.uniform_cost_search()

class GBFSSearchTree:

    ACTIONS = ['up', 'right', 'down', 'left']

    def __init__(self, initial_state, puzzle_number):
        self.id = puzzle_number
        self.puzzle = RushHour(initial_state) # create puzzle instance
        self.root = SearchNode(self.puzzle.string_puzzle, self.puzzle.board, self.puzzle.fuel, None, None, None, None, 0, 0)  # set root node
        self.open = [self.root] # list of open nodes
        self.closed = [] # list of closed nodes
        self.visited = [] # list of visited puzzle strings states (for easier search)
        self.solution_path = [] # list of nodes in the solution path

    """
    Searches for puzzle solution with the GBFS search.
    Writes solution (if any) to solution file and search path to search file.
    Returns (as a list):
        Length of the solution (0 if no solution)
        Length of the Search Path
        Execution Time
        Cost of solution (None if no solution)
    """
    
    def GBFS(self, heuristic):
        # initialize output files
        current_directory = os.path.dirname(os.path.realpath(__file__))
        output_directory = "outputs"
        search_filename = "GBFS-h" + str(heuristic) + "-search-" + str(self.id) + ".txt"
        solution_filename = "GBFS-h" + str(heuristic) + "-sol-" + str(self.id) + ".txt"
        search_file = open(os.path.join(current_directory, output_directory, search_filename), "w")
        solution_file = open(os.path.join(current_directory, output_directory, solution_filename), "w")

        start = time.time()
        execution_time = 0

        while True:
            if self.puzzle.is_end(self.open[0].board): # REACHED GOAL
                solution_file.write("Initial board configuration: " + self.puzzle.string_puzzle + "\n\n")
                solution_file.write(self.puzzle.stringify_board() + "\n")
                solution_file.write("Car fuel available: " + str(self.puzzle.fuel) + "\n")
                execution_time = round(time.time() - start, 4)
                solution_file.write(F'Runtime: {execution_time}s \n')
                current_node = self.open[0]
                search_file.write(str(current_node.f) + " " + str(current_node.g) + " " + str(current_node.h) + " " + current_node.string_puzzle)
                
                # compute solution path
                while True:
                    self.solution_path.append(current_node)
                    if current_node.parent == None: break
                    else: current_node = current_node.parent
                self.solution_path.reverse()
                self.solution_path.pop(0) # removes root node from solution path
                

                # write solutions to file
                solution_file.write("Search path length: " + str(len(self.closed)) + " states\n")
                solution_file.write("Solution path length: " + str(len(self.solution_path)) + " moves\n")
                solution_file.write("Solution path: ")
                for node in self.solution_path:
                    solution_file.write(node.car + " " + node.action + " " + str(node.moves) + "; ")
                solution_file.write("\n\n")
                for node in self.solution_path:
                    solution_file.write(node.car + " " + node.action + " " + str(node.moves) + "             " + str(node.fuel[node.car]) + " " + node.string_puzzle + "\n")
                solution_file.write("\n")
                solution_file.write(self.puzzle.stringify_board(self.open[0].string_puzzle))
                break
            else:
                # removes this node from the open list if list contains another similar state of lower or same cost
                if self.is_in_open_GBFS(self.open[0]) or (self.open[0].string_puzzle in self.visited):
                    self.open.pop(0)
                    if len(self.open) == 0: # no solution can be found
                        execution_time = round(time.time() - start, 4)
                        solution_file.write("no solution")
                        break
                    continue

                children = self.generate_all_children_GBFS(self.open[0], heuristic) # generate all unvisited children

                # add children to visit to open
                for child in children:
                    self.open.append(child)

                # sort open by lowest h 
                self.open.sort(key=attrgetter('h'))

                # close current node
                visited_node = self.open.pop(0)
                self.closed.append(visited_node)
                self.visited.append(visited_node.string_puzzle)

                # add searched node to search file
                current_search = str(visited_node.f) + " " + str(visited_node.g) + " " + str(visited_node.h) + " " + visited_node.string_puzzle
                search_file.write(current_search + "\n")

                if len(self.open) == 0: # no solution can be found
                    execution_time = round(time.time() - start, 4)
                    solution_file.write("no solution")
                    break
        search_file.close()
        solution_file.close() 
        return [len(self.solution_path), len(self.closed), execution_time]

    def generate_all_children_GBFS(self, node: SearchNode, heuristic):
        children = []
        for car in self.puzzle.cars:
            for action in self.ACTIONS:
                move_counter = 1
                while True:
                    child = self.puzzle.preview_action(car, action, move_counter, node.fuel, node.board)
                    if child == None: break # changes action for car if move is not valid
                    # adds new children (cost is always +1 no matter the distance)
                    # no heuristic in ucs (h = 0)
                    child_node = SearchNode(child[0], child[1], child[2], node, car, action, move_counter, (node.g + 1), 0) 

                    # calculating h value
                    h_value = 0
                    if heuristic == 1:
                        h_value = self.h1_blocked_vehicles(child_node)
                    elif heuristic == 2:
                        h_value = self.h2_blocked_positions(child_node)
                    elif heuristic == 3:
                        h_value = self.h3_multiplier_blocked_vehicles(child_node)
                    elif heuristic == 4:
                        h_value = self.h4_open_positions(child_node)
                    elif heuristic == 5:
                        h_value = self.h5_sum_blocked_vehicles_and_positions(child_node)
                    child_node.set_h(h_value)

                    is_parent_node = (child_node.string_puzzle == node.string_puzzle)
                    has_been_visited = (child_node.string_puzzle in self.visited)
                    if ((not is_parent_node) and # do not append parent
                        (not has_been_visited)): # has not already been visited
                        children.append(child_node) 
                    move_counter += 1
        node.set_children(children)
        return children

    def is_in_open_GBFS(self, node: SearchNode):
        skip_first = True
        for open_node in self.open:
            # skips the first place (since this method is called from the first node in open always)
            # don't want to compare it to itself
            if skip_first:
                skip_first = False
                continue
            if (open_node.string_puzzle == node.string_puzzle) and (open_node.h <= node.h):
                return True
        return False
    
    def h1_blocked_vehicles(self, node: SearchNode):
        a_coordinates = self.puzzle.get_car_coordinates('A', node.board) # get coordinates of Ambulance (A)
        max_a_coordinate = max(a_coordinates,key=itemgetter(0))[0] # A's highest x-coordinate value
        blocked_pointer = max_a_coordinate + 1 # set pointer to right of max coordinate of A
        blocked_cars = [] # initialize empty list of blocked cars
        
        for x in range(blocked_pointer, 6):
            position = node.board[x][2]
            if (position not in blocked_cars) and (position != "."): 
                blocked_cars.append(position)
        return len(blocked_cars)

    def h2_blocked_positions(self, node: SearchNode):
        a_coordinates = self.puzzle.get_car_coordinates('A', node.board) # get coordinates of Ambulance (A)
        max_a_coordinate = max(a_coordinates,key=itemgetter(0))[0] # A's highest x-coordinate value
        blocked_pointer = max_a_coordinate + 1 # set pointer to right of max coordinate of A
        blocked_positions = [] # initialize empty list of blocked positions
        
        for x in range(blocked_pointer, 6):
            position = node.board[x][2]
            if (position != "."): 
                blocked_positions.append(position)
        return len(blocked_positions)
    
    def h3_multiplier_blocked_vehicles(self, node: SearchNode):
        a_coordinates = self.puzzle.get_car_coordinates('A', node.board) # get coordinates of Ambulance (A)
        max_a_coordinate = max(a_coordinates,key=itemgetter(0))[0] # A's highest x-coordinate value
        blocked_pointer = max_a_coordinate + 1 # set pointer to right of max coordinate of A
        blocked_cars = [] # initialize empty list of blocked cars
        
        for x in range(blocked_pointer, 6):
            position = node.board[x][2]
            if (position not in blocked_cars) and (position != "."): 
                blocked_cars.append(position)
        return 2 * len(blocked_cars)

    def h4_open_positions(self, node: SearchNode):
        a_coordinates = self.puzzle.get_car_coordinates('A', node.board) # get coordinates of Ambulance (A)
        max_a_coordinate = max(a_coordinates,key=itemgetter(0))[0] # A's highest x-coordinate value
        blocked_pointer = max_a_coordinate + 1 # set pointer to right of max coordinate of A
        open_counter = 0
        
        for x in range(blocked_pointer, 6):
            position = node.board[x][2]
            if (position == "."): open_counter += 1
        return open_counter
    
    def h5_sum_blocked_vehicles_and_positions(self, node: SearchNode):
        a_coordinates = self.puzzle.get_car_coordinates('A', node.board) # get coordinates of Ambulance (A)
        max_a_coordinate = max(a_coordinates,key=itemgetter(0))[0] # A's highest x-coordinate value
        blocked_pointer = max_a_coordinate + 1 # set pointer to right of max coordinate of A
        blocked_cars = [] # initialize empty list of blocked cars
        blocked_positions = [] # initialize empty list of blocked positions
        
        for x in range(blocked_pointer, 6):
            position = node.board[x][2]
            if (position not in blocked_cars) and (position != "."):
                blocked_cars.append(position)
            if (position != "."):
                blocked_positions.append(position)
        
        sum_blocked_cars_and_positions = len(blocked_cars) + len(blocked_positions)
        return sum_blocked_cars_and_positions

    def __reset__(self):
        self.open = [self.root]
        self.closed = []
        self.visited = []
        self.solution_path = []

    def run_GBFS(self, heuristic):
        results = self.GBFS(heuristic)
        self.__reset__()
        return results

class AlgorithmASearchTree:

    ACTIONS = ['up', 'right', 'down', 'left']

    def __init__(self, initial_state, puzzle_number):
        self.id = puzzle_number
        self.puzzle = RushHour(initial_state) # create puzzle instance
        self.root = SearchNode(self.puzzle.string_puzzle, self.puzzle.board, self.puzzle.fuel, None, None, None, None, 0, 0)  # set root node
        self.open = [self.root] # list of open nodes
        self.closed = [] # list of closed nodes
        self.visited = [] # list of visited puzzle strings states (for easier search)
        self.solution_path = [] # list of nodes in the solution path

    """
    Searches for puzzle solution with the Algorithm A/A* search.
    Writes solution (if any) to solution file and search path to search file.
    Returns (as a list):
        Length of the solution (0 if no solution)
        Length of the Search Path
        Execution Time
    """
    
    def algorithm_A(self, heuristic):
        # initialize output files
        current_directory = os.path.dirname(os.path.realpath(__file__))
        output_directory = "outputs"
        search_filename = "a-h" + str(heuristic) + "-search-" + str(self.id) + ".txt"
        solution_filename = "a-h" + str(heuristic) + "-sol-" + str(self.id) + ".txt"
        search_file = open(os.path.join(current_directory, output_directory, search_filename), "w")
        solution_file = open(os.path.join(current_directory, output_directory, solution_filename), "w")

        start = time.time()
        execution_time = 0

        while True:
            if self.puzzle.is_end(self.open[0].board): # REACHED GOAL
                solution_file.write("Initial board configuration: " + self.puzzle.string_puzzle + "\n\n")
                solution_file.write(self.puzzle.stringify_board() + "\n")
                solution_file.write("Car fuel available: " + str(self.puzzle.fuel) + "\n")
                execution_time = round(time.time() - start, 4)
                solution_file.write(F'Runtime: {execution_time}s \n')
                current_node = self.open[0]
                search_file.write(str(current_node.f) + " " + str(current_node.g) + " " + str(current_node.h) + " " + current_node.string_puzzle)
                
                # compute solution path
                while True:
                    self.solution_path.append(current_node)
                    if current_node.parent == None: break
                    else: current_node = current_node.parent
                self.solution_path.reverse()
                self.solution_path.pop(0) # removes root node from solution path

                # write solutions to file
                solution_file.write("Search path length: " + str(len(self.closed)) + " states\n")
                solution_file.write("Solution path length: " + str(len(self.solution_path)) + " moves\n")
                solution_file.write("Solution path: ")
                for node in self.solution_path:
                    solution_file.write(node.car + " " + node.action + " " + str(node.moves) + "; ")
                solution_file.write("\n\n")
                for node in self.solution_path:
                    solution_file.write(node.car + " " + node.action + " " + str(node.moves) + "             " + str(node.fuel[node.car]) + " " + node.string_puzzle + "\n")
                solution_file.write("\n")
                solution_file.write(self.puzzle.stringify_board(self.open[0].string_puzzle))
                break
            else:
                # removes this node from the open list if list contains another similar state of lower or same cost
                if self.has_lower_cost_in_open_algorithm_A(self.open[0]) or (self.open[0].string_puzzle in self.visited):
                    self.open.pop(0)
                    if len(self.open) == 0: # no solution can be found
                        execution_time = round(time.time() - start, 4)
                        solution_file.write("no solution")
                        break
                    continue

                children = self.generate_all_children_algorithm_A(self.open[0], heuristic) # generate all unvisited children

                # add children to visit to open
                for child in children:
                    self.open.append(child)

                # sort open by lowest f
                self.open.sort(key=attrgetter('f'))

                # close current node
                visited_node = self.open.pop(0)
                self.closed.append(visited_node)
                self.visited.append(visited_node.string_puzzle)

                # add searched node to search file
                current_search = str(visited_node.f) + " " + str(visited_node.g) + " " + str(visited_node.h) + " " + visited_node.string_puzzle
                search_file.write(current_search + "\n")

                if len(self.open) == 0: # no solution can be found
                    execution_time = round(time.time() - start, 4)
                    solution_file.write("no solution")
                    break
        search_file.close()
        solution_file.close() 
        return [len(self.solution_path), len(self.closed), execution_time]

    def generate_all_children_algorithm_A(self, node: SearchNode, heuristic):
        children = []
        for car in self.puzzle.cars:
            for action in self.ACTIONS:
                move_counter = 1
                while True:
                    child = self.puzzle.preview_action(car, action, move_counter, node.fuel, node.board)
                    if child == None: break # changes action for car if move is not valid
                    # adds new children (cost is always +1 no matter the distance)
                    child_node = SearchNode(child[0], child[1], child[2], node, car, action, move_counter, (node.g + 1), 0)

                    # calculating h value
                    h_value = 0
                    if heuristic == 1:
                        h_value = self.h1_blocked_vehicles(child_node)
                    elif heuristic == 2:
                        h_value = self.h2_blocked_positions(child_node)
                    elif heuristic == 3:
                        h_value = self.h3_multiplier_blocked_vehicles(child_node)
                    elif heuristic == 4:
                        h_value = self.h4_open_positions(child_node)
                    elif heuristic == 5:
                        h_value = self.h5_sum_blocked_vehicles_and_positions(child_node)
                    child_node.set_h(h_value)

                    is_parent_node = (child_node.string_puzzle == node.string_puzzle)
                    has_been_visited = (child_node.string_puzzle in self.visited)

                    if not is_parent_node and not has_been_visited:
                        children.append(child_node) 
                    move_counter += 1
        node.set_children(children)
        return children

    def has_lower_cost_in_open_algorithm_A(self, node: SearchNode):
        skip_first = True
        for open_node in self.open:
            # skips the first place (since this method is called from the first node in open always)
            # don't want to compare it to itself
            if skip_first:
                skip_first = False
                continue
            if (open_node.string_puzzle == node.string_puzzle) and (open_node.f <= node.f):
                return True
        return False
    
    def h1_blocked_vehicles(self, node: SearchNode):
        a_coordinates = self.puzzle.get_car_coordinates('A', node.board) # get coordinates of Ambulance (A)
        max_a_coordinate = max(a_coordinates,key=itemgetter(0))[0] # A's highest x-coordinate value
        blocked_pointer = max_a_coordinate + 1 # set pointer to right of max coordinate of A
        blocked_cars = [] # initialize empty list of blocked cars
        
        for x in range(blocked_pointer, 6):
            position = node.board[x][2]
            if (position not in blocked_cars) and (position != "."): 
                blocked_cars.append(position)
        return len(blocked_cars)

    def h2_blocked_positions(self, node: SearchNode):
        a_coordinates = self.puzzle.get_car_coordinates('A', node.board) # get coordinates of Ambulance (A)
        max_a_coordinate = max(a_coordinates,key=itemgetter(0))[0] # A's highest x-coordinate value
        blocked_pointer = max_a_coordinate + 1 # set pointer to right of max coordinate of A
        blocked_positions = [] # initialize empty list of blocked positions
        
        for x in range(blocked_pointer, 6):
            position = node.board[x][2]
            if (position != "."): blocked_positions.append(position)
        return len(blocked_positions)
    
    def h3_multiplier_blocked_vehicles(self, node: SearchNode):
        a_coordinates = self.puzzle.get_car_coordinates('A', node.board) # get coordinates of Ambulance (A)
        max_a_coordinate = max(a_coordinates,key=itemgetter(0))[0] # A's highest x-coordinate value
        blocked_pointer = max_a_coordinate + 1 # set pointer to right of max coordinate of A
        blocked_cars = [] # initialize empty list of blocked cars
        
        for x in range(blocked_pointer, 6):
            position = node.board[x][2]
            if (position not in blocked_cars) and (position != "."): 
                blocked_cars.append(position)
        return 2 * len(blocked_cars)

    def h4_open_positions(self, node: SearchNode):
        a_coordinates = self.puzzle.get_car_coordinates('A', node.board) # get coordinates of Ambulance (A)
        max_a_coordinate = max(a_coordinates,key=itemgetter(0))[0] # A's highest x-coordinate value
        blocked_pointer = max_a_coordinate + 1 # set pointer to right of max coordinate of A
        open_counter = 0
        
        for x in range(blocked_pointer, 6):
            position = node.board[x][2]
            if (position == "."): open_counter += 1
        return open_counter

    def h5_sum_blocked_vehicles_and_positions(self, node: SearchNode):
        a_coordinates = self.puzzle.get_car_coordinates('A', node.board) # get coordinates of Ambulance (A)
        max_a_coordinate = max(a_coordinates,key=itemgetter(0))[0] # A's highest x-coordinate value
        blocked_pointer = max_a_coordinate + 1 # set pointer to right of max coordinate of A
        blocked_cars = [] # initialize empty list of blocked cars
        blocked_positions = [] # initialize empty list of blocked positions
        
        for x in range(blocked_pointer, 6):
            position = node.board[x][2]
            if (position not in blocked_cars) and (position != "."):
                blocked_cars.append(position)
            if (position != "."):
                blocked_positions.append(position)
        
        sum_blocked_cars_and_positions = len(blocked_cars) + len(blocked_positions)
        return sum_blocked_cars_and_positions
    
    def __reset__(self):
        self.open = [self.root]
        self.closed = []
        self.visited = []
        self.solution_path = []

    def run_algorithm_A(self, heuristic):
        results = self.algorithm_A(heuristic)
        self.__reset__()
        return results

# Runner
if __name__ == '__main__':
    # 2.2 Dealing with input file
    # puzzles_file = open('sample-input.txt', 'r')
    puzzles_file = open('puzzles.txt', 'r') # Full 50 puzzles file
    lines = [line.strip() for line in puzzles_file.readlines() if line.strip()] # Removes empty lines
    RushHour.print_board
    puzzles_file.close()

    # Setting up csv file for data analysis
    analysis_header = ["Puzzle Number", "Algorithm", "Heuristic", "Length of the Solution", "Length of the Search Path", "Execution Time (in seconds)"]
    analysis_file = open('analysis.csv', 'w', encoding='UTF8', newline='')
    writer = csv.writer(analysis_file)
    writer.writerow(analysis_header)

    puzzle_counter = 1
    for line in lines:
        if not line.startswith('#'): # skips over comment lines
            try:
                # UCS
                ucs_search = UCSSearchTree(line.split(), puzzle_counter)
                ucs_results = ucs_search.run()
                ucs_data = [puzzle_counter, "UCS", "N/A"] + ucs_results
                writer.writerow(ucs_data)

                # GBFS
                GBFS_search = GBFSSearchTree(line.split(), puzzle_counter)
                GBFS_h1_results = GBFS_search.run_GBFS(1)
                GBFS_h1_data = [puzzle_counter, "GBFS", "h1"] + GBFS_h1_results
                GBFS_h2_results = GBFS_search.run_GBFS(2)
                GBFS_h2_data = [puzzle_counter, "GBFS", "h2"] + GBFS_h2_results
                GBFS_h3_results = GBFS_search.run_GBFS(3)
                GBFS_h3_data = [puzzle_counter, "GBFS", "h3"] + GBFS_h3_results
                GBFS_h4_results = GBFS_search.run_GBFS(4)
                GBFS_h4_data = [puzzle_counter, "GBFS", "h4"] + GBFS_h4_results
                GBFS_h5_results = GBFS_search.run_GBFS(5)
                GBFS_h5_data = [puzzle_counter, "GBFS", "h5"] + GBFS_h5_results
                writer.writerow(GBFS_h1_data)
                writer.writerow(GBFS_h2_data)
                writer.writerow(GBFS_h3_data)
                writer.writerow(GBFS_h4_data)
                writer.writerow(GBFS_h5_data)

                # A
                algorithm_a_search = AlgorithmASearchTree(line.split(), puzzle_counter)
                algorithm_a_h1_results = algorithm_a_search.run_algorithm_A(1)
                algorithm_a_h1_data = [puzzle_counter, "Algorithm A", "h1"] + algorithm_a_h1_results
                algorithm_a_h2_results = algorithm_a_search.run_algorithm_A(2)
                algorithm_a_h2_data = [puzzle_counter, "Algorithm A", "h2"] + algorithm_a_h2_results
                algorithm_a_h3_results = algorithm_a_search.run_algorithm_A(3)
                algorithm_a_h3_data = [puzzle_counter, "Algorithm A", "h3"] + algorithm_a_h3_results
                algorithm_a_h4_results = algorithm_a_search.run_algorithm_A(4)
                algorithm_a_h4_data = [puzzle_counter, "Algorithm A", "h4"] + algorithm_a_h4_results
                algorithm_a_h5_results = algorithm_a_search.run_algorithm_A(5)
                algorithm_a_h5_data = [puzzle_counter, "Algorithm A", "h5"] + algorithm_a_h5_results
                writer.writerow(algorithm_a_h1_data)
                writer.writerow(algorithm_a_h2_data)
                writer.writerow(algorithm_a_h3_data)
                writer.writerow(algorithm_a_h4_data)
                writer.writerow(algorithm_a_h5_data)

            except ValueError:
                print("Puzzle #" + str(puzzle_counter) + " is not configured properly")
            except Exception as e: print(e)
            puzzle_counter += 1
    analysis_file.close()
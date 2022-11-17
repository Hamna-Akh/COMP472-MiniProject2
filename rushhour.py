from operator import itemgetter

class RushHour:
    """
    RushHour class represents an 6x6 rush-hour type puzzle. ...
    """

    ACTIONS = ['up', 'right', 'down', 'left']

    def __init__(self, p):
        self.fuel = {}
        self.list = None
        self.board = [['.','.','.','.','.','.'],
                      ['.','.','.','.','.','.'],
                      ['.','.','.','.','.','.'],
                      ['.','.','.','.','.','.'],
                      ['.','.','.','.','.','.'],
                      ['.','.','.','.','.','.']]
        self.initialize_game(p)

    # initialize the state of the game
    def initialize_game(self, p):
        self.list = p[0]

        # set the game board according to the list
        list_index = 0
        for y in range(0, 6):
            for x in range(0, 6):
                self.board[x][y] = self.list[list_index]
                if (self.board[x][y] not in self.fuel) and (self.board[x][y] != '.'):
                    self.fuel[self.board[x][y]] = 100
                list_index += 1

        # modify fuel levels if provided
        if len(p) > 1:
            for fuel_info in p[1:]:
                car = fuel_info[0]
                fuel_amount = int(fuel_info[1:])
                self.fuel[car] = fuel_amount
    
    # draw the board
    def draw_board(self):
        print()
        for y in range(0, 6):
            for x in range(0, 6):
                print(F'{self.board[x][y]}', end="")
            print()
        print()

    # validates move
    def is_valid(self, car, action, moves):
        # invalid inputs
        if ((car not in self.fuel) or 
            (action not in self.ACTIONS) or
            (not str(moves).isdigit()) or (moves < 1)):
            return False

        if self.fuel[car] < moves: # car has insufficient fuel
            return False

        # get car coordinates on board
        car_coordinates = []
        for y in range(0, 6):
            for x in range(0, 6):
                if self.board[x][y] == car: car_coordinates.append((x, y))

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
                if self.board[coordinate[0]][coordinate[1] - i] != '.':
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
                if self.board[coordinate[0] + i][coordinate[1]] != '.':
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
                if self.board[coordinate[0]][coordinate[1] + i] != '.':
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
                if self.board[coordinate[0] - i][coordinate[1]] != '.':
                    return False

        return True


# Runner
if __name__ == '__main__':
    # 2.2 Dealing with input file
    puzzles_file = open('sample-input.txt', 'r')
    lines = [line.strip() for line in puzzles_file.readlines() if line.strip()] # Removes empty lines
    puzzles_file.close()

    for line in lines:
        if not line.startswith('#'): # skips over comment lines
            game = RushHour(line.split())
            # game.draw_board()
            # print(game.is_valid('L', 'right', 1))

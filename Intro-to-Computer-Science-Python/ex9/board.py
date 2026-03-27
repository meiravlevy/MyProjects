#################################################################
# FILE : board.py
# WRITER : Meirav Levy , meiravlevy
# EXERCISE : intro2cs2 ex9 2021
# DESCRIPTION: A simple program that will create a class Board
# STUDENTS I DISCUSSED THE EXERCISE WITH:
# WEB PAGES I USED: Stack OverFlow
# NOTES: ...
#################################################################


class Board:
    """
    This class initializes a board game with cars and changes it according to
    the cars moves.
    """
    BOARD_SIZE = 7

    def __init__(self):
        """A constructor for a Board object"""
        self.__board = [[None for _ in range(Board.BOARD_SIZE)] for _ in
                        range(Board.BOARD_SIZE)]
        self.__board[3].append(None)
        self.__target_location = (3, 7)
        self.__cars = dict()
        self.__car_moves = ["u", "d", "l", "r"]

    def __str__(self):
        """
        This function is called when a board object is to be printed.
        :return: A string of the current status of the board
        """
        board_display = list()
        for row in range(Board.BOARD_SIZE):
            for col in range(Board.BOARD_SIZE):
                val = self.__board[row][col]
                if val is None:
                    board_display.append("_ ")
                else:
                    board_display.append(val)
                    board_display.append(" ")
            if row == 3:
                board_display.append("E\n")
            else:
                board_display.append("*\n")
        return "".join(board_display)

    def cell_list(self):
        """ This function returns the coordinates of cells in this board
        :return: list of coordinates
        """
        cells_coords = [(row, col) for row in range(Board.BOARD_SIZE)
                        for col in range(len(self.__board[row]))]
        return cells_coords

    def is_move_legal(self, car, move_key):
        """
        This method checks if the car can move in he given direction.
        :param car: Car object
        :param move_key: Key of move in car to check if legal
        :return: True if move is legal. False otherwise
        """
        if move_key not in car.possible_moves().keys():
            return False
        for coord in car.movement_requirements(move_key):
            row = coord[0]
            col = coord[1]
            if row == 3 and col == 7:
                continue
            if row < 0 or row > 6 or col < 0 or col > 6:
                return False
            if self.cell_content(coord) is not None:
                return False
        return True

    def possible_moves(self):
        """ This function returns the legal moves of all cars in this board
        :return: list of tuples of the form (name,movekey,description) 
                 representing legal moves
        """
        legal_moves = list()
        for car in self.__cars.values():
            for move_key in self.__car_moves:
                if self.is_move_legal(car, move_key):
                    car_name = car.get_name()
                    move_description = car.possible_moves()[move_key]
                    legal_moves.append((car_name, move_key, move_description))
        return legal_moves

    def target_location(self):
        """
        This function returns the coordinates of the location which is to be filled for victory.
        :return: (row,col) of goal location
        """
        return self.__target_location

    def cell_content(self, coordinate):
        """
        Checks if the given coordinates are empty.
        :param coordinate: tuple of (row,col) of the coordinate to check
        :return: The name if the car in coordinate, None if empty
        """
        row, col = coordinate[0], coordinate[1]
        if self.__board[row][col] is None:
            return None
        return self.__board[row][col]

    def is_adding_car_valid(self, car):
        """This function return False if the car coordinates are not in the
        limits of the board or if there is a car in the board with the same
        name"""
        for row in self.__board:
            if car.get_name() in row:
                return False
        for coord in car.car_coordinates():
            row = coord[0]
            col = coord[-1]
            if row < 0 or row > 6 or col < 0 or col > 6:
                if row == 3 and col == 7:
                    continue
                return False
            if self.cell_content(coord) is not None:
                return False

    def add_car(self, car):
        """
        Adds a car to the game.
        :param car: car object of car to add
        :return: True upon success. False if failed
        """
        if self.is_adding_car_valid(car) is False:
            return False
        self.__cars[car.get_name()] = car
        for coord in car.car_coordinates():
            self.__board[coord[0]][coord[1]] = car.get_name()
        return True

    def change_board_arrangement(self, car, name=None):
        """
        this method wither removes a car from the board or adds its new
        location to the board
        :param car: The car that we want to remove or add to the board
        :param name: The name of the car. None if we are removing a car.
        """
        for coord in car.car_coordinates():
            row = coord[0]
            col = coord[1]
            self.__board[row][col] = name

    def move_car(self, name, movekey):
        """
        moves car one step in given direction.
        :param name: name of the car to move
        :param movekey: Key of move in car to activate
        :return: True upon success, False otherwise
        """
        if name not in self.__cars.keys():
            return False
        car = self.__cars[name]
        if self.is_move_legal(car, movekey) is False:
            return False
        self.change_board_arrangement(car)
        car.move(movekey)
        self.__cars[name] = car
        self.change_board_arrangement(car, name)
        return True

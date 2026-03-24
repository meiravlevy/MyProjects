#################################################################
# FILE : car.py
# WRITER : Meirav Levy , meiravlevy
# EXERCISE : intro2cs2 ex9 2021
# DESCRIPTION: A simple program that will create a class Car
# STUDENTS I DISCUSSED THE EXERCISE WITH:
# WEB PAGES I USED: Stack OverFlow
# NOTES: ...
#################################################################


class Car:
    """
    This class creates a car.
    """
    def __init__(self, name, length, location, orientation):
        """
        A constructor for a Car object
        :param name: A string representing the car's name
        :param length: A positive int representing the car's length.
        :param location: A tuple representing the car's head (row, col) location
        :param orientation: One of either 0 (VERTICAL) or 1 (HORIZONTAL)
        """
        self.__name: str = name
        self.__length: int = length
        self.__location = location
        self.__orientation: int = orientation
        self.__distance_to_move = 1

    def set_distance_to_move(self, distance):
        """
        this function sets the distance that the car can move to a different
        one than the default which is 1.
        :param distance: The new distance.
        """
        self.__distance_to_move = distance

    def car_coordinates(self):
        """
        :return: A list of the car's coordinates
        """
        coords = list()
        car_head_row, car_head_col = self.__location[0], self.__location[1]
        if self.__orientation == 0:  # if car is vertical
            for row in range(car_head_row, car_head_row + self.__length):
                coords.append((row, car_head_col))
        else:
            for col in range(car_head_col, car_head_col + self.__length):
                coords.append((car_head_row, col))
        return coords

    def possible_moves(self):
        """
        :return: A dictionary of strings describing possible movements permitted by this car.
        """
        possible_moves = dict()
        if self.__orientation == 0:
            possible_moves["u"] = "Cause the car to go up"
            possible_moves["d"] = "Cause the car to go down"
        elif self.__orientation == 1:
            possible_moves["r"] = "Cause the car to go right"
            possible_moves["l"] = "Cause the car to go left"
        return possible_moves

    def movement_requirements(self, movekey):
        """ 
        :param movekey: A string representing the key of the required move.
        :return: A list of cell locations which must be empty in order for this move to be legal.
        """
        required_move_cells = list()
        if movekey == "d" and self.__orientation == 0:
            required_move_cells.append((self.car_coordinates()[-1][0] +
                                        self.__distance_to_move,
                                        self.car_coordinates()[-1][1]))
        elif movekey == "u" and self.__orientation == 0:
            required_move_cells.append((self.__location[0] -
                                        self.__distance_to_move,
                                        self.__location[1]))
        elif movekey == "r" and self.__orientation == 1:
            required_move_cells.append((self.car_coordinates()[-1][0],
                                        self.car_coordinates()[-1][1] +
                                        self.__distance_to_move))
        elif movekey == "l" and self.__orientation == 1:
            required_move_cells.append((self.__location[0],
                                        self.__location[1] -
                                        self.__distance_to_move))
        return required_move_cells

    def move(self, movekey):
        """ 
        :param movekey: A string representing the key of the required move.
        :return: True upon success, False otherwise
        """
        if movekey not in self.possible_moves():
            return False
        if movekey == "u" or movekey == "l":
            self.__location = self.movement_requirements(movekey)[0]
        elif movekey == "d" or movekey == "r":
            self.__location = self.car_coordinates()[1]
        return True

    def get_name(self):
        """
        :return: The name of this car.
        """
        return self.__name

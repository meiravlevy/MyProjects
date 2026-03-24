#################################################################
# FILE : game.py
# WRITER : Meirav Levy , meiravlevy
# EXERCISE : intro2cs2 ex9 2021
# DESCRIPTION: A simple program that will create a class game
# STUDENTS I DISCUSSED THE EXERCISE WITH:
# WEB PAGES I USED: Stack OverFlow
# NOTES: ...
#################################################################

import car
import board
import sys
import helper


class Game:
    """
    This class creates the game Rush Hour.
    """

    def __init__(self, board):
        """
        Initialize a new Game object.
        :param board: An object of type board
        """
        self.__game_board = board
        self.__target_coord = self.__game_board.target_location()

    def __single_turn(self):
        """
        Note - this function is here to guide you and it is *not mandatory*
        to implement it. 

        The function runs one round of the game :
            1. Get user's input of: what color car to move, and what 
                direction to move it.
            2. Check if the input is valid.
            3. Try moving car according to user's input.

        Before and after every stage of a turn, you may print additional 
        information for the user, e.g., printing the board. In particular,
        you may support additional features, (e.g., hints) as long as they
        don't interfere with the API.
        """
        pass

    def is_input_legal(self, users_chars):
        """This method checks if the input given by the user is legal."""
        if len(users_chars) != 3 or \
                users_chars[0] not in CARS_LEGAL_NAMES or \
                users_chars[1] != "," or users_chars[2] not in LEGAL_MOVES:
            return False
        return True

    def play(self):
        """
        The main driver of the Game. Manages the game until completion.
        :return: None
        """
        print(self.__game_board)
        while True:
            users_move = input()
            if users_move == "!":
                break
            users_chars = list(users_move)
            if self.is_input_legal(users_chars) is False:
                print("Illegal move! please try again.")
                continue
            name, direction = users_move[0], users_move[2]
            if not self.__game_board.move_car(name, direction):
                print("Illegal move! please try again.")
                continue
            else:
            # if self.__game_board.move_car(name, direction):
                print(self.__game_board)
            if self.__game_board.cell_content(self.__target_coord) is not None:
                break
        return


if __name__ == "__main__":
    cars_dict = helper.load_json(sys.argv[1])
    game_board = board.Board()
    CARS_LEGAL_NAMES = ["Y", "B", "O", "G", "R"]
    LEGAL_MOVES = ["d", "u", "r", "l"]
    for car_name, value in cars_dict.items():
        if car_name not in CARS_LEGAL_NAMES:
            continue
        car_length = value[0]
        if car_length > 4 or car_length < 2:
            continue
        car_location = tuple(value[1])
        car_orientation = value[2]
        car_to_board = car.Car(car_name, car_length, car_location,
                               car_orientation)
        game_board.add_car(car_to_board)
    game = Game(game_board)
    game.play()





#################################################################
# FILE : puzzle_solver.py
# WRITER : Meirav Levy , meiravlevy
# EXERCISE : intro2cs2 ex8 2021
# DESCRIPTION: A simple program that solves a puzzle.
# STUDENTS I DISCUSSED THE EXERCISE WITH:
# WEB PAGES I USED: Stack OverFlow
# NOTES: ...
#################################################################


from typing import List, Tuple, Set, Optional, Any, Union


# We define the types of a partial picture and a constraint (for type checking).
Picture = List[List[int]]
Constraint = Tuple[int, int, int]
Black_cells = Union[Tuple[int], Tuple[int, int]]


def sum_seen_cells_col(picture: Picture, col_coord: int,
                       black_cells: Black_cells, start: int, end: int,
                       step: int = 1) -> int:
    """This function will go over all the rows with the specified column and
    sum up all the cells that are white or unknown until reaching a black
    cell"""
    seen_cells = 0
    for ind in range(start, end, step):
        if picture[ind][col_coord] in black_cells:
            break
        seen_cells += 1
    return seen_cells


def sum_seen_cells_row(picture: Picture, row_coord: int,
                       black_cells: Black_cells, start: int, end: int,
                       step: int = 1) -> int:
    """This function will go over all the columns with the specified row and
        sum up all the cells that are white or unknown until reaching a black
        cell"""
    seen_cells = 0
    for ind in range(start, end, step):
        if picture[row_coord][ind] in black_cells:
            break
        seen_cells += 1
    return seen_cells


def count_total_seen_cells(black_cells: Black_cells, picture: Picture,
                           row: int, col: int) -> int:
    """This Function will count all the seen cells from a specified cell"""
    total_seen_cells: int = 0
    if picture[row][col] in black_cells:
        return total_seen_cells
    total_seen_cells += sum_seen_cells_row(picture, row, black_cells, col,
                                           len(picture[0]))
    total_seen_cells += sum_seen_cells_row(picture, row, black_cells, col - 1,
                                           -1, -1)
    total_seen_cells += sum_seen_cells_col(picture, col, black_cells, row + 1,
                                           len(picture))
    total_seen_cells += sum_seen_cells_col(picture, col, black_cells, row - 1,
                                           -1, -1)
    return total_seen_cells


def max_seen_cells(picture: Picture, row: int, col: int) -> int:
    """This function will sum up all the seen cells from the cell coords given
    to the function. unknown cells will be considered as white cells"""
    black_cells: Tuple[int] = (0, )
    return count_total_seen_cells(black_cells, picture, row, col)


def min_seen_cells(picture: Picture, row: int, col: int) -> int:
    """This function will sum up all the seen cells from the cell coords given
    to the function. unknown cells will be considered as black cells"""
    black_cells: Tuple[int, int] = (0, -1)
    return count_total_seen_cells(black_cells, picture, row, col)


def is_constraint_valid(picture: Picture, row: int, col: int,
                        constraint_val: int, temp_success: int) -> int:
    """This function will check if a constraint can exist in the picture."""
    if constraint_val > max_seen_cells(picture, row, col) or \
            constraint_val < min_seen_cells(picture, row, col):
        temp_success = 0
    elif max_seen_cells(picture, row, col) != \
            min_seen_cells(picture, row, col):
        temp_success = 2
    return temp_success


def check_constraints(picture: Picture, constraints_set: Set[Constraint]) -> \
        int:
    """This function will check if a set of constraints is valid in the
    picture. will return 0 if one of the constraints is invalid, 1 if all the
    constraints have only one way to exist in the picture and 2 otherwise"""
    temp_success: int = 1
    for constraint in constraints_set:
        temp_success = is_constraint_valid(picture, constraint[0],
                                           constraint[1], constraint[2],
                                           temp_success)
        if temp_success == 0:
            break
    return temp_success


def solve_puzzle(constraints_set: Set[Constraint], n: int, m: int) -> \
        Optional[Picture]:
    """
    :param constraints_set: The constraints on the puzzle
    :param n: The number of rows
    :param m: The number of columns
    :return: None if there is no solution for the puzzle and the solved puzzle
    otherwise.
    """
    board: List[List[int]] = [[-1] * m for _ in range(n)]
    solution: Optional[Picture] = _puzzle_helper(board, constraints_set, 0)
    return solution


def _puzzle_helper(board: List[list[int]], constraints_set: Set[Constraint],
                   ind: int) -> Any:
    """This function will try to solve a puzzle and return one of the
    solutions if there is at least one."""
    if ind == len(board) * len(board[0]):
        return True
    row, col = ind // len(board[0]), ind % len(board[0])
    for value in range(2):
        board[row][col] = value
        if check_constraints(board, constraints_set) != 0:
            if _puzzle_helper(board, constraints_set, ind + 1):
                return board
    board[row][col] = -1


def how_many_solutions(constraints_set: Set[Constraint], n: int, m: int) \
        -> int:
    """This function will check how many solutions are for a given puzzle"""
    board = [[-1] * m for _ in range(n)]
    return _num_solutions_helper(board, constraints_set, 0)


def _num_solutions_helper(board: List[list[int]],
                          constraints_set: Set[Constraint], ind: int) -> int:
    """This function will count the amount of valid solutions for the given
    board."""
    total_solutions: int = 0
    if ind == len(board) * len(board[0]):
        return 1

    row, col = ind // len(board[0]), ind % len(board[0])
    for value in range(2):
        board[row][col] = value
        if check_constraints(board, constraints_set) != 0:
            total_solutions += _num_solutions_helper(board, constraints_set,
                                                     ind + 1)
        board[row][col] = -1
    return total_solutions


def generate_puzzle(picture: Picture) -> Set[Constraint]:
    """This function will return a constraint set that creates only one
    solution for the puzzle"""
    constraints = set()
    for row in range(len(picture)):
        for col in range(0, len(picture[0]), 2):
            if how_many_solutions(constraints, len(picture), len(picture[0])) \
                    == 1:
                break
            seen_cells = count_total_seen_cells((0, ), picture, row, col)
            constraints.add((row, col, seen_cells))
    return constraints

#################################################################
# FILE : ex7.py
# WRITER : Meirav Levy , meiravlevy
# EXERCISE : intro2cs2 ex7 2021
# DESCRIPTION: A simple program that will use recursion to solve problems
# STUDENTS I DISCUSSED THE EXERCISE WITH:
# WEB PAGES I USED:
# NOTES: ...
#################################################################


import ex7_helper
from typing import Any, List


def mult(x: float, y: int) -> float:
    """This function will return the product of 2 numbers"""
    if y == 0:
        return 0
    return ex7_helper.add(x, mult(x, ex7_helper.subtract_1(y)))


def is_even(n: int) -> bool:
    """This function will check if a number is even."""
    if n == 0:
        return True
    elif n == 1:
        return False
    n = ex7_helper.subtract_1(n)
    return is_even(ex7_helper.subtract_1(n))


def log_mult(x: float, y: int) -> float:
    """This function will multiply 2 numbers in a complexity of O(log(n))"""
    if y == 0:
        return 0
    half_num_mult: float = log_mult(x, ex7_helper.divide_by_2(y))
    if not ex7_helper.is_odd(y):
        return ex7_helper.add(half_num_mult, half_num_mult)
    else:
        return ex7_helper.add(ex7_helper.add(half_num_mult, half_num_mult), x)


def do_and_check_power(b: int, x: int, num_to_mult: int) -> bool:
    """This function will check if the number <x> is the power of the number
    <num_to_mult> by multiplying the <num_to_mult> and checking each time
    if it is equal to <x> or greater than <x>"""
    if b == x:
        return True
    elif b > x:
        return False
    b = int(log_mult(b, num_to_mult))
    return do_and_check_power(b, x, num_to_mult)


def is_power(b: int, x: int) -> bool:
    """This function will check if the number <x> is the power of the number
    <b>"""
    if x == 1:
        return True
    if b <= 1:
        return False
    num_to_mult: int = b
    return do_and_check_power(b, x, num_to_mult)


def make_reversed_str(s: str, new_s: str) -> str:
    """
    :param s: the string we want to reverse
    :param new_s: the string reversed
    :return: new_s
    """
    if len(new_s) == len(s):
        return new_s
    return make_reversed_str(s, ex7_helper.append_to_end(new_s,
                                                      s[-len(new_s) - 1]))


def reverse(s: str) -> str:
    """This function will return the string reversed."""
    new_s: str = ""
    return make_reversed_str(s, new_s)


def play_hanoi(hanoi: Any, n: int, src: Any, dst: Any, temp: Any) -> None:
    """This function will play the hanoi tower game."""
    if n <= 0:
        return
    play_hanoi(hanoi, n - 1, src, temp, dst)
    hanoi.move(src, dst)
    play_hanoi(hanoi, n - 1, temp, dst, src)


def check_digit_one(n: int, sum: int) -> int:
    """This function will check how many times the digit 1 is in a number."""
    if n < 1:
        return sum
    if n % 10 == 1:
        sum += 1
    return check_digit_one(n//10, sum)


def number_of_ones(n: int) -> int:
    """This function will go over all the numbers between 1 to n and return
    the amount of times that the digit 1 appears in all the numbers."""
    sum: int = 0
    if n < 1:
        return sum
    return check_digit_one(n, sum) + number_of_ones(n - 1)


def compare_1d_lists(lst1: List[int], lst2: List[int], n: int) -> bool:
    """
    :param lst1: a 1d list
    :param lst2: a 1d list
    :param n: the last index of both lists. will help with recursion on the
    index.
    :return: True if the lists are in the same length and have the same values.
    False otherwise.
    """
    if len(lst1) != len(lst2):
        return False
    elif n < 0:
        return True
    else:
        return lst1[n] == lst2[n] and \
               compare_1d_lists(lst1, lst2, n - 1)


def go_over_2d_lists(n: int, l1: List[List[int]], l2: List[List[int]]) -> bool:
    """This function will go over each element in two 2D lists and check
    if they are the same."""
    if n < 0:
        return True
    return compare_1d_lists(l1[n], l2[n],
                            len(l2[n]) - 1) and go_over_2d_lists(
        n - 1, l1, l2)


def compare_2d_lists(l1: List[List[int]], l2: List[List[int]]) -> bool:
    """This function will compare two 2D lists and return True if they are
    in hte same length and have the exact same values. The function will
    return False otherwise."""
    if len(l1) != len(l2):
        return False
    last_ind_2d: int = len(l1) - 1
    return go_over_2d_lists(last_ind_2d, l1, l2)


def create_seq(new_lst: List[Any], last_elem: List[Any],
                        last_elem_length: int) -> List[Any]:
    """This function will create a sequence of lists"""
    if last_elem_length == 0:
        new_lst.append(last_elem[:])
        return new_lst
    new_lst.append(last_elem[-last_elem_length][:])
    return create_seq(new_lst, last_elem, last_elem_length - 1)


def magic_list(n: int) -> List[Any]:
    """this function will return the n element in a sequence of lists"""
    if n == 0:
        return []
    last_elem: List[Any] = magic_list(n - 1)[:]
    last_elem_length: int = len(last_elem)
    new_lst: List[Any] = []
    create_seq(new_lst, last_elem, last_elem_length)
    return new_lst

#################################################################
# FILE : largest_and_smallest.py
# WRITER : Meirav Levy , meiravlevy
# EXERCISE : intro2cs2 ex2 2020
# DESCRIPTION: A simple program that checks which number out of 3 numbers
#              is smallest and which is the largest
# STUDENTS I DISCUSSED THE EXERCISE WITH:
# WEB PAGES I USED:
# NOTES: in the function check_largest_and_smallest I chose to check the case
#        where all the numbers are equal because I wanted to see if it will
#        give me  two of the same number (one for largest and one for smallest)
#        and not one.
#        I chose also to check the case where there are float numbers and
#        negative numbers, in order to see that the function doesn't give me
#        a positive number as the smallest number and to check that the
#        function knows how to work with floats and doesn't give me an error.
#################################################################


def largest_and_smallest(num1, num2, num3):
    """
    This function takes 3 numbers and returns the largest number and the
    smallest number.
    """
    largest = 0 #will have the value of the largest number
    smallest = 0 #will have the value of the smallest number
    if num1 >= num2:
        largest = num1
        smallest = num2
    elif num2 > num1:
        largest = num2
        smallest = num1
    if num3 >= largest:
        largest = num3
    elif num3 <= smallest:
        smallest = num3
    return largest, smallest


def check_largest_and_smallest():
    """
    This function checks that the function largest_and_smallest works correctly
    by checking a few edge cases and returning True if all of them gave the
    correct answer, and False otherwise
    """
    if largest_and_smallest(17, 1, 6) != (17, 1):
        return False
    if largest_and_smallest(1, 17, 6) != (17, 1):
        return False
    if largest_and_smallest(1, 1, 2) != (2, 1):
        return False
    if largest_and_smallest(1, 1, 1) != (1, 1):
        return False
    if largest_and_smallest(3.25, -2, 1) != (3.25, -2):
        return False
    return True

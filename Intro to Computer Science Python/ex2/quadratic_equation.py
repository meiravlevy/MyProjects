#################################################################
# FILE : quadratic_equation.py
# WRITER : Meirav Levy , meiravlevy
# EXERCISE : intro2cs2 ex2 2020
# DESCRIPTION: A simple program that calculates a quadratic equation according
#              to the user's input of coefficients.
# STUDENTS I DISCUSSED THE EXERCISE WITH:
# WEB PAGES I USED:
# NOTES: ...
#################################################################
import math


def quadratic_equation(a, b, c):
    """
    This function takes 3 coefficients and calculates the quadratic equation
    with those coefficients
    """
    inside_sqrt = b**2 - 4*a*c
    if inside_sqrt < 0:
        return None, None
    elif inside_sqrt == 0:
        x1 = (-b + math.sqrt(inside_sqrt)) / (2*a)
        return x1, None
    else:
        x1 = (-b + math.sqrt(inside_sqrt)) / (2*a)
        x2 = (-b - math.sqrt(inside_sqrt)) / (2*a)
        return x1, x2


def quadratic_equation_user_input():
    """
    This function asks from the user for 3 coefficients and returns the
    result of the quadratic equation with those coefficients.
    """
    users_input = input("Insert coefficients a, b, and c: ")
    coefficients = users_input.split()
    a, b, c = float(coefficients[0]), float(coefficients[1]),\
              float(coefficients[2])
    if a == 0:
        print("The parameter 'a' may not equal 0")
    else:
        result1, result2 = quadratic_equation(a, b, c)
        if result2 == None:
            if result1 == None:
                print("The equation has no solutions")
            else:
                print("The equation has 1 solution: " + str(result1))
        else:
             print("The equation has 2 solutions: " + str(result1) + " and "
             + str(result2))

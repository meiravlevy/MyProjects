#################################################################
# FILE : calculate_mathematical_expression.py
# WRITER : Meirav Levy , meiravlevy
# EXERCISE : intro2cs2 ex2 2020
# DESCRIPTION: A simple program that calculates different math expressions.
# STUDENTS I DISCUSSED THE EXERCISE WITH:
# WEB PAGES I USED:
# NOTES: ...
#################################################################


def calculate_mathematical_expression(num1, num2, operator):
    """This function will take two numbers and an operator and calculate
    their mathematical expression"""
    if operator == "+":
        return num1 + num2
    elif operator == "-":
        return num1 - num2
    elif operator == "*":
        return num1 * num2
    elif operator == ":" and num2 != 0:
        return num1 / num2
    else:
        return None


def calculate_from_string(math_expression):
    """
    This function will take a math expression as a string, split it into 2
    numbers and an operator and calculate the math expression.
    """
    split_express = math_expression.split()
    num1, operator, num2 = split_express[0], split_express[1], split_express[2]
    result = calculate_mathematical_expression(float(num1), float(num2),
                                               operator)
    return result










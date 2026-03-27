#################################################################
# FILE : shapes.py
# WRITER : Meirav Levy , meiravlevy
# EXERCISE : intro2cs2 ex2 2020
# DESCRIPTION: A simple program that asks from the user rto pick a shape and
#              size of the radius/ side, and returns the shape's area
# STUDENTS I DISCUSSED THE EXERCISE WITH:
# WEB PAGES I USED:
# NOTES: ...
#################################################################
import math


def circle_area():
    """
    This function asks from the user for a circle's radius and calculates the
    circle's area with that radius
    """
    radius = float(input())
    return math.pi * math.pow(radius, 2)


def rectangle_area():
    """
    This function asks from the user for 2 sides of a rectangle and calculates
    the rectangle's area.
    """
    side1 = float(input())
    side2 = float(input())
    return side1 * side2


def equilateral_triangle_area():
    """
    This function asks from the user for an equilateral triangle's side and
    calculates the equilateral triangle's area.
    """
    side = float(input())
    return (math.sqrt(3)/4) * math.pow(side, 2)


def shape_area():
    """
    This function asks from the user to pick a shape, and returns the shape's
    area
    """
    shape_choice = input("Choose shape (1=circle, 2=rectangle, 3=triangle): ")
    if shape_choice != "1" and shape_choice != "2" and shape_choice != "3":
        return None
    elif shape_choice == "1":
        return circle_area()
    elif shape_choice == "2":
        return rectangle_area()
    else:
        return equilateral_triangle_area()

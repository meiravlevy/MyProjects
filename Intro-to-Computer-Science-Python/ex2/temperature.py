#################################################################
# FILE : temperature.py
# WRITER : Meirav Levy , meiravlevy
# EXERCISE : intro2cs2 ex2 2020
# DESCRIPTION: A simple program that will return True if in 2 out of 3 days
#              the temeprature was higher than the temperature's limit,
#              and will return False otherwise.
# STUDENTS I DISCUSSED THE EXERCISE WITH:
# WEB PAGES I USED:
# NOTES: ...
#################################################################


def is_vormir_safe(temp_limit, temp_day1, temp_day2, temp_day3):
    """
    This function will return True if in 2 out of 3 days the temeprature was
    higher than the temperature's limit, and will return False otherwise.
    """
    if temp_day1 > temp_limit and temp_day2 > temp_limit:
        return True
    elif temp_day1 > temp_limit and temp_day3 > temp_limit:
        return True
    elif temp_day2 > temp_limit and temp_day3 > temp_limit:
        return True
    else:
        return False

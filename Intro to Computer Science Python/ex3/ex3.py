#################################################################
# FILE : ex3.py
# WRITER : Meirav Levy , meiravlevy
# EXERCISE : intro2cs2 ex3 2020
# DESCRIPTION: A simple program that sums numbers, does different calculations
#              on vectors, checks monotonicity of a sequence and checks prime
#              numbers
# STUDENTS I DISCUSSED THE EXERCISE WITH:
# WEB PAGES I USED:
# NOTES: ...
#################################################################


def input_list():
    """This function asks from the user to type numbers. The function
       sums them up and returns a list with all the numbers and their summary
       which is the last element of the list."""
    list_of_nums = []
    sum = 0
    user_typed_num = input()
    if user_typed_num == "":
        list_of_nums.append(0)
        return list_of_nums
    while True:
        user_typed_num = float(user_typed_num)
        list_of_nums.append(user_typed_num)
        sum += user_typed_num
        user_typed_num = input()
        if user_typed_num == "":
            break
    list_of_nums.append(sum)
    return list_of_nums


def inner_product(vec_1, vec_2):
    """This function calculates and returns the inner product of 2 vectors."""
    if len(vec_1) != len(vec_2):
        return None
    sum_of_products = 0
    for ind in range(len(vec_1)):
        sum_of_products += vec_1[ind] * vec_2[ind]
    return sum_of_products


def sequence_monotonicity(sequence):
    """This function checks the monoticity of a sequence and returns a list
       of booleans showing if the function is: incresing, strictly increasing,
       decreasing, strictly decreasing"""
    is_monotonic_list = [True] * 4
    if sequence == []:
        return is_monotonic_list
    for ind in range(1, len(sequence)):
        if sequence[ind] > sequence[ind - 1]: #Strictly increasing
            is_monotonic_list[2], is_monotonic_list[3] = False, False
        elif sequence[ind] < sequence[ind - 1]: #Strictly decreasing
            is_monotonic_list[0], is_monotonic_list[1] = False, False
        elif sequence[ind] == sequence[ind -1]: #increasing/decreasing
            is_monotonic_list[1], is_monotonic_list[3] = False, False
    return is_monotonic_list


def monotonicity_inverse(def_bool):
    """This function returns an example for a sequence that fulfill the
       requirements of monotonicity in the list given. if there is no sequence
       that can be created, the function will return None"""
    list_of_monotonicity = []
    for index in range(len(def_bool)):
        #the next few lines will create a new list that includes  the indexes
        #in the list that have the value of True in them.
        if def_bool[index] == True:
            list_of_monotonicity.append(index)
    if list_of_monotonicity == []: #not monotone
        return [1, 2, 2, 1]
    elif list_of_monotonicity == [0]: #only increasing
        return [1, 2, 2, 2]
    elif list_of_monotonicity == [0, 1]: #strictly increasing
        return [1,2,3,4]
    elif list_of_monotonicity == [0, 2]: #increasing and decreasing
        return [1, 1, 1, 1]
    elif list_of_monotonicity == [2]: #decreasing
        return [2, 1, 1, 1]
    elif list_of_monotonicity == [2, 3]: #strictly decreasing
        return [4, 3, 2, 1]
    return None


def is_prime(suspect_prime):
    """This function checks if a number is prime."""
    for divisor in range(3, int(suspect_prime**(1/2)) + 1, 2):
        if suspect_prime % divisor == 0:
            return False
    return True


def primes_for_asafi(n):
    """This function returns a list with the n first prime numbers."""
    if n == 0:
        return []
    list_of_primes = [2]
    suspect_prime = 3
    while len(list_of_primes) < n:
        if is_prime(suspect_prime):
            list_of_primes.append(suspect_prime)
        suspect_prime += 2
    return list_of_primes


def sum_of_vectors(vec_lst):
    """This function will sum all the vectors in the list and return a new
    vector that is the sum of all those vectors."""
    if vec_lst == []:
        return None
    inner_vectors_len = len(vec_lst[0])
    sum_vec = []
    for index in range(inner_vectors_len):
        sum = 0
        for inner_vector in vec_lst:
            sum += inner_vector[index]
        sum_vec.append(sum)
    return sum_vec



def num_of_orthogonal(vectors):
    """This function will return the number of vectors that are orthogonal
    to each other"""
    num_of_orth_vec = 0
    for ind in range(len(vectors)):
        for index in range(ind + 1, len(vectors)):
            if inner_product(vectors[ind], vectors[index]) == 0:
                num_of_orth_vec += 1
    return num_of_orth_vec

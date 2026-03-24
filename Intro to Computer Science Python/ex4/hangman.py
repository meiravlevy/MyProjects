#################################################################
# FILE : hangman.py
# WRITER : Meirav Levy , meiravlevy
# EXERCISE : intro2cs2 ex2 2021
# DESCRIPTION: A simple program that runs games of hangman.
# STUDENTS I DISCUSSED THE EXERCISE WITH:
# WEB PAGES I USED: Stackoverflow
# NOTES: ...
#################################################################
import hangman_helper


def update_word_pattern(word, pattern, letter):
    """This function takes the word and the pattern and updates the pattern
    to a pattern that includes the letter in all places that the word includes
    the letter."""
    list_of_pattern = list(pattern)
    for index, let in enumerate(word):
        if let == letter:
            list_of_pattern[index] = letter
    updated_pattern = "".join(list_of_pattern)
    return updated_pattern


def validity_of_letter(guess, wrong_guess_list, pattern):
    """Checks if the user typed a valid letter and returns a message
    if he didn't"""
    if len(guess) > 1 or guess.islower() == False or guess.isalpha() == False:
        msg = "The letter you entered is invalid."
        return msg
    elif guess in wrong_guess_list or guess in pattern:
        msg = "The letter you entered was already chosen."
        return msg
    return True


def update_score(score, num_of_right_letters):
    """updates the playesr's score according to his guess"""
    score += (num_of_right_letters * (num_of_right_letters + 1)) // 2
    return score


def update_guess_of_letter(score, guess, WORD_TO_GUESS, pattern,
                           wrong_guess_lst):
    """This function will update the current state according to the guess of
    the letter"""
    score -= 1
    if guess in WORD_TO_GUESS:
        num_of_right_letters = WORD_TO_GUESS.count(guess)
        score = update_score(score, num_of_right_letters)
        pattern = update_word_pattern(WORD_TO_GUESS, pattern,
                                      guess)
        message = "yay!!! you guessed a letter in the word!"
    else:
        wrong_guess_lst.append(guess)
        message = "This letter isn't in the word."
    return score, pattern, wrong_guess_lst, message


def is_lett_in_wrong_guess_list(letter, wrong_guess_list):
    """This function checks if lwtter is in the wrong guess list"""
    if letter in wrong_guess_list:
        return True
    return False


def is_word_valid(pattern, word, wrong_guess_list):
    """This function checks if the pattern has the same letters in the same
    indexes as the word does."""
    if len(pattern) != len(word):
        return False
    for index, pattern_letter in enumerate(pattern):
        if pattern_letter != "_":
           if pattern_letter != word[index]:
               return False
           if pattern.count(pattern_letter) != word.count(pattern_letter):
               return False
        if is_lett_in_wrong_guess_list(word[index], wrong_guess_list):
            return False
    return True


def filter_words_list(words, pattern, wrong_guess_list):
    """This function checks what words in the list of words have the potential
    of being the word to guess and returns a list of those words"""
    valid_words_for_hint = []
    for word in words:
        if not is_word_valid(pattern, word, wrong_guess_list):
            continue
        valid_words_for_hint.append(word)
    return valid_words_for_hint


def hint_words(valid_words_for_hint):
    """This function will return a new list of hints in the length of
    HINT_LENGTH"""
    lst_of_hint_length_words = []
    VALID_WORDS_LST_LENGTH = len(valid_words_for_hint)
    if VALID_WORDS_LST_LENGTH >= hangman_helper.HINT_LENGTH:
        for index in range(hangman_helper.HINT_LENGTH):
            word_for_new_list = valid_words_for_hint[
                (index * VALID_WORDS_LST_LENGTH) // 3]
            lst_of_hint_length_words.append(word_for_new_list)
    else:
        lst_of_hint_length_words = valid_words_for_hint
    return lst_of_hint_length_words


def display_end_of_game(score, pattern, WORD_TO_GUESS, wrong_guess_lst):
    """This function diplays the state in the end of the game."""
    if score < 1:
        message = "You lost the game. The word was: " + WORD_TO_GUESS
    else:
        num_of_right_letters = pattern.count("_")
        score = update_score(score, num_of_right_letters)
        pattern = WORD_TO_GUESS
        message = "you won the game!"
    hangman_helper.display_state(pattern, wrong_guess_lst, score,
                                 message)
    return score



def run_single_game(word_list, score):
    """This function runs one game og hangman"""
    WORD_TO_GUESS = hangman_helper.get_random_word(word_list)
    print(WORD_TO_GUESS) #Delete after
    pattern = "_" * len(WORD_TO_GUESS)
    wrong_guess_lst = []
    message = "Let's play hangman!"
    while "_" in pattern and score > 0:
        hangman_helper.display_state(pattern, wrong_guess_lst, score,
                                         message)
        type_of_guess, guess = hangman_helper.get_input()
        if type_of_guess == hangman_helper.LETTER:
            is_letter_valid = validity_of_letter(guess, wrong_guess_lst,
                                                     pattern)
            if is_letter_valid != True:
                message = is_letter_valid
            else:
                score, pattern, wrong_guess_lst, message = \
                    update_guess_of_letter(score, guess, WORD_TO_GUESS,
                                            pattern, wrong_guess_lst)
        elif type_of_guess == hangman_helper.WORD:
            score -= 1
            if guess == WORD_TO_GUESS:
                break
            else:
                message = "That is not the correct word."
        else:
            score -= 1
            valid_words_for_hint = filter_words_list(word_list,
                                                     pattern, wrong_guess_lst)
            lst_of_hint_length_words = hint_words(valid_words_for_hint)
            hangman_helper.show_suggestions(lst_of_hint_length_words)
    return(display_end_of_game(score, pattern, WORD_TO_GUESS,
                                    wrong_guess_lst))


def init_game(LST_OF_WORDS_TO_GUESS):
    """This Function intializes the number of games and total score and runs
    a single game"""
    num_of_games = 0
    total_score = hangman_helper.POINTS_INITIAL
    last_game_score = run_single_game(LST_OF_WORDS_TO_GUESS,
                                      total_score)
    return last_game_score, num_of_games


def msg_for_play_again(last_game_score, num_of_games):
    """This function returns a message for the function play_again in
    hangman_helper according to the score of the last game."""
    if last_game_score == 0:
        msg = "Number of games survived: " + str(num_of_games) + \
              ". Start a new series of games? "
    else:
        msg = "Number of games so far: " + str(num_of_games) + \
            ". total score: " + str(last_game_score) + ". Want to continue ? " \
            "Enter 'y' or 'Y' for YES, 'n' or 'N' for NO"
    return msg


def main():
    """This function runs as many games of hangman as the user wants."""
    LST_OF_WORDS_TO_GUESS = hangman_helper.load_words()
    last_game_score, num_of_games = init_game(LST_OF_WORDS_TO_GUESS)
    while True:
        num_of_games += 1
        if last_game_score == 0:
            meessage = msg_for_play_again(last_game_score, num_of_games)
            if hangman_helper.play_again(meessage) == False:
                return
            last_game_score, num_of_games = init_game(LST_OF_WORDS_TO_GUESS)
        else:
            meessage = msg_for_play_again(last_game_score, num_of_games)
            if hangman_helper.play_again(meessage) == False:
                return
            last_game_score = run_single_game(LST_OF_WORDS_TO_GUESS,
                                              last_game_score)


if __name__ == '__main__':
   main()

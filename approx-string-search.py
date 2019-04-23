"""
COMP90049 Knowledge Technologies - Project 1
Name: Emmanuel Macario <macarioe>
Student Number: 831659
"""
# Import useful libraries
from ctypes import *
from collections import defaultdict


# Cython SENTDEX Tutorial
# https://www.youtube.com/watch?v=mXuEoqK4bEc

# WORDSname constants
MISSPELL_WORDS = 'misspell.txt'
DICT_WORDS = 'dict.txt'
CORRECT_WORDS = 'correct.txt'


"""
TODO: Process each unique s
"""


def main():
    # Store dictionary words as a set
    dictionary = set()
    with open(DICT_WORDS) as f:
        for word in f:
            word = word.strip()
            dictionary.add(word)

    # Get unique misspelled tokens
    unique_misspelled = set()
    with open(MISSPELL_WORDS) as f:
        for word in f:
            word = word.strip()
            unique_misspelled.add(word)

    # Extract the 'gold standard', storing all of the 'correct'
    # words each unique 'misspelled' word can be corrected to
    with open(MISSPELL_WORDS) as misspell, open(CORRECT_WORDS) as correct:
        gold_standard = defaultdict(set)
        for m, c in zip(misspell, correct):
            m = m.strip()
            c = c.strip()
            gold_standard[m].add(c)
    print(len(gold_standard))

    # DEBUGGING
    """
    for m in gold_standard:
        if len(gold_standard[m]) > 1:
            print("{:12s}:".format(m) + ' ' + str(gold_standard[m]))
    """

    # Load the shared object file
    edit_distance = CDLL('./edit_distance.so')

    # Create byte objects from the strings
    b_m = "gily".encode('utf-8')
    b_d = "geely".encode('utf-8')



    m1 = "honda"
    d1 = "hyundai"

    r = edit_distance.levenshtein(m1.encode('utf-8'), d1.encode('utf-8'));
    print(r)

    m = "julie".encode('utf-8')
    total = 0
    for word in dictionary:
        d = word.encode('utf-8')
        r = edit_distance.levenshtein(m, d)
        total += 1
    print("Total dict words:", total)


def print_interesting():
    """
    Prints some stats about how many words in 'correct.txt'
    are not in 'dict.txt', which would lower precision/recall
    """
    dict_set = set()
    with open(DICT_WORDS) as f:
        for word in f:
            dict_set.add(word.strip())

    # print(len(dict_set))

    with open(CORRECT_WORDS) as f:
        unique_correct = set()
        not_in_dict = 0
        total = 0

        unique_not_in_dict = set()
        for word in f:
            word = word.strip()
            unique_correct.add(word)
            if word not in dict_set:
                unique_not_in_dict.add(word)
                not_in_dict += 1
            total += 1

        print("Not in dict:", not_in_dict)
        print("Total:", total)
        print("Unique not in dict:", len(unique_not_in_dict))

        n = 0
        for word in unique_correct:
            if word not in dict_set:
                n += 1
        print("Total unique 'correct' words not in 'dict':", n)


def print_stats():
    with open(MISSPELL_WORDS) as f:
        words = []
        count = 0
        for word in f:
            words.append(word.strip())
            count += 1

        print("Total mispelled words:", len(words))
        print("Count:", count)
        print("Total unique mispelled words:", len(set(words)))
        unique_words = set(words)

    print()

    with open(DICT_WORDS) as f:
        dict_words = []
        count = 0
        for word in f:
            dict_words.append(word.strip())
            count += 1

        print("Total dict words:", len(dict_words))
        print("Count:", count)
        print("Total unique dict words:", len(set(dict_words)))

    with open(CORRECT_WORDS) as f:
        correct_words = []
        count = 0
        for word in f:
            correct_words.append(word.strip())
            count += 1

        unique_correct_words = set(correct_words)
        print("\nTotal correct words:", count)
        print("Total unique correct words:", len(unique_correct_words))


if __name__ == "__main__":
    main()
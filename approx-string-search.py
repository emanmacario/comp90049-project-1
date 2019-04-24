"""
COMP90049 Knowledge Technologies - Project 1
Name: Emmanuel Macario <macarioe>
Student Number: 831659
"""
# Import useful libraries
from ctypes import *
from collections import defaultdict
import math
import nltk
import json


# Cython SENTDEX Tutorial
# https://www.youtube.com/watch?v=mXuEoqK4bEc

# Filename constants
MISSPELL_WORDS = 'misspell.txt'
DICT_WORDS = 'dict.txt'
CORRECT_WORDS = 'correct.txt'


def main2():
    with open('levenshtein.json') as f:
        results = json.load(f)
        print(results['thirsty'])


def main():
    dictionary = get_dictionary(DICT_WORDS)
    unique_misspelled = get_unique_misspelled(MISSPELL_WORDS)

    # Extract the 'gold standard', storing all of the 'correct'
    # words each unique 'misspelled' word can be corrected to
    with open(MISSPELL_WORDS) as misspell, open(CORRECT_WORDS) as correct:
        gold_standard = []
        for m, c in zip(misspell, correct):
            m = m.strip()
            c = c.strip()
            gold_standard.append((m, c))

    # Load the shared object file
    edit_distance = CDLL('./edit_distance.so')

    # For every unique misspelled word, get the best match(es)
    # according to the specific edit distance function
    results = {}
    total = 0
    LIMIT = 10
    for misspelled in sorted(unique_misspelled):

        # Debugging
        # if total >= LIMIT:
        #    break

        matches = []
        lowest = math.inf
        results[misspelled] = {'distance': lowest, 'matches': matches}

        # Convert strings to byte objects
        b_misspelled = misspelled.encode('utf-8')

        for word in dictionary:
            b_word = word.encode('utf-8')

            # Calculate Levenshtein distance
            distance = edit_distance.levenshtein(b_misspelled, b_word)

            if distance == lowest:
                matches.append(word)
            elif distance < lowest:
                lowest = distance
                results[misspelled]['distance'] = lowest
                matches.clear()
                matches.append(word)
        total += 1

        if total % 75 == 0:
            print("Total of {:4d}/{:4d} unique misspelled words processed".format(total, len(unique_misspelled)))

    # Store results in a JSON file
    with open('levenshtein.json', 'x') as fp:
        json.dump(results, fp, indent=4)


def get_dictionary(file):
    # Store dictionary words as a set
    dictionary = set()
    with open(file) as f:
        for word in f:
            word = word.strip()
            dictionary.add(word)
    return dictionary


def get_unique_misspelled(file):
    # Get unique misspelled tokens
    unique_misspelled = set()
    with open(file) as f:
        for word in f:
            word = word.strip()
            unique_misspelled.add(word)
    return unique_misspelled


if __name__ == "__main__":
    main()


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



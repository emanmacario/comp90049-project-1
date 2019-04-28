"""
COMP90049 Knowledge Technologies - Project 1
Name: Emmanuel Macario <macarioe>
Student Number: 831659
"""
# Import useful libraries
from ctypes import *
from collections import defaultdict
from itertools import groupby, islice
import math
import ngram
import json

# Filename constants
MISSPELL_WORDS = 'misspell.txt'
DICT_WORDS = 'dict.txt'
CORRECT_WORDS = 'correct.txt'

# Results filenames
LEVENSHTEIN_JSON = 'levenshtein.json'
DAMERAU_LEVENSHTEIN_JSON = 'damerau-levenshtein.json'
DAMERAU_LEVENSHTEIN_BIGRAM_JSON = 'damerau-levenshtein-bigram.json'


def compare_results():
    with open(LEVENSHTEIN_JSON) as f1, open(DAMERAU_LEVENSHTEIN_JSON) as f2:
        rl = json.load(f1)
        rdl = json.load(f2)

    len_matches = 0
    exact_matches = 0
    subset_counts = 0
    for word in rl:
        l_matches = set(rl[word]['matches'])
        dl_matches = set(rdl[word]['matches'])
        if len(l_matches) == len(dl_matches):
            len_matches += 1
            if l_matches == dl_matches:
                exact_matches += 1
        else:
            if l_matches.issubset(dl_matches):
                subset_counts += 1
            print("=" * 200)
            print("Word: '{:s}'".format(word))
            print("Levenshtein         :", sorted(l_matches))
            print("Minimum distance    :", rl[word]['distance'])
            print("Damerau-Levenshtein :", sorted(dl_matches))
            print("Minimum distance    :", rdl[word]['distance'])
            print("Set Difference      :", dl_matches.difference(l_matches))

    print("Length matches :", len_matches)
    print("Exact matches  :", exact_matches)
    print("Total keys     :", len(rl))
    print("Percentage same:", (len_matches / len(rl)))
    print("Total different:", (len(rl) - len_matches))
    print("Subset counts  :", subset_counts)


def ngram_similarity():
    # Break ties in DLD via bi-gram similarity
    unique_misspelled = get_unique_misspelled(MISSPELL_WORDS)

    with open(DAMERAU_LEVENSHTEIN_JSON) as f:
        results = json.load(f)

    for misspell in unique_misspelled:
        matches = results[misspell]['matches']
        results[misspell]['matches'] = break_ties(misspell, matches)

    with open('damerau-levenshtein-bigram.json', 'x') as fp:
        json.dump(results, fp, indent=4, sort_keys=True)


def break_ties(misspell, matches):
    G = ngram.NGram(matches)
    filtered = groupby(G.search(misspell), lambda x: x[1])
    filtered_matches = []
    for score, group in islice(filtered, 0, 1):
        for word in group:
            filtered_matches.append(word[0])

    return sorted(filtered_matches)


def compare_metrics():
    gold_standard = get_gold_standard()
    with open(LEVENSHTEIN_JSON) as f1, open(DAMERAU_LEVENSHTEIN_JSON) as f2:
        rl = json.load(f1)
        rdl = json.load(f2)

    ld_only = set()
    dld_only = set()
    for misspell, correct in gold_standard:
        ld_matches = set(rl[misspell]['matches'])
        dld_matches = set(rdl[misspell]['matches'])

        if correct in ld_matches and correct not in dld_matches:
            ld_only.add((misspell, correct))

        if correct not in ld_matches and correct in dld_matches:
            dld_only.add((misspell, correct))
    print("LD only:", ld_only)
    print("DLD only:", dld_only)


def analyse_results(results_file):
    print("=" * 50)
    print("Analysing:", results_file)

    # Load JSON results files into dicts
    with open(results_file) as f:
        results = json.load(f)

    # Convert lists to sets for both dicts for faster search
    for word in results:
        results[word]['matches'] = set(results[word]['matches'])

    # Calculate precision/recall
    gold_standard = get_gold_standard()
    total_correct = 0
    total_returned = 0
    for misspell, correct in gold_standard:
        matches = results[misspell]['matches']
        if correct in matches:
            total_correct += 1
        total_returned += len(matches)

    precision = total_correct / total_returned
    recall = total_correct / len(gold_standard)

    print("Total keys in results:", len(results))
    print("Total pairs in gold standard:", len(gold_standard))
    print("Precision  : {:.10f}".format(precision))
    print("Recall     : {:.10f}".format(recall))
    print("Avg Matches: {:.10f}".format(total_returned / len(gold_standard)))
    print("=" * 50)


def lexical_normalisation():
    dictionary = get_dictionary(DICT_WORDS)
    unique_misspelled = get_unique_misspelled(MISSPELL_WORDS)

    # Load the shared object file
    edit_distance = CDLL('./edit_distance.so')

    # For every unique misspelled word, get the best match(es)
    # according to the specific edit distance function
    results = {}
    total = 0
    LIMIT = float('inf')
    for misspelled in sorted(unique_misspelled):

        # Debugging
        if total >= LIMIT:
            break

        matches = []
        lowest = math.inf
        results[misspelled] = {'distance': lowest, 'matches': matches}

        # Convert strings to byte objects
        b_misspelled = misspelled.encode('utf-8')

        for word in dictionary:
            b_word = word.encode('utf-8')

            # Calculate Levenshtein distance
            distance = edit_distance.damerau_levenshtein(b_misspelled, b_word)

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
    with open('damerau-levenshtein.json', 'x') as fp:
        json.dump(results, fp, indent=4, sort_keys=True)


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


def get_gold_standard():
    # Extract the 'gold standard', storing all of the 'correct'
    # words each unique 'misspelled' word can be corrected to
    with open(MISSPELL_WORDS) as misspell, open(CORRECT_WORDS) as correct:
        gold_standard = []
        for m, c in zip(misspell, correct):
            m = m.strip()
            c = c.strip()
            gold_standard.append((m, c))

    return gold_standard


def write_gold_standard():
    gold_standard = get_gold_standard()
    with open('gold-standard.csv', 'x') as fp:
        for misspell, correct in gold_standard:
            fp.write(str(misspell) + ',' + str(correct) + '\n')


def main():
    # Compare results
    # compare_results()
    # Analyse the results
    #analyse_results(LEVENSHTEIN_JSON)
    #analyse_results(DAMERAU_LEVENSHTEIN_JSON)
    #analyse_results(DAMERAU_LEVENSHTEIN_BIGRAM_JSON)
    # ngram_similarity()
    compare_metrics()


if __name__ == "__main__":
    main()

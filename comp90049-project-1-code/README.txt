COMP90049 Knowledge Technologies
Project 1 - Code README
Name: Emmanuel Macario <macarioe>
Student Number: 831659

This zip file contains a program written in Python 3 to predict the best matches
for each misspelled word in 'misspell.txt', with respect to the reference
dictionary 'dict.txt'. The edit-distance similarity metrics are written in C,
compiled and imported into Python for efficiency.

To use the program, simply replace the code in the main()
function with either calls to the analysis functions, or the lexical normalisaton
functions.

External Code Sources:
 - https://en.wikibooks.org/wiki/Algorithm_Implementation/Strings/Levenshtein_distance#C
 - https://gist.github.com/badocelot/5331587
 - https://github.com/gpoulter/python-ngram

Requirements:
    - ngram
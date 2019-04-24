/**
 * Levenshtein Distance algorithm optimized to use O(min(m,n)) space instead of O(mn). The key observation is
 * that we only need to access the contents of the previous column when filling the matrix column-by-column.
 * Hence, we can re-use a single column over and over, overwriting its contents as we proceed.
 *
 * Source: https://en.wikibooks.org/wiki/Algorithm_Implementation/Strings/Levenshtein_distance#C
 */
#include <stdlib.h>
#include <stdio.h>
#include <string.h>

#define MIN3(a, b, c) ((a) < (b) ? ((a) < (c) ? (a) : (c)) : ((b) < (c) ? (b) : (c)))

int levenshtein(char *s1, char *s2) {
    unsigned int s1len, s2len, x, y, lastdiag, olddiag;
    s1len = strlen(s1);
    s2len = strlen(s2);
    unsigned int column[s1len+1];
    for (y = 1; y <= s1len; y++)
        column[y] = y;
    for (x = 1; x <= s2len; x++) {
        column[0] = x;
        for (y = 1, lastdiag = x-1; y <= s1len; y++) {
            olddiag = column[y];
            column[y] = MIN3(column[y] + 1, column[y-1] + 1, lastdiag + (s1[y-1] == s2[x-1] ? 0 : 1));
            lastdiag = olddiag;
        }
    }
    return(column[s1len]);
}



// Damerau-Levenshtein edit distance implementation in C99
//
// Based on pseudocode from Wikipedia: <https://en.wikipedia.org/wiki/Damerau-Levenshtein_distance>
// and on my Python implementation: <https://gist.github.com/badocelot/5327337>
//
// Source: https://gist.github.com/badocelot/5331587
int damerau_levenshtein_distance(const char *source, const char *target)
{
    // Size of the strings and dimensions of the matrix
    int m = 0;
    if (source != NULL)
        m = strlen(source);

    int n = 0;
    if (target != NULL)
        n = strlen(target);

    // If either is NULL or of zero length, there's no real work to be done: the
    // cost is just the length of the other.
    if (m == 0)
        return n;
    if (n == 0)
        return m;

    // Set up the table
    int **matrix = (int**) malloc ((m + 2) * sizeof (int*));
    if (matrix == NULL)
        abort();

    for (int i = 0; i < m + 2; i++)
    {
        matrix[i] = (int*) malloc ((n + 2) * sizeof (int));

        if (matrix[i] == NULL)
            abort();
    }

    // Initialize the table similar to Wagner-Fischer, with an extra row and
    // column with higher-than-possible costs to prevent erroneous detection of
    // transpositions that would go outside the bounds of the strings.
    int INF = m + n;

    matrix[0][0] = INF;
    for (int i = 0; i <= m; i++)
    {
        matrix[i+1][1] = i;
        matrix[i+1][0] = INF;
    }
    for (int j = 0; j <= n; j++)
    {
        matrix[1][j+1] = j;
        matrix[0][j+1] = INF;
    }

    // This lets us store and look up the row where a given character last
    // appeared in `source` -- changing this to a map type might be useful if
    // GLib or a similar library is available to you.
    int *last_row = (int*) malloc (256 * sizeof (int));

    // Zero here denotes that the character has not be seen in `source yet,
    // because zero is the "infinity" column
    for (int d = 0; d < 256; d++)
        last_row[d] = 0;

    // Fill out the table
    for (int row = 1; row <= m; row++)
    {
        // The current character in `source`; this and `ch_t` below both have to
        // be unsigned so that they can be used as an index to last_row no
        // matter what their values
        unsigned char ch_s = source[row-1];

        // The last column this row where the character in `source` matched the
        // character in `target`; as with last_row, zero denotes no match yet
        int last_match_col = 0;

        for (int col = 1; col <= n; col++)
        {
            // The current character in `target`
            unsigned char ch_t = target[col-1];

            // The last place in `source` where we can find the current
            // character in `target`
            int last_matching_row = last_row[ch_t];

            int cost = (ch_s == ch_t) ? 0 : 1;

            // Calculate the distances of all possible operations
            int dist_add = matrix[row][col+1] + 1;
            int dist_del = matrix[row+1][col] + 1;
            int dist_sub = matrix[row][col] + cost;

            // This took me a while to figure out. What this calculates is the
            // cost of a transposition between the current character in `target`
            // and the last character found in both strings.
            //
            // All characters between these two are treated as either additions
            // or deletions.
            //
            // NOTE: Damerau-Levenshtein allows for either additions OR
            // deletions between the transposed characters, NOT both. This is
            // not explicitly prevented, but if both additions and deletions
            // would be required between transposed characters -- this is if
            // neither
            //
            //     `(row - last_matching_row - 1)`
            //
            // nor
            //
            //     `(col - last_match_rol - 1)`
            //
            // is zero -- then adding together both addition and deletion costs
            // will cause the total cost of a transposition to become higher
            // than any other operation's cost.
            int dist_trans = matrix[last_matching_row][last_match_col]
                             + (row - last_matching_row - 1) + 1
                             + (col - last_match_col - 1);

            // Find the minimum of the distances
            int min = dist_add;
            if (dist_del < min)
                min = dist_del;
            if (dist_sub < min)
                min = dist_sub;
            if (dist_trans < min)
                min = dist_trans;

            // Store the minimum as the cost for this cell
            matrix[row+1][col+1] = min;

            // If there was a match, update the last matching column
            if (cost == 0)
                last_match_col = col;
        }

        // Update the entry for this row's character
        last_row[ch_s] = row;
    }

    // Extract the bottom right-most cell -- that's the total distance
    int result = matrix[m+1][n+1];

    // Clean up
    for (int i = 0; i < m + 2; i++)
        free (matrix[i]);
    free (matrix);
    free (last_row);

    return result;
}
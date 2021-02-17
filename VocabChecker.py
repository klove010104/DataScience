# -*- coding: utf-8 -*-

"""Check a list of terms against a standard vocabulary.

The standard vocabulary is specified by an Excel with columns titled
'COLUMN BUSINESS NAME' and 'TABLE BUSINESS NAME'. The list of terms is 
an Excel with columns 'TABLE NAME' and 'COLUMN NAME'. 

  Typical usage example:

  results = run_vocab_match('ColumnsToMatch.xlsx', 70, 40 ) \n
  save_as_xl(results)

Created on Sun Feb 14 13:15:59 2021

@author: klove
"""

import pandas as pd
from fuzzywuzzy import process
import stringcase

# This file will be on a shared drive and refreshed periodically
MASTER_VOCAB_FILE_NAME = 'C:/Users/klove/Downloads/CoreAttributes.xlsx'
RESULT_FILE_NAME = 'Matched_Vocab.xlsx'

def load_xl_df(input_file_name):
    """Loads an Excel into a DataFrame.
    
        Assumes that either file is in current directory, or it's 
        fully qualified
    """
    df = pd.read_excel(input_file_name)
    return df

def save_as_xl(result_df, result_name=RESULT_FILE_NAME):
    """Saves DataFrame to Excel
    
    """    
    result_df.to_excel(result_name)

def get_target_vocab(df_column):
    """Creates a sorted, unique list of target words

    Retrieves rows pertaining to the given keys from the Table instance
    represented by table_handle.  String keys will be UTF-8 encoded.

    """
    tv = pd.unique(df_column)
    tv.sort()
    return tv

def preprocess_input_vocab(input_df):
    """Drops rows with no values, title cases words.

    """
    # TODO handle non-standard format
    input_df = input_df.dropna(subset=['COLUMN BUSINESS NAME'])

    # Standardize and add a column with the standardized names
    # TODO SettingWithCopyWarning
    input_df['ColumnNameStd'] = input_df['COLUMN BUSINESS NAME'].str.title()
    # also gives the warning. leaving as comment because lambda is handy
    # input_df['ColumnNameStd'] = input_df['COLUMN BUSINESS NAME'].apply(lambda x: x.title())
    return input_df
 
def create_input_vocab(input_file_name):
    """Returns unique list of target names to match against.

    """
    input_vocab_df = load_xl_df(input_file_name)
    input_vocab_df = preprocess_input_vocab(input_vocab_df)
    # use unique list for further processing
    target_names = get_target_vocab(input_vocab_df['ColumnNameStd'])
    return target_names


def match_to_target(inputword, target_names, threshold, max_matches):
    """Matches single word to vocabulary - returns list of tuples

    Uses fuzzy matching to compare a single word to a list of candidate 
    words, and returns the number of possible matches (limited by max 
    matches) scoring >= threshold.

    Args:
        inputword: the word to find a match for
        target_names: a list with the standard vocabulary
        threshold: an integer representing the lowest score for a match
        max_matches: an integer representing the most matches to keep

    Returns:
        A list of tuples representing the matches and their score, sorted 
        by score descending.
        Example:
            [ ('Aaron', 99), ('Aardvark', 75)]

    """
    matches = []
    score_col = 1
    for match in process.extract(inputword, target_names, limit=max_matches):
        if match[score_col] > threshold:
            matches.append(match)
    return matches    

# take input of match tuples, and return a tuple of the best match
# if multiple with top score, put word "multiple"
def get_top_match(matches):
    """From the list of matches, returns tuple of the highest score match.

    Assumes the list is sorted by match score descending. Returns the tuple 
    from the first row. If there are no matches, returns tuple 
    ('no matches', 0). If there are multiple matches with same top score, 
    returns tuple ('multiple matches', top score)

    """
    if len(matches) == 0:
        top_score = 0
        top_term = 'no matches'
    if len(matches) > 1:
        top_score = matches[0][1]
        top_term = matches[0][0]
        if matches[1][1] == top_score:
            top_term = 'multiple matches'
    return (top_term, top_score)

def match_vocab(inputDf, vocab, threshold, max_matches):
    """Matches each term in inputDf to standard vocab

    Loops through input and runs the match, then returns a dataframe with
    the results.

    Args:
        inputDf: the original dataframe loaded from user input
        vocab: the standardized vocabulary list
        threshold: an integer representing the lowest score for a match
        max_matches: an integer representing the most matches to keep

    Returns:
        outputDf: a dataframe with below columns:
            "Orig Table Name", "Orig Column Name","Best Match Term",
            "Best Match Score", "Top Matches"

    """
    term_matches = []
    output_df = pd.DataFrame(columns =
                             ["Orig Table Name", "Orig Column Name",
                              "Best Match Term","Best Match Score", 
                              "Top Matches" ] )

    for tbl, term in zip(inputDf['Table Name'],inputDf['Column Name']): 
        term_matches = match_to_target(term, vocab, threshold, max_matches);
        top_term_tuple = get_top_match(term_matches)
        values_to_add = {'Orig Table Name': tbl, 
                         'Orig Column Name': term, 
                         'Best Match Term': top_term_tuple[0], 
                         'Best Match Score': top_term_tuple[1], 
                         'Top Matches': term_matches}
        tname = stringcase.camelcase(stringcase.snakecase(term))
        row_to_add = pd.Series(values_to_add, name = tname)
        output_df = output_df.append(row_to_add)
    return output_df

# returns a dataframe with the matched values
def run_vocab_match(input_file_name, threshold, max_matches, 
                    vocab_file_name = MASTER_VOCAB_FILE_NAME):
    """Matches terms in an input file to a vocabulary and returns dataframe.

    Retrieves rows pertaining to the given keys from the Table instance
    represented by table_handle.  String keys will be UTF-8 encoded.

    Args:
        input_file_name: Excel with columns 'TABLE NAME' and 'COLUMN NAME'
        threshold: an integer representing the lowest score for a match
        max_matches: an integer representing the most matches to keep
        vocab: Excel with target terms with columns 'COLUMN BUSINESS NAME' 
               and 'TABLE BUSINESS NAME'

    Returns:
        result_df: a dataframe with below columns:
            "Orig Table Name", "Orig Column Name","Best Match Term",
            "Best Match Score", "Top Matches"

    """
    vocab = create_input_vocab(vocab_file_name)
    toMatchDf = load_xl_df(input_file_name)
    toMatchDf = toMatchDf.dropna(subset=['Column Name'])
    result_df = match_vocab(toMatchDf, vocab, threshold, max_matches)
    return result_df


# Sample code
# import os
# WORKING_DIRECTORY = 'C:/Users/klove/Downloads'
# os.chdir(WORKING_DIRECTORY)
# results = run_vocab_match('ColumnsToMatch.xlsx', 70, 40 )
# save_as_xl(results)






    
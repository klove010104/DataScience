# -*- coding: utf-8 -*-

"""Check a list of terms against a standard vocabulary.

The standard vocabulary is specified by an Excel with columns titled
'Attribute Name' and 'Entity Name'. The list of terms is 
an Excel with columns 'Entity Name' and 'Attribute Name'. 

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
    input_df = input_df.dropna(subset=['Attribute Name'])

    # Standardize and add a column with the standardized names
    # TODO SettingWithCopyWarning
    input_df['ColumnNameStd'] = input_df['Attribute Name'].str.title()
    # also gives the warning. leaving as comment because lambda is handy
    # input_df['ColumnNameStd'] = input_df['Attribute Name'].apply(lambda x: x.title())
    return input_df
 
def create_input_vocab(input_file_name):
    """Returns unique list of target names to match against.

    """
    input_vocab_df = load_xl_df(input_file_name)
    input_vocab_df = preprocess_input_vocab(input_vocab_df)
    # use unique list for further processing
    target_names = get_target_vocab(input_vocab_df['ColumnNameStd'])
    return target_names


def match_to_target(input_word, target_names, threshold, max_matches):
    """Matches single word to vocabulary - returns list of tuples

    Uses fuzzy matching to compare a single word to a list of candidate 
    words, and returns the number of possible matches (limited by max 
    matches) scoring >= threshold.

    Args:
        input_word: the word to find a match for
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
    for match in process.extract(input_word, target_names, limit=max_matches):
        if match[score_col] > threshold:
            matches.append(match)
    return matches    

def get_top_match(matches):
    """From the list of matches, returns tuple of the highest score match.

    Assumes the list is sorted by match score descending. Returns the tuple 
    from the first row. If there are no matches, returns tuple 
    ('no matches', 0). If there are multiple matches with same top score, 
    returns tuple ('multiple matches', top score)
    
    Args:
        matches: a list of tuples (match word, score)
        
    Returns:
        single tuple in form of (top match, top score)

    """
    top_score = 0
    top_term = 'no matches'
    
    if len(matches) >= 1:
        top_score = matches[0][1]
        top_term = matches[0][0]
        if len(matches) > 1:
            if matches[1][1] == top_score:
                top_term = 'multiple matches'
    return (top_term, top_score)

def match_vocab(input_df, vocab, threshold, max_matches):
    """Matches each term in input_df to standard vocab

    Loops through input and runs the match, then returns a dataframe with
    the results.

    Args:
        input_df: the original dataframe loaded from user input
        vocab: the standardized vocabulary list
        threshold: an integer representing the lowest score for a match
        max_matches: an integer representing the most matches to keep

    Returns:
        output_df: a dataframe with below columns:
            "Orig Entity Name", "Orig Attribute Name","Best Match Term",
            "Best Match Score", "Top Matches"

    """
    term_matches = []
    output_df = pd.DataFrame(columns =
                             ["Orig Entity Name", "Orig Attribute Name",
                              "Best Match Term","Best Match Score", 
                              "Top Matches" ] )

    for tbl, term in zip(input_df['Entity Name'],input_df['Attribute Name']): 
        term_matches = match_to_target(term, vocab, threshold, max_matches);
        top_term_tuple = get_top_match(term_matches)
        values_to_add = {'Orig Entity Name': tbl, 
                         'Orig Attribute Name': term, 
                         'Best Match Term': top_term_tuple[0], 
                         'Best Match Score': top_term_tuple[1], 
                         'Top Matches': term_matches}
        tname = stringcase.camelcase(stringcase.snakecase(term))
        row_to_add = pd.Series(values_to_add, name = tname)
        output_df = output_df.append(row_to_add)
    return output_df

def is_dd_format(input_df):
    """Checks to see if input file has expected data dictionary format
    
        Args:
            input_df: DataFrame to check
        
        Returns:
            True if 
                the DataFrame has at least these columns:'MODEL NAME', 
                    'Entity Name', 'Attribute Name',
                    'COLUMN BUSINESS DEFINITION'
                the DataFrame has at least 1 observation (row)
    """ 
    return False

# =============================================================================
#  public facing functions below here. maybe I'll create a class sometime
# 
# =============================================================================
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

def run_vocab_match(input_file_name, threshold, max_matches, 
                    vocab_file_name = MASTER_VOCAB_FILE_NAME):
    """Matches terms in an input file to a vocabulary and returns dataframe.

    Retrieves rows pertaining to the given keys from the Table instance
    represented by table_handle.  String keys will be UTF-8 encoded.

    Args:
        input_file_name: Excel with columns 'Entity Name' and 'Attribute Name'
        threshold: an integer representing the lowest score for a match
        max_matches: an integer representing the most matches to keep
        vocab: Excel with target terms with columns 'Attribute Name' 
               and 'Entity Name'

    Returns:
        result_df: a dataframe with below columns:
            "Orig Entity Name", "Orig Attribute Name","Best Match Term",
            "Best Match Score", "Top Matches"

    """
    vocab = create_input_vocab(vocab_file_name)
    to_match_df = load_xl_df(input_file_name)
    to_match_df = to_match_df.dropna(subset=['Attribute Name'])
    result_df = match_vocab(to_match_df, vocab, threshold, max_matches)
    return result_df

def score_data_dictionary(input_file_name):
    """Scores data dictionary for inconsistencies and missing values.
    
        Examine the input data dictionary and score each attribute:
            0 if the definition is missing
            1 if there's another attribute with same name different definition
            2 if all instances of the attribute have same definition
        
        Also return the number of times the attribute name appears.
        
        Future enhancement: check for consistency in data types
        
        Args:
            input_file_name: Excel with columns 'MODEL NAME', 
                'Entity Name', 'Attribute Name',
                'COLUMN BUSINESS DEFINITION'
                
        Returns:
            result_df: a dataframe echoing the input columns plus:
                'DEFINITION SCORE', 'INSTANCE COUNT'
    
    """
    output_df = pd.DataFrame()
    # potential file does not exist
    input_df = load_xl_df(input_file_name)
    if(is_dd_format(input_df)):
        None # TODO (obviously)
    else:
        output_df = 'error string' # TODO - raise exception or describe file format
    return output_df

# Sample code
# import os
# WORKING_DIRECTORY = 'C:/Users/klove/Downloads'
# os.chdir(WORKING_DIRECTORY)
# results = run_vocab_match('ColumnsToMatch.xlsx', 70, 40 )
# save_as_xl(results)






    
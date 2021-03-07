# -*- coding: utf-8 -*-

'''Check a list of terms against a standard vocabulary.

The standard vocabulary is specified by an Excel with columns titled
'Attribute Name' and 'Entity Name'. The list of terms is 
an Excel with columns 'Entity Name' and 'Attribute Name'. 

  Typical usage example:

  results = run_vocab_match('ColumnsToMatch.xlsx', 70, 40 ) \n
  save_as_xl(results)

Created on Sun Feb 14 13:15:59 2021

@author: klove
'''

import pandas as pd
import numpy as np
from fuzzywuzzy import process
import FilePrepUtils


WORKING_DIRECTORY = 'C:\\Users\\klove\\Downloads\\'
MASTER_VOCAB_FILE_NAME = WORKING_DIRECTORY + 'MasterDDv2.xlsx'
TRANSLATOR_FILE_NAME = WORKING_DIRECTORY +  'DD Transforms.xlsx'
RESULT_FILE_NAME = 'Matched_Vocab.xlsx'

MODEL_COL = 'Model Name'
ENTITY_COL = 'Entity Name'
ATTRIBUTE_COL = 'Attribute Name'
ATT_DEFN_COL = 'Attribute/Column Definition'



def preprocess_df(input_df, attr_col = ATTRIBUTE_COL, translate_file_name = TRANSLATOR_FILE_NAME):
    '''Drops rows with no values and standardizes the values in attr_col
    
    Standardization rules: 
        remove underscores
        remove doublespaces (two spaces in a row)
        remove leading and trailing spaces
        title case the attributes
        translate terms using standard translation file specified 
            in FilePrepUtils TRANSLATOR_FILE_NAME
    
    Args: 
        input_df - a dataframe with attribute column named by attr_col
    
    Returns:
        input_df with original attr_col renamed prefixed with Old and 
            standardized attributes in attr_col

    '''
    input_df = input_df.dropna(subset=[attr_col])
    attributes = FilePrepUtils.standardize_cosmetic(input_df[attr_col])
    attributes = FilePrepUtils.find_and_replace(attributes, translate_file_name)
    old_col = 'Old ' + attr_col
    input_df = input_df.rename(columns={attr_col: old_col})
    input_df[attr_col] = attributes
    return input_df

def match_to_target(input_word, target_names, threshold, max_matches):
    '''Matches single word to vocabulary - returns list of tuples

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

    '''
    matches = []
    score_col = 1
    for match in process.extract(input_word, target_names, limit=max_matches):
        if match[score_col] > threshold:
            matches.append(match)
    return matches    

def get_top_match(matches):
    '''From the list of matches, returns tuple of the highest score match.

    Assumes the list is sorted by match score descending. Returns the tuple 
    from the first row. If there are no matches, returns tuple 
    ('no matches', 0). If there are multiple matches with same top score, 
    returns tuple ('multiple matches', top score)
    
    Args:
        matches: a list of tuples (match word, score)
        
    Returns:
        single tuple in form of (top match, top score)

    '''
    top_score = 0
    top_term = 'no matches'
    
    if len(matches) >= 1:
        top_score = matches[0][1]
        top_term = matches[0][0]
        if len(matches) > 1:
            if matches[1][1] == top_score:
                top_term = 'multiple matches'
    return (top_term, top_score)

def match_vocab(to_match_df, vocab, threshold, max_matches):
    '''Matches each term in to_match_df to standard vocab

    Loops through input and runs the match, then returns a dataframe with
    the results.

    Args:
        to_match_df: TODO specify what is required   
        vocab: the standardized vocabulary list
        threshold: an integer representing the lowest score for a match
        max_matches: an integer representing the most matches to keep

    Returns:
        output_df: a dataframe with below columns:
        'Entity Name', 'Old Attribute Name', 'Attribute/Column Definition',
       'Attribute Name', 'Matches', 'Top Match Attribute', 'Top Match Score1'

    '''
    
    term_matches = []
    matched_dict = {}
    for tbl, term in zip(to_match_df[ENTITY_COL],to_match_df[ATTRIBUTE_COL]): 
        term_matches = match_to_target(term, vocab, threshold, max_matches);
        matched_dict[term] = term_matches
    # now construct a new data frame to hold the results
    output_df = to_match_df[[ENTITY_COL,'Old '+ ATTRIBUTE_COL, ATT_DEFN_COL, 
                             ATTRIBUTE_COL]]
    # TODO WARNING now map the matches back to those attributes
    output_df['Matches'] = output_df[ATTRIBUTE_COL].map(matched_dict)
    # get top matches and append to the output
    output_df['Top Match Tuple']= list(map(get_top_match, output_df['Matches']))
    output_df[['Top Match Attribute','Top Match Score1']] = pd.DataFrame(output_df['Top Match Tuple'].tolist(), index=output_df.index)
    output_df =output_df.drop(['Top Match Tuple'], axis=1)
    return output_df

def is_dd_format(input_df):
    '''Checks to see if input file has expected data dictionary format
    
        Args:
            input_df: DataFrame to check
        
        Returns:
            True if 
                the DataFrame has at least these columns:'MODEL NAME', 
                    'Entity Name', 'Attribute Name',
                    'Attribute/Column Definition'
                the DataFrame has at least 1 observation (row)
    '''  
    required_cols = [MODEL_COL,ENTITY_COL, ATTRIBUTE_COL, ATT_DEFN_COL]
    hascols= set(input_df.columns).intersection(required_cols) == set(required_cols)
    hasarow = not input_df.empty
    return hascols & hasarow


def score_definitions(input_df, colname = ATTRIBUTE_COL, defname = ATT_DEFN_COL):
    '''For each attribute, scores how well definitions match in dataset
    
        Examine the input data dictionary and score each attribute:
            0 if the definition is missing
            1 if there's another attribute with same name different definition
            2 if all instances of the attribute have same definition    

        Args:
            input_df: DataFrame to check
        
        Returns:  
            attribute_scores: pandas Series same size/order as df with score
    '''
    odf = pd.DataFrame( { colname : input_df[colname],
                          defname : input_df[defname]})
    odf['Definition Score'] = -1
    unique = input_df[colname].unique()
    # now you have to match the counts back to the df
    score = []
    for name_col in unique:
        # find all the rows where this attribute appears
        these = input_df.loc[lambda input_df: input_df[colname] == 
                             name_col]
        # if the definitions match, there will be 1 unique value
        if these[defname].nunique() == 1:
            score.append(2)
        else:
            score.append(1)
    # now you have to match the scores back to the df
    i = 0
    for name_col in unique:
        odf['Definition Score'].where(~((odf[colname] == name_col
                                         )), 
                                      other=score[i], inplace=True)
        i+=1  
    #  score for rows with missing attribute definition to 0
    odf['Definition Score'] = np.where(odf[defname].isna(), 0, odf['Definition Score'])
    odf['Definition Score'] = np.where((odf[defname] == ""), 0, odf['Definition Score'])
    return odf['Definition Score']
 
    
    
def attribute_count_in_df(input_df, colname = 'Attribute Name'):
    '''Counts how many times an attribute appears in the DataFrame
       
    
    Args:
            input_df: DataFrame with column colname
            colname:  column name to count
        
    Returns:
            instance_counts: pandas Series same size/order as df with count of 
                how many times attribute is in the df
    '''
    odf = pd.DataFrame( { colname : input_df[colname]})
    odf['Instance Count'] = 0
    values = np.array(input_df[colname])
    (unique, counts) = np.unique(values, return_counts=True)
    # now you have to match the counts back to the df
    i = 0
    for name_col in unique:
        odf['Instance Count'].where(~(odf[colname] == name_col), other=counts[i], inplace=True)
        i+=1
    return odf['Instance Count']

# =============================================================================
#  public facing functions below here. maybe I'll create a class sometime
# 
# =============================================================================

def run_vocab_match(match_file_name, threshold, max_matches, 
                    vocab_file_name = MASTER_VOCAB_FILE_NAME,
                    std_abbrev_file_name = TRANSLATOR_FILE_NAME):
    '''Matches terms in an input file to a vocabulary and returns dataframe.

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
            'Orig Entity Name', 'Orig Attribute Name','Best Match Term',
            'Best Match Score', 'Top Matches'

    '''
    input_vocab_df = pd.read_excel(vocab_file_name)
    vocab = pd.unique(input_vocab_df[ATTRIBUTE_COL])

    # load the file to match
    to_match_df = pd.read_excel(match_file_name)
    to_match_df = to_match_df.dropna(subset=[ATTRIBUTE_COL])
    to_match_df = preprocess_df(to_match_df, ATTRIBUTE_COL, std_abbrev_file_name)
    
    result_df = match_vocab(to_match_df, vocab, threshold, max_matches)
    #result_df.to_excel(WORKING_DIRECTORY + 'New_' + match_file_name)

    translator_dict = dict(zip(input_vocab_df[ATTRIBUTE_COL], input_vocab_df[ATT_DEFN_COL]))
    result_df['Matched Attribute Definition'] = result_df[ATTRIBUTE_COL].map(translator_dict)
    result_df['Top Match Score'] = result_df['Top Match Score1']
    result_df = result_df.drop(['Top Match Score1'], axis=1)
    return result_df

def score_data_dictionary(input_file_name):
    '''Scores data dictionary for inconsistencies and missing values.
    
        Examine the input data dictionary and score each attribute:
            0 if the definition is missing
            1 if there's another attribute with same name different definition
            2 if all instances of the attribute have same definition
        
        Also return the number of times the attribute name appears.
        
        Future enhancement: check for consistency in data types
        
        Args:
            input_file_name: Excel with columns 'Model Name','Entity Name', 
                'Attribute Name', 'Attribute/Column Definition'
                
        Returns:
            result_df: a dataframe echoing the input columns plus:
                        'Definition Score', 'Instance Count'
    
    '''
    output_df = pd.DataFrame()
    # potential file does not exist
    input_df = pd.read_excel(input_file_name)
    if(is_dd_format(input_df)):
        output_df = input_df.copy()
        output_df['Definition Score'] = score_definitions(input_df)
        # find the attributes where every definition matches and score 2
        # find attributes where some definitions do not match and score 1
        output_df['Instance Count'] = attribute_count_in_df(input_df)
    else:
        output_df = 'Input File must have all required columns and at least 1 row'
        # TODO consider raising exception
    return output_df

# Sample code
# import os
WORKING_DIRECTORY = 'C:/Users/klove/Downloads/'
matchfile = 'TemplateAttributesToMatch.xlsx' 
#results = run_vocab_match(WORKING_DIRECTORY + matchfile, 70, 40 )
#results.to_excel(WORKING_DIRECTORY + 'New_' + matchfile)







    
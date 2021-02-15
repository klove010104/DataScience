# -*- coding: utf-8 -*-
"""
Created on Sun Feb 14 13:27:03 2021

@author: klove
"""

import pandas as pd
from fuzzywuzzy import process
import stringcase

# This file will be on a shared drive and refreshed periodically
MASTER_VOCAB_FILE_NAME = 'C:/Users/klove/Downloads/CoreAttributes.xlsx'
RESULT_FILE_NAME = 'Matched_Vocab.xlsx'

# Assumes that either file is in current directory, or it's fully qualified
def load_xl_df(input_file_name):
    df = pd.read_excel(input_file_name)
    return df

# Save dataframe as excel
def save_as_xl(result_df, result_name=RESULT_FILE_NAME):
    result_df.to_excel(result_name)

# use unique list for further processing
def get_target_vocab(df_column):
    tv = pd.unique(df_column)
    tv.sort()
    return tv

def preprocess_input_vocab(input_df):
    # print(input_df.shape)
    input_df = input_df.dropna(subset=['COLUMN BUSINESS NAME'])
    # print(input_df.shape)
    # Standardize and add a column with the standardized names
    # SettingWithCopyWarning
    input_df['ColumnNameStd'] = input_df['COLUMN BUSINESS NAME'].str.title()
    # also gives the warning. leaving as comment because lambda is handy
    # input_df['ColumnNameStd'] = input_df['COLUMN BUSINESS NAME'].apply(lambda x: x.title())
    return input_df

# Returns unique list of target names to match against
def create_input_vocab(input_file_name):
    input_vocab_df = load_xl_df(input_file_name)
    input_vocab_df = preprocess_input_vocab(input_vocab_df)
    # use unique list for further processing
    target_names = get_target_vocab(input_vocab_df['ColumnNameStd'])
    return target_names

# Matches a single word to a vocabulary
# Returns a list of matches - tuple of (matched word, match score)
def match_to_target(inputword, target_names, threshold, max_matches):
    matches = []
    score_col = 1
    for match in process.extract(inputword, target_names, limit=max_matches):
        if match[score_col] > threshold:
            matches.append(match)
    return matches    

# take input of match tuples, and return a tuple of the best match
# if multiple with top score, put word "multiple"
def get_top_match(matches):
    if len(matches) == 0:
        top_score = 0
        top_term = 'no matches'
    else:
        top_score = matches[0][1]
        top_term = matches[0][0]
    if len(matches) > 1:
        if matches[1][1] == top_score:
            top_term = 'multiple matches'
    return (top_term, top_score)

# return a data frame for output of the whole process
# if there are multiple best match terms with same score,  print <multiple matches>
def create_output_df(inputDf, vocab, threshold, max_matches):
    term_matches = []
    output_df = pd.DataFrame(columns =["Orig Table Name", "Orig Column Name","Best Match Term","Best Match Score", "Top Matches" ] )

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
def run_vocab_match(input_file_name, threshold, max_matches, vocab_file_name = MASTER_VOCAB_FILE_NAME):
    vocab = create_input_vocab(vocab_file_name)
    toMatchDf = load_xl_df(input_file_name)
    toMatchDf = toMatchDf.dropna(subset=['Column Name'])
    result_df = create_output_df(toMatchDf, vocab, threshold, max_matches)
    # save to a file
    return result_df


# Sample code
# import os
# WORKING_DIRECTORY = 'C:/Users/klove/Downloads'
# os.chdir(WORKING_DIRECTORY)
# results = run_vocab_match('ColumnsToMatch.xlsx', 70, 40 )
# save_as_xl(results)






    
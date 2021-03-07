# -*- coding: utf-8 -*-
'''
test_VocabChecker.py

Created on Sun Feb 14 22:05:05 2021

@author: klove
'''
import VocabChecker as vc
import pandas as pd
import os

WORKING_DIRECTORY = 'C:\\Users\\klove\\Downloads\\'
GITHUB_TEST_DIR = "C:\\Users\\klove\\OneDrive\\Documents\\GitHub\\DataScience\\tests\\"
REQUIRED_INPUT_COLUMNS = ['Model Name','Entity Name', 'Attribute Name', 
                          'Attribute/Column Definition']

# =============================================================================
# Utilities
# =============================================================================
def diagnose_failure(result_df, expected_df):
    mismatches = result_df['Definition Score'] != expected_df['Definition Score']
    mismatched = result_df[mismatches]
    return mismatched
    
def add_input_row (model_name, table_name, column_name, dfn, extra1, 
                   extra2, rowlbl) :
    values_to_add = {'Model Name': model_name, 
                      'Entity Name': table_name, 
                      'Attribute Name': column_name, 
                      'Attribute/Column Definition': dfn,
                      'Random Attribute 1': extra1, 
                      'xtra column2': extra2}
    row_to_add = pd.Series(values_to_add, name = rowlbl)
    return row_to_add
        
def create_test_xl(scenario):
    os.chdir(WORKING_DIRECTORY)
    column_names = REQUIRED_INPUT_COLUMNS + ['Random Attribute 1', 
                                             'xtra column2']
    row1 = add_input_row('model1','table1','attribute1','number one is best',
                         'blue','Goofy','row1')
    df = pd.DataFrame()
    if scenario == 'Empty File':
        df.to_excel('EmptyFile.xlsx')
    elif scenario == 'Headers Only':
        df = pd.DataFrame(columns = column_names)
        df.to_excel('HeadersOnly.xlsx')
    else:
        df = pd.DataFrame(columns = column_names)
        df = df.append(row1)        
        if scenario == 'Missing Model':
            column_names.remove('Model Name')
            df = pd.DataFrame(columns = column_names)
            df.to_excel('MissingModel.xlsx')
        elif scenario == 'Missing Table':
            column_names.remove('Entity Name')
            df = pd.DataFrame(columns = column_names)
            df.to_excel('MissingTable.xlsx')
        elif scenario == 'Missing Column':
            column_names.remove('Attribute Name')
            df = pd.DataFrame(columns = column_names)
            df.to_excel('MissingColumn.xlsx')
        elif scenario == 'Missing Definition':
            column_names.remove('Attribute/Column Definition')
            df = pd.DataFrame(columns = column_names)
            df.to_excel('MissingDef.xlsx')
    # default returns df with 1 row
    return df
    
def remove_file(file_name):
    if os.path.exists(file_name):
        os.remove(file_name) 

def cleanup():
    os.chdir(WORKING_DIRECTORY)
    remove_file(WORKING_DIRECTORY + 'EmptyFile.xlsx')
    remove_file('HeadersOnly.xlsx')
    remove_file('MissingModel.xlsx')
    remove_file('MissingTable.xlsx')
    remove_file('MissingColumn.xlsx')
    remove_file('MissingDef.xlsx')
    remove_file('default.xlsx')

# =============================================================================
# Tests
# =============================================================================
def test_preprocess():
    '''unit tests for VocabChecker.preprocess_df
    
    Loads VocabMatcherTests.xlsx which has the tests and expected results
        
    Cosmetic tests - removing underscores, leading/trailing spaces, two spaces
    Find and Replace tests - at beginning, middle, and end
 
    '''
    test_df = pd.read_excel(GITHUB_TEST_DIR + 'VocabMatcherTests.xlsx')
    test_case_df = test_df[test_df['Model Name']=='TestPreprocess']
    result_df = vc.preprocess_df(test_case_df)
    assert( list(result_df['Attribute Name']) ==list(test_case_df['Expected Attribute']))

def test_run_vocab_match():
    '''unit tests for VocabChecker.run_vocab_match
    
    Loads VocabMatcherIntTests.xlsx which has the tests and expected results
    Uses File_Util_TransformDD_Test.xlsx as its translator file
 
    '''
    test_df = pd.read_excel(GITHUB_TEST_DIR + 'VocabMatcherIntTests.xlsx')
    test_cases_df = test_df[test_df['Model Name']=='TestMatchVocab']
    match_file_name = GITHUB_TEST_DIR + 'VocabMatcherIntTests.xlsx'
    vocab_file_name = GITHUB_TEST_DIR + 'VocabMatcherIntTests.xlsx'
    translator_file_name = GITHUB_TEST_DIR + 'File_Util_TransformDD_Test.xlsx'
    result_df = vc.run_vocab_match(match_file_name, 90, 5, vocab_file_name, translator_file_name )
    results = list(result_df['Attribute Name'])
    expected = list(test_cases_df['Expected Attribute'])
    assert(results == expected ) 
    
def test_get_top_match():
    '''unit tests for VocabChecker.get_top_match
    
    Test cases:
        No matches
        Only 1 match
        Two matches equal strength. Three matches equal strength
        Strongest match
        Match scores not in order - returns weaker match
 
    '''
    
    # if there are no matches
    matches = []
    expected_val = ('no matches', 0)
    assert( vc.get_top_match(matches) == expected_val)
    
    # if there is only 1 match
    matches = [ ('Only Match', 100) ]
    expected_val = ('Only Match', 100) 
    assert( vc.get_top_match(matches) == expected_val)
    
    # two matches of equal strength
    matches = [ ('One Match', 90), ('Another Match', 90) ]
    expected_val = ('multiple matches', 90) 
    assert( vc.get_top_match(matches) == expected_val)   

    # two matches but one is stronger
    matches = [ ('One Match', 100), ('Another Match', 90) ]
    expected_val = ('One Match', 100) 
    assert( vc.get_top_match(matches) == expected_val)   
    
    # three matches of equal strength
    matches = [ ('One Match', 90), ('Another Match', 90), ('Third Match', 90) ]
    expected_val = ('multiple matches', 90) 
    assert( vc.get_top_match(matches) == expected_val)   
    
    # two matches but one is stronger, but order is wrong 
    # ******NOTE********* Algorithm assumes top match is first
    # ******************* So, if it isn't, this happens (wrong top score)
    matches = [ ('One Match', 90), ('Another Match', 100) ]
    expected_val = ('One Match', 90) 
    assert( vc.get_top_match(matches) == expected_val)   

def test_score_data_dictionary_inputs():
    '''unit tests for score_data_dictionary inputs
    
    Input file tests:
        input file is empty
        input file only has headers, no data
        input file does not have required columns
        input file has more than required columns (all should appear in output)
        
    '''
    expected = 'Input File must have all required columns and at least 1 row'
    create_test_xl('Empty File')
    assert(vc.score_data_dictionary('EmptyFile.xlsx') == expected)
    create_test_xl('Headers Only')
    assert(vc.score_data_dictionary('HeadersOnly.xlsx') == expected)    
    create_test_xl('Missing Model')
    assert(vc.score_data_dictionary('MissingModel.xlsx') == expected)
    create_test_xl('Missing Table')
    assert(vc.score_data_dictionary('MissingTable.xlsx') == expected)
    create_test_xl('Missing Column')
    assert(vc.score_data_dictionary('MissingColumn.xlsx') == expected)
    create_test_xl('Missing Definition')
    assert(vc.score_data_dictionary('MissingDef.xlsx') == expected)
    cleanup()

def test_score_data_dictionary_out():
    '''unit tests for score_data_dictionary output format
        
    Output file format tests:
        check if all output columns are present
        check if every row has a score
        check if every row has a count
        check if all Definition Scores are between 0 and 2
        check if all Instance Counts are > 0
    
    '''
    input_df = create_test_xl("default")
    input_df.to_excel("default.xlsx")
    column_names = REQUIRED_INPUT_COLUMNS + ['Random Attribute 1', 
                                             'xtra column2',
                                             'Definition Score', 
                                             'Instance Count']  
    output_df = vc.score_data_dictionary("default.xlsx")
    print(output_df)
    assert(type(output_df) == pd.DataFrame)
    assert(output_df.shape[1] == len(column_names) + 1)
    output_cols = list(output_df.columns[1:])
    assert(output_cols == column_names)
    assert(output_df['Definition Score'].notnull().all())
    assert((output_df['Definition Score'] >= 0).all())
    assert((output_df['Definition Score'] <=2 ).all())
    assert(output_df['Instance Count'].notnull().all())
    assert((output_df['Instance Count'] > 0).all())

def test_score_data_dictionary():
    '''unit tests for score_data_dictionary
    
    Excel input file with test data : DDScoreTest
    Excel file with expected output : DDScoreTestExpected
    
    Tests for attribute count:
        input file only has 1 row (attribute count =1, score = 2)
        attribute appears once - count 1
        attribute appears 2 times - count 2
        attribute appears 3 times - count 3
    
    Tests for score
        definition is missing - score 0
        two columns same name, definitions mismatch - score 1
        three columns same name, all mismatch - score 1
        three columns same name, two same, one different - score 1
        column only appears once in dataset, single row scenario - score 2
        column only appears once in dataset, multiple scenario - score 2
    '''
    expected_df = pd.read_excel( GITHUB_TEST_DIR + "DDScoreTestExpected.xlsx")
    result_df = vc.score_data_dictionary(GITHUB_TEST_DIR + "DDScoreTest.xlsx")
    assert(type(result_df) == pd.DataFrame)
    assert((result_df['Definition Score'] == expected_df['Definition Score']).all())
    assert(result_df['Instance Count'] == expected_df['Instance Count']).all()

def test_score_definitions():
    '''unit tests for VocabChecker.score_definitions
    
    Excel input file with test data : DDScoreTest
    Excel file with expected output : DDScoreTestExpected
    
    Tests for score
        definition is missing - score 0
        two columns same name, definitions mismatch - score 1
        three columns same name, all mismatch - score 1
        three columns same name, two same, one different - score 1
        column only appears once in dataset, single row scenario - score 2
        column only appears once in dataset, multiple scenario - score 2
    '''
    expected_df = pd.read_excel( GITHUB_TEST_DIR + "DDScoreTestExpected.xlsx")
    input_df = pd.read_excel(GITHUB_TEST_DIR + "DDScoreTest.xlsx")
    results = vc.score_definitions(input_df)    
    assert(type(results) == pd.Series)
    assert( list(results) == list(expected_df['Definition Score']))

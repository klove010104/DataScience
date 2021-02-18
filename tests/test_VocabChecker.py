# -*- coding: utf-8 -*-
'''
test_VocabChecker.py

Created on Sun Feb 14 22:05:05 2021

@author: klove
'''
import VocabChecker as vc
import pandas as pd
import os

WORKING_DIRECTORY = 'C:/Users/klove/Downloads/'

def test_get_top_match():
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

    
def test_score_data_dictionary():
    '''unit tests for score_data_dictionary
        
    Output file format tests:
        check if all output columns are present
        check if every row has a score
        check if every row has a count
    
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
        column only appears once in dataset, single scenario - score 2
        column only appears once in dataset, multiple scenario - score 2
    '''
# =============================================================================
#     column_names = ['MODEL NAME',  'TABLE BUSINESS NAME', 
#                     'COLUMN BUSINESS NAME', 'DEFINITION SCORE',
#                     'INSTANCE COUNT']  
# =============================================================================
    assert(False)

def add_input_row (model_name, table_name, column_name, dfn, extra1, 
                   extra2, rowlbl) :
    values_to_add = {'MODEL NAME': model_name, 
                      'TABLE BUSINESS NAME': table_name, 
                      'COLUMN BUSINESS NAME': column_name, 
                      'COLUMN BUSINESS DEFINITION': dfn,
                      'random column 1': extra1, 
                      'xtra column2': extra2}
    row_to_add = pd.Series(values_to_add, name = rowlbl)
    return row_to_add
        
def create_test_xl(scenario):
    os.chdir(WORKING_DIRECTORY)
    column_names = ['MODEL NAME',  'TABLE BUSINESS NAME', 
                    'COLUMN BUSINESS NAME', 'COLUMN BUSINESS DEFINITION',
                    'random column 1', 'xtra column2']
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
            column_names.remove('MODEL NAME')
            df = pd.DataFrame(columns = column_names)
            df.to_excel('MissingModel.xlsx')
        elif scenario == 'Missing Table':
            column_names.remove('TABLE BUSINESS NAME')
            df = pd.DataFrame(columns = column_names)
            df.to_excel('MissingTable.xlsx')
        elif scenario == 'Missing Column':
            column_names.remove('COLUMN BUSINESS NAME')
            df = pd.DataFrame(columns = column_names)
            df.to_excel('MissingColumn.xlsx')
        elif scenario == 'Missing Definition':
            column_names.remove('COLUMN BUSINESS DEFINITION')
            df = pd.DataFrame(columns = column_names)
            df.to_excel('MissingDef.xlsx')
    return df

def remove_file(file_name):
    if os.path.exists('file_name'):
        os.remove('file_name') 

def cleanup():
    os.chdir(WORKING_DIRECTORY)
    remove_file('EmptyFile.xlsx')
    remove_file('HeadersOnly.xlsx')
    remove_file('MissingModel.xlsx')
    remove_file('MissingTable.xlsx')
    remove_file('MissingColumn.xlsx')
    remove_file('MissingDef.xlsx')
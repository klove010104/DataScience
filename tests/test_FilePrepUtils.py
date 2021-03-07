# -*- coding: utf-8 -*-
"""
Created on Sat Feb 27 17:52:17 2021

@author: klove
"""

import pandas as pd
import FilePrepUtils as fp

WORKING_DIRECTORY = 'C:\\Users\\klove\\Downloads\\'
GITHUB_TEST_DIR = "C:\\Users\\klove\\OneDrive\\Documents\\GitHub\\DataScience\\tests\\"

def test_replace_at_beginning():
    test_df = pd.read_excel(GITHUB_TEST_DIR + 'VocabMatcherTests.xlsx')
    test_cases_df = test_df[test_df['Model Name']=='TestFindBegin']
    
    for ind in test_cases_df.index:
        print(test_cases_df['Attribute Name'][ind])
        result =  fp.replace_at_beginning(test_cases_df['Attribute Name'][ind] 
                                          , test_cases_df['NonStandard Value'][ind]
                                          , test_cases_df['Standard Value'][ind])
        assert(result == test_cases_df['Expected Attribute'][ind])        

def test_replace_at_end():
    test_df = pd.read_excel(GITHUB_TEST_DIR + 'VocabMatcherTests.xlsx')
    test_cases_df = test_df[test_df['Model Name']=='TestFindEnd']
    
    for ind in test_cases_df.index:
        print(test_cases_df['Attribute Name'][ind])
        result =  fp.replace_at_end(test_cases_df['Attribute Name'][ind] 
                                          , test_cases_df['NonStandard Value'][ind]
                                          , test_cases_df['Standard Value'][ind])
        expected = test_cases_df['Expected Attribute'][ind]
        assert(result == expected ) 

def test_replace_in_middle():
    test_df = pd.read_excel(GITHUB_TEST_DIR + 'VocabMatcherTests.xlsx')
    test_cases_df = test_df[test_df['Model Name']=='TestMiddle']
    
    for ind in test_cases_df.index:
        print(test_cases_df['Attribute Name'][ind])
        result =  fp.replace_in_middle(test_cases_df['Attribute Name'][ind] 
                                          , test_cases_df['NonStandard Value'][ind]
                                          , test_cases_df['Standard Value'][ind])
        expected = test_cases_df['Expected Attribute'][ind]
        assert(result == expected ) 

def test_find_and_replace():
    test_df = pd.read_excel(GITHUB_TEST_DIR + 'VocabMatcherTests.xlsx')
    test_cases_df = test_df[test_df['Model Name']=='TestFindReplace']
    results = fp.find_and_replace(test_cases_df['Attribute Name'], 
                                  GITHUB_TEST_DIR + 'File_Util_TransformDD_Test.xlsx')
    expected = list(test_cases_df['Expected Attribute'])
    assert(results == expected ) 

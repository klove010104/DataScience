# -*- coding: utf-8 -*-
"""
test_VocabChecker.py

Created on Sun Feb 14 22:05:05 2021

@author: klove
"""
import VocabChecker as vc

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
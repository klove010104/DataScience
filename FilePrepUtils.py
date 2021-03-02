# -*- coding: utf-8 -*-
"""
Created on Thu Feb 25 10:17:32 2021

@author: klove
"""

import pandas as pd
import re

WORKING_DIRECTORY = 'C:\\Users\\klove\\Downloads\\'
TRANSLATOR_FILE_NAME = WORKING_DIRECTORY +  'DD Transforms.xlsx'

def remove_underscores(attributes):
    list_old_val = ['_' for i in range(len(attributes))]
    list_new_val = [' ' for i in range(len(attributes))]
    std_attr = list(map(str.replace, attributes, list_old_val, list_new_val))
    return std_attr

def remove_doublespace(attributes):
    list_old_val = ['  ' for i in range(len(attributes))]
    list_new_val = [' ' for i in range(len(attributes))]
    std_attr = list(map(str.replace, attributes, list_old_val, list_new_val))
    return std_attr

def standardize_case(attributes):
    """Returns list with preferred casing: currently title case

    """

    std_attr = list(map(str.title, attributes))
    return std_attr

def remove_lead_trail(attributes):
    """Returns list with lead/trail spaces and EOL stripped

    """
    return list(map(str.strip, attributes))

def replace_at_end(target, old_val, new_val):
    """ replace if the word is at the end of the string
    
    Note it also title cases if it replaces
    
    replace_at_end(attribute, 'id', 'Identifier')
    """
    expr = old_val + '$'
    replaced = re.sub(expr, new_val, target, flags=re.IGNORECASE)
    return replaced

def replace_at_beginning(target, old_val, new_val):
    """ replace if the word is at the end of the string
    
    Note it also title cases if it replaces
    
    replace_at_end(attribute, 'id', 'Identifier')
    """
    expr = '^' + old_val + ' '
    new_val = new_val + ' '
    replaced = re.sub(expr, new_val, target, flags=re.IGNORECASE)
    return replaced

def replace_in_middle(target, old_val, new_val):
    expr = ' ' + old_val + ' '
    new_val = ' ' + new_val + ' '
    replaced = re.sub(expr, new_val, target, flags=re.IGNORECASE)
    return replaced

def recode_old_new(attributes, old_val, new_val):
    """ Recode ID, Id at end of word or with trailing space to Identifier """
    # to use map, you need to have same length args list
    # so, create your old and new value arrays with same size as attributes
    list_old_val = [old_val for i in range(len(attributes))]
    list_new_val = [new_val for i in range(len(attributes))]
    std_attr = list(map(replace_at_end, attributes, list_old_val, list_new_val))
    std_attr = list(map(replace_at_beginning, std_attr, list_old_val, list_new_val))  
    std_attr = list(map(replace_in_middle, std_attr, list_old_val, list_new_val))  
    return std_attr

def find_and_replace(attributes, translator_fname = TRANSLATOR_FILE_NAME):
    """ Replaces nonStandard with Standard values in a list of attributes
    
        Looks for a pattern at the beginning or end of a word, or in the
        middle if surrounded by spaces, and replaces it with a new value
    
    Args: 
        attributes - a list of attributes to do the find and replace in 
        translator_fname - the file to load the translations from
            translator file must have "NonStandard" and "Standard Logical" cols
    
    Returns:
        recoded_attrs - a new list with the replacements done in it
    """
       # load the translator file
    transforms = pd.read_excel(translator_fname )
    transforms['translate tuple'] = list(zip(transforms["NonStandard"], transforms["Standard Logical"]))
    recoded_attrs = attributes
    for transformer in transforms['translate tuple']:
        recoded_attrs = recode_old_new(recoded_attrs,transformer[0], transformer[1])
    return recoded_attrs

def standardize_cosmetic(attributes):
    # Standardize the attribute names
    std_attr = attributes.copy()
    std_attr = remove_underscores(std_attr)
    std_attr = remove_doublespace(std_attr)
    std_attr = remove_lead_trail(std_attr)
    std_attr = standardize_case(std_attr)
    return std_attr

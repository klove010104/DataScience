# -*- coding: utf-8 -*-
"""
From the combined list of models, standardize entity names.
Then score the definitions for the entities, and find a single definition for 
each entity.
Then extract unique entity names and definitions.

Created on Fri Mar  5 19:14:04 2021

@author: klove
"""
import pandas as pd
import VocabChecker as vc
import FilePrepUtils as fp

#MASTER_VOCAB_FILE_NAME = 'C:/Users/klove/Downloads/MasterDDv2.xlsx'

WORKING_DIRECTORY = 'C:\\Users\\klove\\Downloads\\'
ENTITY_NAME_COL = 'Entity Name'
ENTITY_DEFN_COL = 'Entity/Table Definition'
ATTRIBUTE_COL = 'Attribute Name'
ATT_DEFN_COL = 'Attribute/Column Definition'
#TRANSLATOR_FILE_NAME = WORKING_DIRECTORY +  'DD Transforms.xlsx'

COMBINED_MODEL_FILE = 'CombinedModels.xlsx'


def get_models(input_df, colname = ATTRIBUTE_COL):
    '''For each attribute, get a list of models it is in

        Args:
            input_df: DataFrame to check
        
        Returns:  
            odf: pandas DataFrame with 1 row per attribute and 
                list of models that attribute is in
    '''
    odf = pd.DataFrame()
    models = []
    for search_name in input_df[colname].unique():
        # find all the rows where this attribute appears
        temp_df = input_df.loc[input_df[colname] == search_name]
        models =list(temp_df['Model Name'].unique())
        newrow = {colname: search_name, 'Models': models}
        odf = odf.append(newrow, ignore_index=True)   
    return odf

#preprocess_df(input_df, attr_col = ENTITY_NAME_COL, translate_file_name = TRANSLATOR_FILE_NAME):
input_file_name = WORKING_DIRECTORY + COMBINED_MODEL_FILE
input_df =  pd.read_excel(input_file_name)
# only focus on entities
processed_df = pd.DataFrame(input_df, columns=['Model Name', ENTITY_NAME_COL, ENTITY_DEFN_COL, 'Common Entity'])
processed_df = processed_df.dropna(subset=[ENTITY_NAME_COL])
# drop entities where we have marked as not interested
# in other words, only keep rows where it's na
processed_df = processed_df[processed_df['Common Entity'].isna()]
# now standardize the dataset
processed_df = vc.preprocess_df(processed_df, ENTITY_NAME_COL)

merged_df = pd.merge(left=processed_df, 
                     right=get_models(processed_df, ENTITY_NAME_COL), 
                     left_on=ENTITY_NAME_COL, right_on=ENTITY_NAME_COL)

# unique entity/attribute combos
deduped_df = merged_df.drop_duplicates(subset=[ ENTITY_NAME_COL, ENTITY_DEFN_COL])

# Score definitions for consistency across models
#deduped_df['Definition Score1'] = vc.score_definitions(deduped_df, ENTITY_NAME_COL, ENTITY_DEFN_COL)
#deduped_df['Instance Count'] = vc.attribute_count_in_df(deduped_df, ENTITY_NAME_COL)

# see if trimming the definitions will help
deduped_df[ENTITY_DEFN_COL] = deduped_df[ENTITY_DEFN_COL].fillna("")
deduped_df[ENTITY_DEFN_COL] = fp.remove_lead_trail(deduped_df[ENTITY_DEFN_COL])
deduped_df[ENTITY_DEFN_COL] = fp.remove_doublespace(deduped_df[ENTITY_DEFN_COL])
deduped_df = deduped_df.drop_duplicates(subset=[ ENTITY_NAME_COL, ENTITY_DEFN_COL])
deduped_df['Definition Score'] = vc.score_definitions(deduped_df, ENTITY_NAME_COL, ENTITY_DEFN_COL)
deduped_df['Instance Count'] = vc.attribute_count_in_df(deduped_df, ENTITY_NAME_COL)

deduped_df.to_excel(WORKING_DIRECTORY + "MasterEntities.xlsx")

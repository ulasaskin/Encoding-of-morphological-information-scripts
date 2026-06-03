"""
----Generate predictors for linguistic variables----

This script takes the csv files where we quantified the speech features, and aligns those with phoneme onset timepoints
for alignment of the speech features. In this script, we generate predictors related to phonemes(i.e., phoneme onset, surprisal and entropy), 
syllables (i.e., syllable onset), morphemes (i.e., onset, complexity, category),and lexical items (i.e., number, onset, surprisal and entropy). 

"""
#%% load the libraries and determine the input and output folder. 
#input folder is where the last version of the predictor csv file reside
from pathlib import Path
import os
import eelbrain

STIMULUS_DIR = Path("/project/3027013.01/Materials/raw_data/GPT_added/morpheme_onset_added/").expanduser() 
PREDICTOR_DIR = Path("/project/3027013.01/Materials/Predictors/").expanduser() 

#%%first put the phoneme, syllable and morpheme level predictors
list_wav = [f.split('_full')[0] for f in os.listdir(STIMULUS_DIR) if f.endswith('_cohort_model_GPT.csv')]
# print(dur)
for segment in list_wav:
    print(segment)
    segment_table = eelbrain.load.tsv(STIMULUS_DIR / f'{segment}_full_cohort_model_GPT.csv',delimiter=';')

    ds = eelbrain.Dataset({'time': segment_table['phoneme_onset']}, info={'tstop': segment_table[-1, 'phoneme_offset']})
    
    #add phoneme, syllable and morpheme predictors
    
    for key in ['cohort_entropy', 'cohort_surprisal',
                #syllable level predictor
                'syllable_onset', 
                #morpheme level predictors
                'morpheme_onset','complexity',
                #fine-grained morpheme functions
                'cat_1','cat_2','cat_3','cat_4','cat_5','cat_6',
                'cat_7','cat_8','cat_9','cat_10','cat_11','cat_12',
                'cat_13','cat_14','cat_15','cat_16','cat_17','cat_18',
                'cat_19','cat_20','cat_21','cat_22','cat_23','cat_24',
                'cat_25','cat_26','cat_27','cat_28','cat_29','cat_30',
                'cat_31','cat_32','cat_33','cat_34','cat_35','cat_36',
                #grouped-categories
                'grp_1','grp_2','grp_3','grp_4','grp_5',
                'grp_6','grp_7','grp_8','grp_9','grp_10',
                #word-level predictors
                'word_number','word_onset', 
                'word_surprisal_GPT', 'word_entropy_GPT']:
       
        ds[key] = segment_table[key]

    #save
    eelbrain.save.pickle(ds, PREDICTOR_DIR / f'{segment}~phoneme_cohort_model_syllable_morpheme_word_GPT.pickle')
    
#%%check the values just in case
import eelbrain
import pandas as pd

#unpickle the predictor file
ds = eelbrain.load.unpickle('/project/3027013.01/Materials/Predictors/tripod_TR_ex-01~phoneme_cohort_model_syllable_morpheme_word_GPT.pickle')
#print the first 5 row of the predictor file
print(ds[:5])
#check the column names. it should include all of the predictors 
print(ds.keys())

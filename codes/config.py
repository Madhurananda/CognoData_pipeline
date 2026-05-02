#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed May  8 14:17:43 2024

@author: madhupahar
"""

from main import *

import os, sys, glob
import time, json
import pandas as pd
from datetime import datetime
from natsort import natsorted
import numpy as np

from tqdm import tqdm
from natsort import natsorted

from multiprocessing.pool import ThreadPool, Pool
from multiprocessing import cpu_count

from spellchecker import SpellChecker



def make_N_chars_a_val(a, n):
    n_char = (int(n)-len(str(a)))*'0' + str(a)
    return n_char


def make_5_chars(a_list):
    five_char_list = [ (5-len(str(a)))*'0' + str(a) for a in a_list ]
    return five_char_list


def rename_a_file(chng_cmd):
    if os.system(chng_cmd) != 0:
        print('There is something wrong in : ', chng_cmd)


def rename_files_inside(folder, ori_val, new_val):
    
    if os.path.exists(extracted_data_dir+folder): 
        files_inside = glob.glob(extracted_data_dir+folder+'/*')
        
        for i in files_inside:
            
            if ori_val in i: 
            
                new_i = extracted_data_dir+folder+'/' + i.split(extracted_data_dir)[-1].split('/')[-1].replace(ori_val, new_val)
                
                chng_cmd = 'mv {} {}'.format(i, new_i)
                
                rename_a_file(chng_cmd)


def get_json_content(dir_name):
    
    # json_files = glob.glob(extracted_data_dir + o + '/*.json')
    json_files = glob.glob(dir_name + '/*.json')
    
    if len(json_files) > 1:
        print('******** There are more than one json file. CHECK :',  dir_name)
        sys.stdout.flush()
        time.sleep(100000000)
    
    with open(json_files[0], 'r') as f:
        dict_json = json.load(f)
    
    return dict_json


# def amend_df(df_sort, assess_ID, ini_ID, final_ID):
#     # df_part = df_sort[df_sort['Assessment ID'] == assess_ID]
#     # df_part = df_part.replace(ini_ID, final_ID)

#     # # df_sort[df_sort['Assessment ID'] == 'c18e1eb5-6650-4a78-9623-8847b5839e39']['Research ID'].values[0] 


#     # df_sort = df_sort.loc[df_sort["Assessment ID"] != assess_ID]


#     # final_df = pd.concat([df_sort, df_part], axis=0)
    
#     df_sort.loc[( df_sort[df_sort['Assessment ID'] == assess_ID].index.item(), 'Research ID' )] = final_ID
    
#     return df_sort



# def amend_final_df(df_xls_summary, df_xls_demographics, df_xls_assess, df_PHQ, df_GAD):
#     df_xls_summary = amend_df(df_xls_summary, assess_ID, ini_ID, final_ID)
#     df_xls_demographics = amend_df(df_xls_demographics, assess_ID, ini_ID, final_ID)
#     df_xls_assess = amend_df(df_xls_assess, assess_ID, ini_ID, final_ID)
#     df_PHQ = amend_df(df_PHQ, assess_ID, ini_ID, final_ID)
#     df_GAD = amend_df(df_GAD, assess_ID, ini_ID, final_ID)
    
#     # df_xls_demographics[df_xls_demographics['Research ID']==final_ID]
#     # df_PHQ[df_PHQ['Research ID']==final_ID]
    
#     return df_xls_summary, df_xls_demographics, df_xls_assess, df_PHQ, df_GAD


def amend_df_json(df_sort, assess_ID, ini_ID, final_ID):
    # df_part = df_sort[df_sort['assessment_ID'] == assess_ID]
    # df_part = df_part.replace(ini_ID, final_ID)
    
    # df_sort[df_sort['Assessment ID'] == 'c18e1eb5-6650-4a78-9623-8847b5839e39']['Research ID'].values[0] 
    
    df_sort.loc[( df_sort[df_sort.assessment_ID == assess_ID].index.item(), 'research_ID' )] = final_ID
    
    # df_sort = df_sort.loc[df_sort["assessment_ID"] != assess_ID]
    
    # final_df = pd.concat([df_sort, df_part], axis=0)
    return df_sort


def do_exec_cmd(cmd):
    if_faluty = 0
    if os.system(cmd) != 0:
        print('\n\nThis command did not execute successfully: ', cmd)
        sys.stdout.flush()
        if_faluty = 1
        
    return if_faluty



## a_file: file to be copied 
## dest: destination folder
## if_m_dest: modify the destination directory and make a new directory 
## overwrite: if 1 then it will overwrite 
def do_copy(args):
    
    a_file, dest, if_m_dest, overwrite = args[0], args[1], args[2], args[3]
    
    if_faluty = 0
    
    # print('a_file : ', a_file)
    # sys.stdout.flush()
    # time.sleep(100000000)
    
    folder = a_file.split('/')[ len(a_file.split('/'))-2 ]
    
    if if_m_dest == 1:
        
        dest_dir = dest + '/' + folder
        
        if not os.path.isdir(dest_dir):
            os.mkdir(dest_dir)
        
    elif if_m_dest == 0:
        dest_dir = dest
    
    copy_cmd = 'cp {} {}'.format( a_file, dest_dir)
    # copy_cmd = 'rsync -rlptDvh --inplace {} {}'.format( a_file, dest_dir)
    # copy_cmd = 'rsync --inplace {} {}'.format( a_file, dest_dir)
    
    # print('copy_cmd : ', copy_cmd)
    # sys.stdout.flush()
    # time.sleep(100000000)
    
    ## Check if the files exist .... 
    if overwrite == 0:
        # if os.path.exists(dest_dir + '/' + a_file.split('/')[-1]):
        #     print('the file exists ... ', a_file.split('/')[-1])
            
        # else:
        #     if_faluty = do_exec_cmd(copy_cmd)
        
        if not os.path.exists(dest_dir + '/' + a_file.split('/')[-1]):
            if_faluty = do_exec_cmd(copy_cmd)
        # else:
        #     print('the file exists ... ', a_file.split('/')[-1])
        
    ## Copy everything ... 
    else:
        if_faluty = do_exec_cmd(copy_cmd)
    
    # sys.stdout.flush()
    # time.sleep(100000000)
    
    return if_faluty, folder


def do_copy_rename(args):
    
    a_file, dest, ext = args[0], args[1], args[2]
    
    if_faluty = 0
    
    # print('a_file : ', a_file)
    # sys.stdout.flush()
    # time.sleep(100000000)
    
    folder = a_file.split('/')[ len(a_file.split('/'))-2 ]
    
    dest_dir = dest + '/' + folder
    if not os.path.isdir(dest_dir):
        os.mkdir(dest_dir)
    
    if '_Q10'+ext in a_file: 
        dest_file = dest_dir +'/'+ a_file.split('_Q10'+ext)[0].split('/')[-1]+'__SFT'+ext
    elif '_Q11'+ext in a_file: 
        dest_file = dest_dir +'/'+ a_file.split('_Q11'+ext)[0].split('/')[-1]+'__PFT'+ext
    elif '_Q12'+ext in a_file: 
        dest_file = dest_dir +'/'+ a_file.split('_Q12'+ext)[0].split('/')[-1]+'__CTD'+ext
    
    # dest_file = dest_dir +'/'+ a_file.split('/')[-1]
    
    # print('a_file: ', a_file)
    # print('dest_file : ', dest_file)
    
    
    
    copy_cmd = 'cp {} {}'.format( a_file, dest_file)
    
    # copy_cmd = 'rsync -rlptDvh -P --stats {} {}'.format( a_file, dest_file)
    
    
    # os.system(copy_cmd)
    
    print('copy_cmd : ', copy_cmd)
    # sys.stdout.flush()
    # time.sleep(100000000)
    
    
    if os.system(copy_cmd) != 0:
        print('This command did not execute successfully: ', copy_cmd)
        sys.stdout.flush()
        if_faluty = 1
    
    
    return if_faluty, folder


def do_copy_simple(cp_cmd):
    if os.system(cp_cmd) != 0:
        print('This command did not execute successfully: ', cp_cmd)
        sys.stdout.flush()


def gen_the_date(dd, mm, yy):
    if len(yy) == 2:
        the_date = datetime.strptime( '20'+yy+'-'+mm+'-'+dd, '%Y-%m-%d')
    elif len(yy) == 4:
        the_date = datetime.strptime( yy+'-'+mm+'-'+dd, '%Y-%m-%d')
    else:
        print('There is something wrong with the date.')
        
    return the_date

## Here, i is the ZIP file name 
def get_date_4M_file(i):
    
    # dd = i.split('__')[-1].split('_')[0][4:6]
    # mm = i.split('__')[-1].split('_')[0][2:4] 
    # yy = i.split('__')[-1].split('_')[0][0:2]
    
    if len(i.split('_')) == 5:
        dd = i.split('_')[3][4:6]
        mm = i.split('_')[3][2:4] 
        yy = i.split('_')[3][0:2]
        
    elif len(i.split('_')) == 4:
    
        dd = i.split('_')[2][4:6]
        mm = i.split('_')[2][2:4] 
        yy = i.split('_')[2][0:2]
    else:
        print('There is something wrong with the _ char in : ', i)
        sys.stdout.flush()
        time.sleep(100000000)
    # the_date = datetime.strptime( '20'+yy+'-'+mm+'-'+dd, '%Y-%m-%d')
    
    # return the_date
    
    return gen_the_date(dd, mm, yy)



def gen_csv_xls(xls_file, csv_xls_file, sh_name):
    df_xls = pd.read_excel(xls_file, sheet_name=sh_name)
    
    df_xls = df_xls[df_xls['Research ID'].notna()]
    
    df_xls['Research ID'] = df_xls['Research ID'].astype(int)
    
    df_xls.to_csv(csv_xls_file, index=False)
    return df_xls


def check_process_csv(xls_file, sh_name):
    
    csv_xls_file = xls_file.split('.xlsx')[0] + '__' + sh_name + '.csv'
    
    ## Check if the csv file exists 
    if os.path.exists(csv_xls_file):
        ## If it does exist, check if the Excel file newer than the csv file or not 
        ## If it is, then recreate the csv file 
        if os.path.getmtime(xls_file) > os.path.getmtime(csv_xls_file):
            # print('CSV file exists, but is older. Regenerating it: ', csv_xls_file)
            df_xls = gen_csv_xls(xls_file, csv_xls_file, sh_name)
        ## Otherwise, read from the exisiting CSV file 
        else:
            # print('Reading from the CSV file: ', csv_xls_file)
            df_xls = pd.read_csv(csv_xls_file)
    ## Otherwise, recreate the csv file 
    else:
        # print('CSV file does not exist. Generating it: ', csv_xls_file)
        df_xls = gen_csv_xls(xls_file, csv_xls_file, sh_name)
    
    return df_xls







def gen_csv_json(json_file, csv_json_file):
    
    with open(json_file, 'r') as f:
        dict_json = json.load(f)
    
    df_meta = pd.DataFrame([], columns=['research_ID', 'assessment_ID', 'diagnosis', 'referral', 'N_results', 'assessment_type', 'assess_date'])
    
    
    
    # for key in dict_json['cognomndAssessments']:
    #     # print(key)
        
    #     for ass_ID in dict_json['cognomndAssessments'][key]:
            
    #         if ass_ID == 'fb799f45-ceee-4104-81ab-0a525bb70294':
                
    #             print(key)
    #             print(ass_ID)
    
    
    
    main_keys = ['assessments', 'cognomndAssessments', 'cognostrokeAssessments']
    
    for m_keys in main_keys:
        
        for key in dict_json[m_keys]:
            
            for ass_ID in dict_json[m_keys][key]:
                
                if 'id' in dict_json[m_keys][key][ass_ID]:
                    
                    
                    if ass_ID != dict_json[m_keys][key][ass_ID]['id']:
                        print('Check this ID : ', ass_ID)
                        sys.stdout.flush()
                        time.sleep(100000000)
                    
                    
                    
                    if 'results' in dict_json[m_keys][key][ass_ID]['assessment']:
                        
                        r_ID = dict_json[m_keys][key][ass_ID]['patient']['profile']['researchNumber']
                        
                        # print('ass_ID: ', ass_ID)
                        json_referral = dict_json[m_keys][key][ass_ID]['patient']['profile']['referralSource']
                        
                        # print('ass_ID: ', ass_ID)
                        # for a_key in dict_json[m_keys][key][ass_ID]['assessment']:
                        #     print(a_key)
                        # sys.stdout.flush()
                        # time.sleep(100000000)
                        
                        if 'taskEntityId' in dict_json[m_keys][key][ass_ID]['assessment']:
                        
                            assess_type = dict_json[m_keys][key][ass_ID]['assessment']['taskEntityId']
                        else:
                            assess_type = NO_EXIST_STR
                        
                        
                        if 'taskCompletedAt' in dict_json[m_keys][key][ass_ID]:
                        
                            assess_date = datetime.strptime( dict_json[m_keys][key][ass_ID]['taskCompletedAt'].split('T')[0], '%Y-%m-%d')
                            
                        else:
                            assess_date = NO_EXIST_STR
                        
                        
                        json_diagnosis = ''
                        
                        for a_key in dict_json[m_keys][key][ass_ID]['patient']['profile']['diagnosis']:
                            
                            if a_key == 'reason':
                                if dict_json[m_keys][key][ass_ID]['patient']['profile']['diagnosis'][a_key] == 'healthy volunteer':
                                    json_diagnosis = 'HC'
                            
                            elif dict_json[m_keys][key][ass_ID]['patient']['profile']['diagnosis'][a_key] == True:
                                # print(dict_json['patient']['profile']['diagnosis'][a_key])
                                # print(a_key)
                                
                                if a_key == 'dementia':
                                    json_diagnosis = 'Dementia'
                                elif a_key == 'functionalMovementDisorder':
                                    json_diagnosis = 'FMD'
                                elif a_key == 'functionalMemoryDisorder':
                                    json_diagnosis = 'FCD'
                                elif a_key == 'mildCognitiveImpairment':
                                    json_diagnosis = 'MCI'
                                
                                elif a_key == 'motorNeuroneDisease':
                                    json_diagnosis = 'MND'
                                
                                elif a_key == 'stroke':
                                    json_diagnosis = 'Stroke'
                        
                        
                        
                        df_meta.loc[len(df_meta.index)] = [r_ID] + [ass_ID] + [json_diagnosis] + [json_referral] + [len(dict_json[m_keys][key][ass_ID]['assessment']['results'])] + [assess_type] + [assess_date]
    
    
    
    df_meta.to_csv( csv_json_file, index=False )
    
    
    
    return df_meta



def check_process_json(json_file):
    
    csv_json_file = json_file.split('.json')[0] + '__metadata.csv' 
    
    ## Check if the csv file exists 
    if os.path.exists(csv_json_file):
        ## If it does exist, check if the JSON file newer than the csv file or not 
        ## If it is, then recreate the csv file 
        if os.path.getmtime(json_file) > os.path.getmtime(csv_json_file):
            # print('CSV file exists, but is older. Regenerating it: ', csv_xls_file)
            df_json = gen_csv_json(json_file, csv_json_file)
        ## Otherwise, read from the exisiting CSV file 
        else:
            # print('Reading from the CSV file: ', csv_xls_file)
            df_json = pd.read_csv(csv_json_file)
    ## Otherwise, recreate the csv file 
    else:
        # print('CSV file does not exist. Generating it: ', csv_xls_file)
        df_json = gen_csv_json(json_file, csv_json_file)
    
    return df_json





def get_dupl_df(df, col_name):
    ids = df[col_name]
    df_dupl = df[ids.isin(ids[ids.duplicated()])].sort_values(col_name)
    df_unique = df.drop_duplicates(subset=[col_name], keep=False, inplace=False)
    
    return df_dupl, df_unique




def get_metadata():
    '''
    Reading the spreadsheet which was created in CognoSpeak_3_check_final.py 
    at final_metadata_path
    '''
    df_METADATA = pd.read_csv( final_metadata_path )
    
    df_metadata = df_METADATA.loc[ (df_METADATA["assessment_ID"] != 'N_all_ANSs') & (df_METADATA["assessment_ID"] != 'SPRDSHT__NOT_TRANS') & (df_METADATA["assessment_ID"] != 'TRANS__NOT_SPRDSHT') & (df_METADATA["assessment_ID"] != 'TEST_IDs') ]
    
    
    df_metadata.reset_index(drop=True, inplace=True)
    
    return df_metadata

def get_pseudo_IDs(df, if_final_sort, sort_col):
# def get_pseudo_IDs(df, if_final_sort):
    ## This cerates the unique IDs for each column 
    
    
    df_dupl, df_unq = get_dupl_df(df, 'research_ID')
    
    
    # ## just a sanitiy check ... 
    
    # find_values_counts( df_metadata_dupl.assessment_ID, 1 )
    
    # df_metadata_dupl[df_metadata_dupl.assessment_ID == '3f09a0d7-8ad0-4725-ae65-fbfe32b49b7d']
    
    # df_metadata_dupl[df_metadata_dupl.assessment_ID == 'ab70d80c-8f5e-4ce6-8770-c4398dc6f33e']
    
    
    df_dupl_final = pd.DataFrame([], columns=df_dupl.columns.insert(1, 'pseudo_unq_id'))
    
    for i_d in natsorted(set(df_dupl.research_ID)):
        if if_final_sort == 1: 
            # df_temp = df_dupl[df_dupl.research_ID == i_d].sort_values('ASSESS_GAPS_days')
            df_temp = df_dupl[df_dupl.research_ID == i_d].sort_values(sort_col)
        else:
            df_temp = df_dupl[df_dupl.research_ID == i_d]
        df_temp.insert(1, 'pseudo_unq_id', [ make_N_chars_a_val(df_temp.research_ID.values[0], 5) + '_' + str(i+1) for i in range(len(df_temp)) ])
        
        df_dupl_final = pd.concat([df_dupl_final, df_temp], ignore_index=True)
    
    
    
    df_unq.insert(1, 'pseudo_unq_id', [ i + '_' + str(1) for i in make_5_chars(list(df_unq.research_ID)) ])
    
    if if_final_sort == 1: 
        df_FINAL = pd.concat([df_unq, df_dupl_final], ignore_index=True).sort_values(['research_ID', sort_col])
    else:
        df_FINAL = pd.concat([df_unq, df_dupl_final], ignore_index=True)
    
    return df_FINAL


def drop_df_cols(df):
    # df.reset_index(drop=True, inplace=True)
    cmd = 'df.drop(columns=['
    
    for i in range(14):
        
        cmd += '\'Q' + str(i+1) + '\', '
    
    cmd = cmd[0:len(cmd)-2] + '], inplace=True)'
    
    exec(cmd)
    
    return df



def do_get_ZIP_4M_logs(a_list):
    file_ID_list = []
    r_ID_list = []
    for a_file in a_list:
        if a_file.endswith('.zip') and 'undefined' not in a_file:
            file_ID = a_file.split('/')[-1].split('.zip')[0]
            
            if file_ID.startswith('STROKE_') or file_ID.startswith('MND_'):
                # print(file_ID)
                if len(file_ID.split('_')) == 6 and file_ID.split('_')[2] != '':
                    # r_ID = file_ID.split('_')[1]
                    r_ID_list.append(int(file_ID.split('_')[2]))
                    file_ID_list.append(file_ID)
                    
            else:
                if len(file_ID.split('_')) == 5 and file_ID.split('_')[1] != '':
                    # r_ID = file_ID.split('_')[1]
                    r_ID_list.append(int(file_ID.split('_')[1]))
                    file_ID_list.append(file_ID)
    return file_ID_list, r_ID_list



### This is for two way classifications 
def prep_labels_2_WAY(df_metadata):
    
    if 'labels' in df_metadata.columns:
        df_metadata = df_metadata.drop(['labels'], axis=1)
    
    
    df_meta_final = df_metadata.reset_index(drop=True)
    
    df_meta_final['labels'] = df_meta_final['diagnosis']
    
    df_meta_final.loc[df_meta_final.labels == 'HC', 'labels'] = 0
    
    df_meta_final.loc[df_meta_final.labels == 'MCI', 'labels'] = 1
    
    
    for a_cat in DEM_CAT:
        df_meta_final.loc[df_meta_final.labels == a_cat, 'labels'] = 1
    
    for a_cat in UNKN_CAT:
        df_meta_final.loc[df_meta_final.labels == a_cat, 'labels'] = -1
    
    if not all(isinstance(x, int) for x in list(set(df_meta_final.labels))):
        
        print('Not all diagnosis has been considered for labels. CHECK ... ')
        print(df_meta_final.labels.value_counts())
        sys.stdout.flush()
        time.sleep(100000000)
    
    return df_meta_final



### This is for three way classifications 
def prep_labels_3_WAY(df_metadata):
    
    if 'labels' in df_metadata.columns:
        df_metadata = df_metadata.drop(['labels'], axis=1)
    
    df_meta_final = df_metadata.reset_index(drop=True)
    
    df_meta_final['labels'] = df_meta_final['diagnosis']
    
    df_meta_final.loc[df_meta_final.labels == 'HC', 'labels'] = 0
    
    df_meta_final.loc[df_meta_final.labels == 'MCI', 'labels'] = 1
    
    for a_cat in DEM_CAT:
        df_meta_final.loc[df_meta_final.labels == a_cat, 'labels'] = 2
    
    for a_cat in UNKN_CAT:
        df_meta_final.loc[df_meta_final.labels == a_cat, 'labels'] = -1
    
    if not all(isinstance(x, int) for x in list(set(df_meta_final.labels))):
        
        print('Not all diagnosis has been considered for labels. CHECK ... ')
        print(df_meta_final.labels.value_counts())
        sys.stdout.flush()
        time.sleep(100000000)
    
    
    return df_meta_final



def sort_out_ethnicity(df):
    
    df.loc[df.ethnicity == 'White British', 'ethnicity'] = 'ENGLISH WHITE'
    df.loc[df.ethnicity == 'English, Welsh, Scottish, Northern Irish or British', 'ethnicity'] = 'ENGLISH WHITE'
    
    df.loc[df.ethnicity == 'White Irish', 'ethnicity'] = 'IRISH WHITE'
    df.loc[df.ethnicity == 'Irish', 'ethnicity'] = 'IRISH WHITE'
    
    df.loc[df.ethnicity == 'Other White', 'ethnicity'] = 'OTHER WHITE'
    df.loc[df.ethnicity == 'Any other White background', 'ethnicity'] = 'OTHER WHITE'
    
    df.loc[df.ethnicity == 'Unknown', 'ethnicity'] = 'UNKNOWN'
    df.loc[df.ethnicity == 'Undisclosed', 'ethnicity'] = 'UNKNOWN'
    df.loc[df.ethnicity == 'Any other ethnic group', 'ethnicity'] = 'UNKNOWN'
    
    df.loc[df.ethnicity == 'Pakistani', 'ethnicity'] = 'ASIAN'
    df.loc[df.ethnicity == 'Chinese', 'ethnicity'] = 'ASIAN'
    df.loc[df.ethnicity == 'Indian', 'ethnicity'] = 'ASIAN'
    df.loc[df.ethnicity == 'Other Asian', 'ethnicity'] = 'ASIAN'
    df.loc[df.ethnicity == 'Any Other Asian', 'ethnicity'] = 'ASIAN'
    df.loc[df.ethnicity == 'Bangladeshi', 'ethnicity'] = 'ASIAN'
    df.loc[df.ethnicity == 'Arab', 'ethnicity'] = 'ASIAN'
    
    df.loc[df.ethnicity == 'Black African', 'ethnicity'] = 'BLACK'
    df.loc[df.ethnicity == 'Black Caribbean', 'ethnicity'] = 'BLACK'
    df.loc[df.ethnicity == 'African', 'ethnicity'] = 'BLACK'
    df.loc[df.ethnicity == 'Any other Black, Black British, or Caribbean background', 'ethnicity'] = 'BLACK'
    df.loc[df.ethnicity == 'Caribbean', 'ethnicity'] = 'BLACK'
    
    df.loc[df.ethnicity == 'Mixed: White & Asian', 'ethnicity'] = 'MIXED'
    df.loc[df.ethnicity == 'Mixed: Other', 'ethnicity'] = 'MIXED'
    df.loc[df.ethnicity == 'White and Asian', 'ethnicity'] = 'MIXED'
    df.loc[df.ethnicity == 'Mixed: White & Black African', 'ethnicity'] = 'MIXED'
    df.loc[df.ethnicity == 'Any other Mixed or multiple ethnic background', 'ethnicity'] = 'MIXED'
    df.loc[df.ethnicity == 'White & Black Caribbean', 'ethnicity'] = 'MIXED'
    df.loc[df.ethnicity == 'Mixed: White & Black Caribbean', 'ethnicity'] = 'MIXED'
    
    df.loc[df.ethnicity == 'Other', 'ethnicity'] = 'OTHER'
    
    return df



def make_all_HC(df, ReF):
    
    # df.diagnosis = 'HC'
    
    df = df.drop(['diagnosis'], axis=1)
    
    # df.diagnosis = ['HC']*len(df)
    # df.referral = [ReF]*len(df)
    
    
    df.insert(len(df.columns), 'diagnosis', ['HC']*len(df))
    df.insert(len(df.columns), 'sort_ethnicity', [ReF]*len(df))
    
    
    
    # if len(df[df.diagnosis == 'HC']) != len(df):
    #     df.loc[( df[df.diagnosis != 'HC'].index.item(), 'diagnosis' )] = 'HC'
    
    # if len(df[df.referral == ReF]) != len(df):
    #     df.loc[( df[df.referral != ReF].index.item(), 'referral' )] = ReF
    
    # df.referral = ReF
    return df


## I will NOT use this as this was the wrong way of calculating SNR
# def signaltonoise_dB(a, axis=0, ddof=0):
#     a = np.asanyarray(a)
#     m = a.mean(axis)
#     sd = a.std(axis=axis, ddof=ddof)
#     return 20*np.log10(abs(np.where(sd == 0, 0, m/sd)))



'''
I was informed by Simon on 02/OCT/2025, that some HC can come from CognoStroke and they will have () in their surnames 

These are the ones by Rithika ... 

Research number: 81574, Last assessed on: 25/06/25
Research number: 65848, Last assessed on: 18/07/25
Research number: 59916, Last assessed on: 04/07/25
Research number: 00321, Last assessed on: 23/06/25
Research number: 97785, Last assessed on: 01/07/25 
Research number: 95930, Last assessed on: 04/07/25
Research number: 13682, Last assessed on: 17/07/25
Research number: 22207, Last assessed on: 16/07/25

'''

def PREP_FINAL_METADATA(df):
    
    ## Remove the multiple sclerosis ones from Rithika 
    
    r_ID_rithika = [81574, 65848, 59916, 321, 97785, 13682, 22207, 95930]
    
    df = df[~df.research_ID.isin(r_ID_rithika)]
    
    
    
    ## Remove the surnames with () in it ... 
    
    df_meta_ALL = pd.read_csv( ACE_out_all_ACE )
    
    to_excld_dirs = []
    for ind in df_meta_ALL.index:
        
        
        if '(' in df_meta_ALL['LastName'][ind]: 
            # print(df_meta_ALL['LastName'][ind])
            
            to_excld_dirs.append( df_meta_ALL['dir_name'][ind] )
    
    
    df = df[~df.dir_name.isin(to_excld_dirs)]
    
    # df[df.dir_name == 'R_38575_250711_143837'].assessment_type
    
    
    ## Finally, remove the space for referrals ... 
    df['referral'] = df['referral'].str.rstrip()
    
    
    return df




def do_copy_sorc_dest(source, dest, ext, dirs_to_copy, OVRWT, N_jobs):
    
    # print('dirs_to_copy : ', dirs_to_copy)
    
    if type(source) == list:
        print('Getting all the files inside the source for the extension: ', ext)
        files_4_trans = []
        for a_dir in tqdm(dirs_to_copy):
            
            files_4_trans.extend( [os.path.join(root, name)
                      for root, dirs, files in os.walk(a_dir)
                      for name in files
                      if name.endswith(ext)])
        
    elif type(source) == str:
        print('Getting all the files inside the source: ', source, ' for the extension: ', ext)
        files_4_trans = [os.path.join(root, name)
                  for root, dirs, files in os.walk(source)
                  for name in files
                  if name.endswith(ext)]
    else:
        print('The source type is wrong, check .... ')
        sys.stdout.flush()
        time.sleep(100000000)
        
    print('There are ', len(files_4_trans), ' files to be copied.')
    sys.stdout.flush()
    
    
    
    # #############################################
    # ## This is using SINGLE CPU ... 
    # for a_file in files_4_trans:
        
    #     dest_dir = dest + '/' + a_file.split('/')[ len(a_file.split('/'))-2 ]
        
    #     if not os.path.isdir(dest_dir):
    #         os.mkdir(dest_dir)
        
    #     copy_cmd = 'cp {} {}'.format( a_file, dest_dir)
        
    #     print('copy_cmd : ', copy_cmd)
        
    #     os.system(copy_cmd)
    #############################################
    
    
    
    #############################################
    ## This is using multiple CPU ... 
    
    files_NOT_copied = []
    
    
    inputs = zip(natsorted(files_4_trans), [dest]*len(files_4_trans), [1]*len(files_4_trans), [OVRWT]*len(files_4_trans))
    
    n_jobs = min(N_jobs, len(files_4_trans))
    print('n_jobs: ', n_jobs)
    sys.stdout.flush()
    
    
    
    results = tqdm(Pool(n_jobs).imap_unordered(do_copy, inputs), total=len(files_4_trans))
    
    for result in results:
        if result[0] == 1:
            # c_incomplete_pats += 1
            files_NOT_copied.append(result[1])
        
        
    #############################################
    
    print('\n\nFiles was not copied: ', files_NOT_copied)
    print('Number of files NOT copied: ', len(files_NOT_copied))
    sys.stdout.flush()



def get_all_data_info(df, Ref):
    print('\n\n****')
    print(Ref, '::: ')
    print('Total subject:', len(df))
    print('Mean Age: ', round(np.mean(df.age), 2))
    print('SD Age: ', round(np.std(df.age), 2))
    print('Gender distribution: ', df.gender.value_counts())
    print('MMSE numbers: ', len(df[df['MMSE'].notna()]))
    print('\n')
    sys.stdout.flush()
    
    all_q_lists = ['Q'+str(i) for i in range(1, 15)]
    
    
    get_audio_text_info(df, all_q_lists, 'ALL')
    get_audio_text_info(df, ['Q4', 'Q5', 'Q6', 'Q7', 'Q8'], 'MEMORY')
    get_audio_text_info(df, ['Q10', 'Q11'], 'FLUENCY')
    get_audio_text_info(df, ['Q12', 'Q13'], 'PDT')



def get_audio_text_info(df, Q_list_2_consider, LABEL):
    
    print('Starting for: ', LABEL)
    
    tot_audio  = 0
    tot_txt_whis = 0
    tot_txt_W2V2 = 0
    tot_txt_Nemo = 0
    
    for a_Q in Q_list_2_consider:
        print()
        
        df[a_Q] = df[a_Q].astype('float')
        tot_audio += round(sum(df[a_Q])/(60*60), 2)
        
        print('The total length of audio for ', a_Q,  ' is: ', round(sum(df[a_Q])/(60*60), 2), ' hr.')
        
        
        
        tot_word_C_Whps = 0
        tot_word_C_W2V2 = 0
        tot_word_C_Nemo = 0
        
        for ind in df.index:
            
            try:
                
                if len(df['dir_name'][ind].split('_')) == 5:
                    
                    txt_cont = read_file(ASR_trans_out_whp_med_44kHz + df['dir_name'][ind] + '/' + df['dir_name'][ind].replace(df['dir_name'][ind].split('_')[0]+'_', '') + '_' + a_Q + '.txt')
                
                elif len(df['dir_name'][ind].split('_')) == 4:
                    
                    txt_cont = read_file(ASR_trans_out_whp_med_44kHz + df['dir_name'][ind] + '/' + df['dir_name'][ind] + '_' + a_Q + '.txt')
                    
                else:
                    print('There is somethong wrong with the dir name: ', df['dir_name'][ind])
                    sys.stdout.flush()
                    time.sleep(100000000)
                
            except:
                txt_cont = ''
            tot_word_C_Whps += len(txt_cont.split())
            
            
            
            
            try:
                
                if len(df['dir_name'][ind].split('_')) == 5:
                    
                    txt_cont = read_file(ASR_trans_out_wav2vec2_16kHz + df['dir_name'][ind] + '/' + df['dir_name'][ind].replace(df['dir_name'][ind].split('_')[0]+'_', '') + '_' + a_Q + '.txt')
                
                elif len(df['dir_name'][ind].split('_')) == 4:
                    
                    txt_cont = read_file(ASR_trans_out_wav2vec2_16kHz + df['dir_name'][ind] + '/' + df['dir_name'][ind] + '_' + a_Q + '.txt')
                    
                else:
                    print('There is somethong wrong with the dir name: ', df['dir_name'][ind])
                    sys.stdout.flush()
                    time.sleep(100000000)
                
            except:
                txt_cont = ''
            tot_word_C_W2V2 += len(txt_cont.split())
            
            
            
            
            
            try:
                
                if len(df['dir_name'][ind].split('_')) == 5:
                    
                    txt_cont = read_file(ASR_trans_out_nemo_16kHz + df['dir_name'][ind] + '/' + df['dir_name'][ind].replace(df['dir_name'][ind].split('_')[0]+'_', '') + '_' + a_Q + '.txt')
                
                elif len(df['dir_name'][ind].split('_')) == 4:
                    
                    txt_cont = read_file(ASR_trans_out_nemo_16kHz + df['dir_name'][ind] + '/' + df['dir_name'][ind] + '_' + a_Q + '.txt')
                    
                else:
                    print('There is somethong wrong with the dir name: ', df['dir_name'][ind])
                    sys.stdout.flush()
                    time.sleep(100000000)
                    
            except:
                txt_cont = ''
            tot_word_C_Nemo += len(txt_cont.split())
            
            
            
            
        
        print('Whisper total numebr of words for ', a_Q,  ' is: ', round((tot_word_C_Whps/1000), 2))
        print('W2V2 total numebr of words for ', a_Q,  ' is: ', round((tot_word_C_W2V2/1000), 2))
        print('Nemo total numebr of words for ', a_Q,  ' is: ', round((tot_word_C_Nemo/1000), 2))
        tot_txt_whis +=tot_word_C_Whps
        tot_txt_W2V2 +=tot_word_C_W2V2
        tot_txt_Nemo +=tot_word_C_Nemo
        print()
        sys.stdout.flush()
    
    print('TOTAL audio: ', round(tot_audio, 2))
    print('TOTAL Whisper text: ', round((tot_txt_whis/1000), 2))
    print('TOTAL W2V2 text: ', round((tot_txt_W2V2/1000), 2))
    print('TOTAL Nemo text: ', round((tot_txt_Nemo/1000), 2))

    print('Ending for: ', LABEL)
    print('******\n')
    sys.stdout.flush()


# --- Spell correction ---
# def correct_word(word):
#     # Only correct if word is unknown (not in dictionary)
#     if word not in spell:
#         return spell.correction(word)
#     else:
#         return word

def correct_word(word):
    
    # If word is already known to spellchecker, keep it
    if word in spell:
        return word

    suggestion = spell.correction(word)

    # Only use suggestion if it's not None
    if suggestion is not None:
        return suggestion

    # Otherwise keep original word
    return word



startTime = datetime.now()
current_time = startTime.strftime("%Y/%m/%d at %H:%M:%S")
print('\n\nThe script starting at: ' + str(current_time), ' \n\n' )

spell = SpellChecker()

NO_EXIST_STR = 'XX'

## There have also been situations where I needed to ignore some assessments ... 
## Some of these assessments do not appear on the portal and has been mentioned on the tracker, on 28/11/2024
## Make sure to add '__' here ... 
to_ignore_assessments = ['R_32882__241010_140101', 'R_32882__241107_154458', 'R_03749__241126_134803', 'R_72014__241126_141640', 'R_45234__240603_120827', 'S_23974__240405_170053', 'S_23974__240405_123053', 'S_992397499__240405_123053', 'R_84513__240814_104736', 'R_998451399__240814_104736', 'R_25600__240515_193138', 'R_01541__240227_100039', 'MND_S_23376__240406_214245', 'MND_S_95500__231128_135609', 'MND_R_74765__231116_225719', 'R_74765__231116_225719', 'MND_R_90271__230820_173909', 'R_90271__230820_173909', 'MND_R_90271__230820_191853', 'R_90271__230820_191853', 'MND_R_90271__230630_160645', 'MND_R_90271__230820_185128', 'S_13638__250811_113706', 'R_38885__240902_124951', 'R_19186__240709_164535', 'R_52107__240810_161141']

cloud_base = 'gs://cognospeak-production.appspot.com/production'
raw_data_dir = '../data/raw_data/'
extracted_data_dir = '../data/EXTRACTED_RAW_DATA/'
extracted_data_dir_temp_dir = '../data/EXTRACTED_RAW_DATA_TEMP/'
extracted_data_dir_backup_dir = '../data/EXTRACTED_RAW_DATA_BACKUP/'
final_extract_dir = '../data/FINAL_EXTRACTED_AUDIO/'
final_ext_16kHz_dir = '../data/FINAL_EXT_AUDIO_16kHz/'
final_transcript_dir = '../data/FINAL_transcript_ready/'
# final_transcript_share = '../data/FINAL_transcript_FINAL_SHARE/'

MAX_LEN_MEDIA_FILES = 20

test_ID_out_csv = '../data/CognoSpeak_TEST_IDs.csv'
dir_media_info_out = '../data/CognoSpeak_2__dir_media_info.csv' 
# out_troubled_none_answers_IDs = '../data/CognoSpeak_2__no_answers_IDs_ZIPs.csv' 
# out_troubled_not_all_answers_IDs = '../data/CognoSpeak_2__not_all_answers_IDs.csv' 
# out_troubled_IDs_sprsht_NTNzip = '../data/CognoSpeak_2__IDs_sprsht_NTNzip.csv'
# out_troubled_IDs_RAWzip_NTNsprsht = '../data/CognoSpeak_2__IDs_RAWzip_NTNsprsht.csv'
# out_troubled_IDs_zip_NTNsprsht = '../data/CognoSpeak_2__IDs_zip_NTNsprsht.csv'
# out_missing_assess_ZIPs = '../data/CognoSpeak_2__assess_missing_ZIP.csv'
# out_missing_assess_xls = '../data/CognoSpeak_2__assess_missing_xls.csv'
out_missing_assess = '../data/CognoSpeak_2__assess_missing.csv'


IDs_with_mult_diag_refs_path = '../data/CognoSpeak_3__SPREADSHEET_diag_ref_mismatch.csv'
ID_issues_path = '../data/CognoSpeak_3__SPREADSHEET_JSON_mismatch.csv'
final_metadata_path = '../data/CognoSpeak_FINAL_METADATA.csv'
duplicated_ids_out = '../data/CognoSpeak_3_possible_duplicates.csv'


ids_to_remove_out = '../data/CognoSpeak_4__ID_remove.csv'
duplicates_confirmed_out = '../data/CognoSpeak_4__duplicates_confirmed_script.csv'
duplicates_TO_confirm_out = '../data/CognoSpeak_4__duplicates_TO_BE_confirmed.csv'
duplicates_FINAL_confirmed_out = '../data/CognoSpeak_4__duplicates_FINAL_confirmed.csv'
duplicates_FINAL_confirmed_out_FINAL = '../data/CognoSpeak_4__duplicates_FINAL_confirmed_FINAL.csv'
temp_ST_MND_save_out = '../data/CognoSpeak_4__temp_Stroke_MND.csv'


sorted_follow_up_out = '../data/CognoSpeak_5__sorted_followUP.csv'
sorted_followUP_all_out = '../data/CognoSpeak_5__sorted_all.csv'
to_check_follow_ups_out = '../data/CognoSpeak_5__follow_up_CHECK.csv'
final_sorted_CognoSpeak_metadata = '../data/CognoSpeak_5__FINAL_METADATA.csv'


# final_metadata_2_share = '../data/CognoSpeak_FINAL_METADATA_2_SHARE.csv'


# ASR_trans_out = '../data/FINAL_ASR/'
# ASR_trans_out_whp_med_16kHz = '../data/FINAL_ASR_Whisper_med_16kHz/'
ASR_trans_out_nemo_16kHz = '../data/FINAL_ASR_Nemo_16kHz/'
ASR_trans_out_wav2vec2_16kHz = '../data/FINAL_ASR_W2V2_16kHz/'

ASR_trans_out_whp_med_44kHz = '../data/FINAL_ASR_Whisper_med_44kHz/'
# ASR_trans_out_nemo_44kHz = '../data/FINAL_ASR_Nemo_44kHz/'
# ASR_trans_out_wav2vec2_44kHz = '../data/FINAL_ASR_W2V2_44kHz/'

metadata_TEMP_asr_out = '../data/CognoSpeak_TEMP_asr_out.csv'

metadata_ASR_out = '../data/CognoSpeak_ASR_out.csv'



transcript_info_out = '../data/CognoSpeak_transcript_info.csv'
transcript_metadata_out =  '../data/CognoSpeak_metadata_transcribed.csv'
# transcript_ori_dir = '/Volumes/Shared/spandh_bessemer/SPandhAndHealthcare/CcCHAT/CcHAT_data_processing/transcripts_to_spreadsheet/txt/'
transcript_ori_dir = '/home/madhu/research_space/spandh_bessemer/SPandhAndHealthcare/CcCHAT/CcHAT_data_processing/transcripts_to_spreadsheet/txt/'
# transcript_all_copy_dir = '/Volumes/Shared/cchat/Shared/CognoSpeak_NEW/MANUAL_TRANSCRIPTS_ORIGINAL/' 
transcript_all_copy_dir = '/home/madhu/madhu_share/MANUAL_TRANSCRIPTS_ORIGINAL/'
transcript_per_Q_copy_dir = '/home/madhu/madhu_share/MANUAL_TRANSCRIPTS_PER_QUESTION/'
manual_transcript_out = '../data/FINAL_MANUAL_TRANSCRIPTS/'



MoCA_out_n_matched_ISRAAC = '../data/CognoSpeak_no_match_MoCA_scores_ISRAAC.csv'
MoCA_out_n_matched_spreadshet = '../data/CognoSpeak_no_match_MoCA_scores_spreadshet.csv'

RUDAS_out_n_matched_spreadshet = '../data/CognoSpeak_no_match_RUDAS_scores_spreadshet.csv'
MCE_out_n_matched_spreadshet = '../data/CognoSpeak_no_match_MCE_scores_spreadshet.csv'
ACE_out_n_matched_spreadshet = '../data/CognoSpeak_no_match_ACE_scores_spreadshet.csv'

# MoCA_out_all_moca = '../data/CognoSpeak_MoCA_all_scores.csv'
MoCA_out_all_metadta = '../data/CognoSpeak_MoCA_all_metadata.csv'
MoCA_out_moca_metadata = '../data/CognoSpeak_MoCA_metadata.csv'

# RUDAS_out_all_RUDAS = '../data/CognoSpeak_RUDAS_all_scores.csv'
RUDAS_out_all_metadta = '../data/CognoSpeak_RUDAS_all_metadata.csv'
RUDAS_out_RUDAS_metadata = '../data/CognoSpeak_RUDAS_metadata.csv'

# MCE_out_all_MCE = '../data/CognoSpeak_MCE_all_scores.csv'
MCE_out_all_metadta = '../data/CognoSpeak_MCE_all_metadata.csv'
MCE_out_MCE_metadata = '../data/CognoSpeak_MCE_metadata.csv'

ACE_out_all_ACE = '../data/CognoSpeak_COGN__all_scores.csv'
ACE_out_all_metadta = '../data/CognoSpeak_ACE_all_metadata.csv'
ACE_out_ACE_metadata = '../data/CognoSpeak_ACE_metadata.csv'

matadata_media_out = '../data/CognoSpeak_metadata_media.csv'



Audio_INFO_CSV_out = '../data/CognoSpeak__Audio_INFO.csv'
Audio_info_metadata_out = '../data/CognoSpeak_8__metadata.csv'

VAD_sr = 16000



# share_audio_dir = '/Volumes/Shared/cchat/Shared/CognoSpeak_NEW/FINAL_AUDIO/'
share_audio_dir = '/home/madhu/madhu_share/FINAL_AUDIO/'


# share_video_dir = '/Volumes/Shared/cchat/Shared/CognoSpeak_NEW/MADHU_CHAONA_VIDEO/'
# share_video_dir = '/home/madhu/madhu_share/MADHU_CHAONA_VIDEO/'
share_video_dir = '/home/madhu/madhu_share/MADHU_CHAONA_VIDEO_ICASSP_2026/'



# congitron_intial_out
congitron_metadata_out = '../data/Cognitron/cognitron_metadata.csv'
# congitron_cogno_out





SR = 44100
wht_ns_mult = 0.1
wht_ns_path = '../data/white_noise.wav'
silence_path = '../data/silence.wav'



# ## These are for my MacBook
# cchat_DIR = '/Volumes/Shared/spandh_bessemer/SPandhAndHealthcare/CcCHAT/CcHAT_data_processing/'

cchat_DIR = '/home/madhu/research_space/spandh_bessemer/SPandhAndHealthcare/CcCHAT/CcHAT_data_processing/'

cogno_challenge_dir = cchat_DIR + 'CognoSpeak_Challenge/'
cogno_challenge_dir_temp = cchat_DIR + 'TEMP_CognoSpeak/'










'''
As the same IDs were assigned to different participants, I need to update the spreadsheet as well after updating the file names 
'''

xls_file = '../data/CcHAT_data_overview.xlsx'

df_xls_summary = check_process_csv(xls_file, 'Summary')
df_xls_demographics = check_process_csv(xls_file, 'demographics')
df_xls_assess = check_process_csv(xls_file, 'CcHAT_assessment_data')

df_MoCA = check_process_csv(xls_file, 'MoCa')
df_RUDAS = check_process_csv(xls_file, 'RUDAS')
df_MCE = check_process_csv(xls_file, 'MCE')
df_ACE_III = check_process_csv(xls_file, 'ACE-III')


df_PHQ = check_process_csv(xls_file, 'PHQ-9')
df_GAD = check_process_csv(xls_file, 'GAD-7')


df_JSON = check_process_json( '../data/cognospeak-production-default-rtdb-export.json' )






'''
The follolwing IDs had issues which Dora mentioned to me ... 
These IDs got their dates fixed so only the mentioned dates will be considered. 
https://docs.google.com/spreadsheets/d/1l3UEzdbZ7xNUEoeyKKh8vm4d621ec-VHwrGIDjykXDA/edit?usp=sharing
https://docs.google.com/spreadsheets/d/1l3UEzdbZ7xNUEoeyKKh8vm4d621ec-VHwrGIDjykXDA/edit?pli=1&gid=0#gid=0
'''

# ## This one needs their diagnosis to be changed ... , which is implemented towards the end of CognoSpeak_3_... script
# SPECIAL_IDs_DIAGNOSIS = [
#     ['06126_1', 'MCI']
#     ]

## This one needs their diagnosis to be changed ... , which is implemented towards the end of CognoSpeak_3_... script
SPECIAL_IDs_DIAGNOSIS = [
    ['88597d20-e3d4-44b8-8189-68151ece6dca', 'MCI'],
    ['ed74cda8-06b4-43b3-bbd8-8a51112947c7', 'Stroke'],
    ['d510f591-b094-4ab1-8df7-ed84a753be0e', 'MCI'],
    ['a8bf5457-33f9-4f69-9cb8-8e1619df3f6b', 'Dementia'],
    ['eafc4a14-a66b-4703-9f4a-ca30ca9dd961', 'MCI'],
    ['f7381258-5c71-4b88-870b-405cd58cab32', 'MCI']
    ]

SPECIAL_IDs_DIAG_TYPE = [
    ['ed74cda8-06b4-43b3-bbd8-8a51112947c7', 'Ischemic stroke'],
    ['a8bf5457-33f9-4f69-9cb8-8e1619df3f6b', 'Fronto temporal dementia']
    ]

SPECIAL_IDs_DOB = [
    ['38905a41-7ccb-4b44-810f-8117407ab73e', '09-1946']
    ]





# ## I was thinking about making these manually but I am reading them from the speardsheet I got directly from Caitlin 
# # https://docs.google.com/spreadsheets/d/1NaYKrUmppTRx9DEOWR-25k-5DubyjnrTmqi6cUM-UHU/edit#gid=0

# fixed_demographics_IDs = [
#     ['01474', 'diagnosis: FMD'],
#     ['07115', 'diagnosis: UC_FMD'],
#     ['15637', 'diagnosis: UC_FMD']
#     ]



'''
These are the sources which I can and can not trust 
'''

## Referral sources to be trusted 
# trust_refs = ['Great Minds', 'Join Dementia Research ', 'Join Dementia Research', 'Primary Care', 'Secondary Care']
# trust_N_refs = ['Self-referral', 'Social Media ', 'Unknown', 'Word of mouth']

trust_refs = ['Primary Care', 'Secondary Care']
trust_N_refs = ['Self-referral', 'Social Media', 'Unknown', 'Word of mouth', 'Great Minds', 'Join Dementia Research ', 'Join Dementia Research']

ethMINOR_refs = ['ISRAAC', 'Meri Yaadein', 'Shipshape', 'Sheffield Chinese Community Centre']



'''
These are the diagnosis category 
'''
DEM_CAT = ['Dementia', 'Mild_Vas_Dementia', 'Dementia (FTD)', 'Park_Dementia']

UNKN_CAT = ['FMD', 'FCD', 'Unknown', 'TBC', 'NC_FMD']



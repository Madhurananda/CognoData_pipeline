#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu May 23 10:43:46 2024

@author: madhupahar
"""


import os, sys, time
from datetime import datetime

from config import *

from tqdm import tqdm

import platform
if platform.system() == 'Darwin':
    from multiprocess.pool import ThreadPool, Pool
else:
    from multiprocessing.pool import ThreadPool, Pool
    
from multiprocessing import cpu_count

from natsort import natsorted


'''
This script will copy my final data to the CcHAT folder for everyone to use ... 
'''


# def do_copy_dir(args):
#     if_faluty = 0
#     a_dir, final_transcript_share = args[0], args[1]
#     copy_cmd = 'cp -r {} {}'.format(a_dir, final_transcript_share)
    
#     # print('copy_cmd : ', copy_cmd)
#     # sys.stdout.flush()
    
#     if_faluty = do_exec_copy_cmd(copy_cmd)
    
#     return if_faluty, a_dir
    
def do_copy_sorc_dest(source, dest, ext):
    
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
    
    


if __name__=='__main__' and '__file__' in globals():
    
    
    if len(sys.argv) < 2:
        print('\n\n Please use : python CognoSpeak_copy_data.py 15 [where 15 is the number of CPU]\n\n')
        sys.exit()
    
    # startTime = datetime.now()
    # current_time = startTime.strftime("%Y/%m/%d at %H:%M:%S")
    # print('\n\nThe script starting at: ' + str(current_time), ' \n\n' )
    
    N_jobs = int(sys.argv[1])
    
    if N_jobs >= cpu_count():
        print('The max no of CPU available : ', cpu_count())
        sys.exit("Lower the number of CPU\n\n")
    
    
    # I need to overwrite once and then back to normal ... 
    
    ## To overwrite the exisiting files ... 
    OVRWT = 0 # no overwrite
    # OVRWT = 1 # overwrite
    
    
    '''
    Step 1: Copy the .wav files for each assessememnts as it appears on the metadata 
    '''
    ## I need to copy ONLY the dir which are on the final metadata sheet 
    
    # df_metadata = get_metadata()
    
    # df_metadata = pd.read_csv( ACE_out_all_ACE )
    
    df_metadata = pd.read_csv( Audio_info_metadata_out )
    
    
    
    
    # xlx_file = '../data/TEST/IDs for Sarah.xlsx'
    # df_xls = pd.read_excel(xlx_file, sheet_name='Tabelle1')
    # df_xls = df_xls.rename(columns={'ID': 'research_ID'})
    # df_metadata = df_metadata.merge(df_xls, on='research_ID', how='right')
    # df_metadata = df_metadata[df_metadata['pseudo_unq_id'].notna()]
    
    
    # print('There are ', len(glob.glob(final_transcript_dir+'/*')), ' folders inside ', final_transcript_dir)
    print('There are ', len(df_metadata), ' folders inside FINAL metadata spreadsheet.')
    
    sys.stdout.flush()
    
    source = final_extract_dir
    dest = share_audio_dir
    # dest = '/home/madhu/research_space/spandh_bessemer/SPandhAndHealthcare/CcCHAT/CcHAT_data_processing/FINAL_transcript_FINAL_SHARE'
    
    
    print('The source dir is: ', source)
    print('The destination dir is: ', dest)
    
    
    
    dirs_to_copy = [ source+i for i in natsorted(df_metadata['dir_name'])  ]
    
    do_copy_sorc_dest(dirs_to_copy, dest, '.wav')
    
    
    '''
    Step 2: Copy the .txt files for each assessememnts as it appears on the metadata 
    At the moment only Whisper transcripts are copied ... 
    '''
    
    # I might need to consider W2V2 or Nemo ASR as well ... 
    
    
    # source = ASR_trans_out
    source = ASR_trans_out_whp_med_44kHz
    
    
    
    print('The source dir is: ', source)
    print('The destination dir is: ', dest)
    
    dirs_to_copy = [ source+i for i in natsorted(df_metadata['dir_name'])  ]
    
    do_copy_sorc_dest(dirs_to_copy, dest, '.txt')
    
    
    '''
    Step 3: Finally copy the metadata with the datetime stamp on it for everyone to share 
    '''
    meta_out_name = share_audio_dir+'CognoSpeak_metadata__' + datetime.today().strftime('%Y_%m_%d')+'.csv'
    
    
    # df_metadata_share = df_metadata[['research_ID', 'pseudo_unq_id',
    #        'assessment_ID', 'dir_name', 'assess_date', 'age',
    #        'diagnosis', 'referral', 'ethnicity', 'gender', 'ENGLISH_FIRST_LANG',
    #        'ENGLISH_ABILITY', 'FIRST_LANG', 'EDUCATION_INFO', 'REGION',
    #        'OTHER_CONDITIONS', 'Q1', 'Q2', 'Q3', 'Q4', 'Q5', 'Q6', 'Q7', 'Q8',
    #        'Q9', 'Q10', 'Q11', 'Q12', 'Q13', 'Q14', 'PHQ-9', 'GAD-7', 'EQ-5D',
    #        'REPEAT', 'ASSESS_GAPS_days', 'CONSENT']]
    
    
    df_metadata_share = df_metadata.drop(['OLD_r_ID', 'OLD_pseudo_unq_id', 'FirstName', 'LastName', 'BirthDay', 'NHS_No', 'Prac_email', 'telephone'], axis=1)
    
    
    df_metadata_share.to_csv(meta_out_name, index = False)
    
    
    
    '''
    Checking some information about the data ... 
    '''
    
    df_metadata.diagnosis.value_counts()
    
    df_metadata.referral.value_counts()
    
    
    df_metadata[df_metadata.diagnosis=='NC_FMD']
    
    
    
    
    executionTime = (datetime.now() - startTime)
    current_time = datetime.now().strftime("%Y/%m/%d at %H:%M:%S")
    print('\n\nThe script completed at: ' + str(current_time))
    print('Execution time: ' + str(executionTime), ' \n\n')



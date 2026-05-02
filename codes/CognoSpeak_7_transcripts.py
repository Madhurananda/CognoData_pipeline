#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jun  4 14:59:52 2024

@author: madhupahar
"""


# import os, sys, time, glob

# import pandas as pd

# import json
# import numpy as np
# # import whisper

# from tqdm import tqdm
# from natsort import natsorted
# from datetime import datetime, timedelta


# from main import *

from config import *





def get_audios(files_4_trans, to_find_ext):
    
    for i in tqdm(df_FINAL_transcribed['dir_name']):
    # for i in tqdm(df_to_share['dir_name']):
    # for i in tqdm(final_df_metadata_consent_transcribed['dir_name']):
        files_4_trans.extend( glob.glob(final_extract_dir+i+'/*'+to_find_ext) )
        if len(glob.glob(final_extract_dir+i+'/*'+to_find_ext)) == 0:
            print('No files: ', i)
        elif len(glob.glob(final_extract_dir+i+'/*'+to_find_ext)) > 1:
            print('multiple files : ', i)
    return files_4_trans

# cp_rm = 0 for only copy
# cp_rm = 1 for copy and rename 
# if_m_dest = 0 No folder will be created before copying
# if_m_dest = 1 A folder will be created before copying
def do_COPY_trans(files_4_trans, dest, cp_rm, if_m_dest):
    print('There are ', len(files_4_trans), ' files to be copied.')
    sys.stdout.flush()
    
    
    #############################################
    ## This is using multiple CPU ... 
    
    files_NOT_copied = []
    
    
    
    n_jobs = min(N_jobs, len(files_4_trans))
    print('n_jobs: ', n_jobs)
    sys.stdout.flush()
    
    
    if cp_rm == 0:
        inputs = zip(natsorted(files_4_trans), [dest]*len(files_4_trans), [if_m_dest]*len(files_4_trans), [cp_rm]*len(files_4_trans))
        results = tqdm(Pool(n_jobs).imap_unordered(do_copy, inputs), total=len(files_4_trans))
    elif cp_rm == 1:
        inputs = zip(natsorted(files_4_trans), [dest]*len(files_4_trans), [if_m_dest]*len(files_4_trans))
        results = tqdm(Pool(n_jobs).imap_unordered(do_copy_rename, inputs), total=len(files_4_trans))
        
    for result in results:
        if result[0] == 1:
            # c_incomplete_pats += 1
            files_NOT_copied.append(result[1])
        
        
    #############################################
    if len(files_NOT_copied) > 0: 
        print('\n\nFile was not copied: ', files_NOT_copied)
        print('Number of files NOT copied: ', len(files_NOT_copied))
        sys.stdout.flush()


def process_text(a_text):
    # a_text = a_text.replace('\n', '')
    
    for a_str in find_str_between(a_text, '(', ')'):
        a_text = a_text.replace( '('+a_str+')', '' )
    
    a_text = a_text.replace('.', ' ')
    a_text = a_text.replace(',', ' ')
    a_text = a_text.replace(';', ' ')
    
    a_text = a_text.replace('  ', ' ')
    a_text = a_text.replace('Pat:', '')
    a_text = a_text.strip()
    
    a_text = a_text.lower()
    a_text = a_text.replace('\n', ' ')
    
    return a_text


def read_write_response(cogno_challenge_dir, a_ch_dir, ID_file, transcrpt_content, s_Q, e_Q, name_Q):
    trans__ori = find_str_between(transcrpt_content, s_Q, e_Q)[0]
    trans_ = process_text(trans__ori)
    to_write_content= '-- ORIGINAL --\n' + trans__ori + '\n\n' + '-- SORTED --' + '\n' + trans_ + '\n'
    write_file_name = cogno_challenge_dir+a_ch_dir + '/' + ID_file + '__' +name_Q+ '.txt'
    if not os.path.exists(write_file_name):
        write_file(write_file_name, to_write_content)
    # else:
    #     print('The file already exists : ', write_file_name)



    



if __name__=='__main__' and '__file__' in globals():
    
    
    
    if len(sys.argv) < 2:
        print('\n\n Please use : python CognoSpeak_transcripts.py 15 [where 15 is the number of CPU]\n\n')
        sys.exit()
    
    N_jobs = int(sys.argv[1])
    
    if N_jobs >= cpu_count():
        print('The max no of CPU available : ', cpu_count())
        sys.exit("Lower the number of CPU\n\n")
    
    
    
    
    
    
    
    
    
    # df_METADATA = pd.read_csv( final_metadata_path )
    
    # df_metadata = df_METADATA.loc[ (df_METADATA["assessment_ID"] != 'N_all_ANSs') & (df_METADATA["assessment_ID"] != 'SPRDSHT__NOT_TRANS') & (df_METADATA["assessment_ID"] != 'TRANS__NOT_SPRDSHT') & (df_METADATA["assessment_ID"] != 'TEST_IDs') ]
    
    
    # df_metadata.reset_index(drop=True, inplace=True)
    
    
    # df_metadata = get_metadata()
    
    
    df_metadata = pd.read_csv( metadata_ASR_out )
    
    
    
    '''
    Here, I need to cross-check the transcript with directories 
    
    There are some trasncripts which do not match with my metadata dir_name 
    
    I need to fix this as soon as possible .... 
    
    The following is required as I made a mistake of sharing FINAL_transcribed_audio which were not cross-checked with my metadata. So, Fuxiang has picked up the wrong dir name, evemn though the audio inside is the same (or is it)? 
    
    '''
    
    
    
    
        
    ## Step 1: Find all the transcripts 
    
    
    check_dir_exists(transcript_ori_dir)
    
    transcript_files = find_files_in_a_dir(transcript_ori_dir, '.txt')
    
    print('There are ', len(transcript_files), ' transcript files.')
    
    
    # ###### This is a  check to be done when I need to find a transcrpit ....
    
    # to_f_trans = 'R_22893_240111_120330'
    
    # for a in transcript_files:
        
    #     if to_f_trans in a:
            
    #         print(a)
    
    
    
    
    
    ###############################
    ## Just checking if a transcript exists here or not ... 
    ## Comment it out after the check is over ... 
    
    # ori_trans_files = [x.split('/')[-1] for x in transcript_files]
    
    # copied_trans_files = [x.split('/')[-1] for x in find_files_in_a_dir(transcript_all_copy_dir, '.txt')]
    
    
    # diff_list(ori_trans_files, copied_trans_files)
    
    # diff_list( copied_trans_files, ori_trans_files )
    
    
    
    
    
    # ori_trans_files_IDs = [x.split('_')[1] for x in ori_trans_files]
    # copied_trans_files_IDs = [x.split('_')[1] for x in copied_trans_files]
    
    
    # diff_list(ori_trans_files_IDs, copied_trans_files_IDs)
    
    # diff_list(copied_trans_files_IDs, ori_trans_files_IDs)
    
    
    
    # serch_C = '28063'
    
    # for t_F in transcript_files:
    #     if serch_C in t_F:
    #         print(t_F)
    
    
    
    # df_meta_OLD = pd.read_csv('/Volumes/Shared/cchat/Shared/CognoSpeak_NEW/FINAL_AUDIO/CognoSpeak_metadata__2024_12_26.csv')
    
    # df_meta_NEW = pd.read_csv('/Volumes/Shared/cchat/Shared/CognoSpeak_NEW/FINAL_AUDIO/CognoSpeak_metadata__2025_05_12.csv')
    
    
    # df_meta_OLD = df_meta_OLD[df_meta_OLD.trans_txt != NO_EXIST_STR]
    
    # df_meta_NEW = df_meta_NEW[df_meta_NEW.trans_txt != NO_EXIST_STR]
    
    
    # diff_list(list(df_meta_OLD.trans_txt), list(df_meta_NEW.trans_txt))
    
    # diff_list(list(df_meta_NEW.trans_txt), list(df_meta_OLD.trans_txt))
    
    
    ###############################
    
    
    
    
    
    ## Step 2: copy them to the transcript final directory, which will be the one for everyone to share 
    # trans_final_dir = '/home/madhu/research_space/spandh_bessemer/SPandhAndHealthcare/CcCHAT/CcHAT_data_processing/CognoSpeak_FINAL_Transcripts/'
    # dest = trans_final_dir
    
    dest = transcript_all_copy_dir
    
    check_dir_exists(dest)
    
    
    ## Step 3 : Replace '__' by '_' if there are any 
    transcript_files_pruned = []
    for i in transcript_files:
        i_new = i.replace(i.split('/')[-1], i.split('/')[-1].replace('__', '_'))
        
        if os.path.exists( i_new ):
            transcript_files_pruned.append( i_new )
            
        else:
            mv_cmd = 'mv {} {}'.format(i, i_new)
            
            if os.system(mv_cmd) != 0:
                print('This command did not execute successfully: ', mv_cmd)
                sys.stdout.flush()
            else:
                transcript_files_pruned.append( i_new )
            
        
    
    ## Step 3A: copy them to the transcript final directory, which will be the one for everyone to share 
    
    do_COPY_trans(transcript_files_pruned, dest, 0, 0)
    
    
    # sys.stdout.flush()
    # time.sleep(100000000)
    
    
    
    
    ## Step 4: cross-check the transcript with the dir names as initially I shared all the dirs and worng dir was picked up while selecting for manual transcription 
    
    trans_IDs = [a.split('/')[-1].split('_')[1] for a in transcript_files]
    
    ## Find IDs for which trabnscripts are done as follow-ups
    print('The following IDs have follow-up transcripts : ')
    print(find_values_counts(trans_IDs, 1))
    
    
    
    # sys.stdout.flush()
    # time.sleep(100000000)
    
    dir_4RM_transcripts = [a.split('/')[-1].replace('__', '_').replace('.txt', '') for a in transcript_files]
    
    
    check_list_len(transcript_files, dir_4RM_transcripts)
    
    df_trans_details = pd.DataFrame( {'trans_txt': dir_4RM_transcripts, 'ori_path': transcript_files} )
    
    
    # print('dir_4RM_transcripts : ', dir_4RM_transcripts)
    print('Length of dir_4RM_transcripts : ', len(dir_4RM_transcripts))
    print('Length of unique dir_4RM_transcripts : ', len(set(dir_4RM_transcripts)))
    
    
    
    
    dir_transcribed = []
    dir_metadata = []
    not_found_dir = []
    n_Nmatched_dir = 0
    
    
    for i in dir_4RM_transcripts:
        
        found = 0
        
        dir_f_list = []
        
        for ind in df_metadata.index:
        # for ind in df_metadata_consent.index:
            
            if i == df_metadata['dir_name'][ind]:
                # print(i)
                dir_f_list.append( df_metadata['dir_name'][ind] )
        
        if len(dir_f_list) == 0:
            for ind in df_metadata.index:
                if i.replace( i.split('_')[-1], '' )[:-1] in df_metadata['dir_name'][ind]:
                    dir_f_list.append( df_metadata['dir_name'][ind] )
        
        if len(dir_f_list) == 0:
            for ind in df_metadata.index:
                if i.replace( i.split('_')[-1], '' )[:-3] in df_metadata['dir_name'][ind]:
                    dir_f_list.append( df_metadata['dir_name'][ind] )
                    
                    
                    
        if len(dir_f_list)==0:
            not_found_dir.append( i )
        elif len(dir_f_list)>1:
            print('Investigate this ID as it still contains mult occ: ', i)
            print('dir_f_list : ', dir_f_list)
        else:
            dir_transcribed.append( i )
            dir_metadata.append( dir_f_list[0] )
    
    
    
    
    
    print('The file for which we have transcripts but are NOT found inside ', final_metadata_path, ' are: ')
    print( not_found_dir )
    
    check_list_len(dir_transcribed, dir_metadata)
    
    list_comnts = ['DIR_EXISTS']*len(dir_metadata)
    
    ## Here, I am adding the transcripts for which I can't find any dirs 
    dir_metadata.extend([NO_EXIST_STR]*len(not_found_dir))
    dir_transcribed.extend( not_found_dir )
    
    list_comnts.extend(['NO_DIR']*len(not_found_dir))
    
    
    check_list_len(dir_transcribed, dir_metadata)
    check_list_len(dir_transcribed, list_comnts)
    
    
    if len(find_values_counts(dir_transcribed, 1)) > 0:
        print('These are the dupliacted values : ', find_values_counts(dir_transcribed, 1))
        print('This means there are two same dirs for which we have different trasncripts.')
    
    if len(find_values_counts(dir_metadata, 1)) > 0:
        print('These are the dupliacted values : ', find_values_counts(dir_metadata, 1))
        print('This means there are two same dirs for which we have different trasncripts.')
    
    
    
    
    ## Step 5: Create the dataframe containing all the trasncription information 
    
    df_trans_meta_temp = pd.DataFrame( {'dir_name': dir_metadata, 'trans_txt': dir_transcribed, 'comments':list_comnts} )
    
    df_trans_meta = pd.merge( df_trans_meta_temp, df_trans_details, on='trans_txt', how='inner')
    
    
    
    ## Step 6: There are some issues needing sorted manually 
    
    
    ## The following will give us an idea of the trans which should not be included to the final metadata 
    df_dupl = df_trans_meta[df_trans_meta['comments']=='DIR_EXISTS']
    # dir_name = df_dupl['dir_name']
    # df_dupl = df_dupl[dir_name.isin(dir_name[dir_name.duplicated()])].sort_values("dir_name")
    df_dupl, _ = get_dupl_df(df_dupl, "dir_name")
    print('Duplicated values before sorting: ')
    print(df_dupl.drop(['comments', 'ori_path'], axis=1))
    
    '''
    98   R_01474_230211_151730   R_01474_230211_153654      DIR_EXISTS    
    needs to be changed to NO_DIR 
    '''
    # ## Didn't work ... 
    # df_trans_meta[df_trans_meta['trans_txt']=='R_01474_230211_153654']['comments'] = 'NO'
    
    df_trans_meta.loc[df_trans_meta.index[df_trans_meta['trans_txt'] == 'R_01474_230211_153654'].values[0], 'comments'] = 'NO_DIR'
    
    
    ## CHECK AGAIN .... 
    ## The following will give us an idea of the trans which should not be included to the final metadata 
    df_dupl = df_trans_meta[df_trans_meta['comments']=='YES']
    # dir_name = df_dupl['dir_name']
    # df_dupl = df_dupl[dir_name.isin(dir_name[dir_name.duplicated()])].sort_values("dir_name")
    df_dupl, _ = get_dupl_df(df_dupl, "dir_name")
    print('\n\n***** Duplicated values after sorting: THIS SHOULD BE EMPTY ...')
    print(df_dupl.drop(['comments', 'ori_path'], axis=1))
    print('\n\n\n\n\n\n')
    sys.stdout.flush()
    time.sleep(5)
    
    
    
    ## Step 7: Some old transcripts have wrong names, just check them in case .... 
    
    ## I have found some dir names have 7 chars in one section, investigate ... 
    print('START .... ')
    print('The following txt file names do not seem OK, change the file names, IGNORE: if the comments are NO_DIR ')
    for a in transcript_files:
        # i = i.replace('__', '_')
        
        i = a.split('/')[-1].replace('__', '_').replace('.txt', '')
        
        if len(i.split('_')[2]) != 6:
            print(a)
            print(df_trans_meta[df_trans_meta['trans_txt']==i]['comments'])
            print()
        elif len(i.split('_')[3]) != 6:
            print(a)
            print(df_trans_meta[df_trans_meta['trans_txt']==i]['comments'])
            print()
    print('.... END')
    
     
    
    ## Step 8: Save the trabnscription info CSV file 
    
    # Check if there are any missing transcripts in the new version (manully aemended or deleted by Fuxiang)
    
    df_before = pd.read_csv( transcript_info_out )
    
    
    print('\n\n** I am checking the mis-matches between this CSV file and the previous exisiting one ... ')
    
    ## These ones I can find the audio files in AFTER csv, which was not in BEFORE for those DIR exists ... 
    miss_trans = diff_list( df_trans_meta[df_trans_meta.comments=='DIR_EXISTS'].trans_txt, df_before[df_before.comments=='DIR_EXISTS'].trans_txt )
    
    print('The number of newly addedd transcripts for which DIR exists are: ')
    print(len(miss_trans))
    print('')
    
    
    ## These ones I can find the audio files in AFTER csv, which was not in BEFORE for those NO DIR can be found ... 
    miss_trans = diff_list( df_trans_meta[df_trans_meta.comments=='NO_DIR'].trans_txt, df_before[df_before.comments=='NO_DIR'].trans_txt )
    
    ## These are the trans which I have already checked as missing ... 
    already_miss_trans = ['R_99214_230908_072300', 'R_99214_230829_103719', 'R_58469_230612_094610', 'R_22909_230316_142831', 'S_62755_231116_111945', 'R_56264_250506_13205']
    
    # print('miss_trans: ')
    # print(miss_trans)
    
    # print('already_miss_trans: ')
    # print(already_miss_trans)
    
    
    miss_trans = diff_list( miss_trans, already_miss_trans )
    
    
    # print('miss_trans: ')
    # print(miss_trans)
    
    # sys.stdout.flush()
    # time.sleep(100000000)
    
    
    # print('Newly addedd transcripts for which NO DIR can be found are: ')
    # print(miss_trans)
    # print('')
    if len(miss_trans) > 0:
        print('*** => =? =>Newly addedd transcripts for which NO DIR can be found are the following ...  Please fix this before continuing ... ')
        print(miss_trans)
        print('')
        sys.stdout.flush()
        time.sleep(100000000)
    
    
    ## These ones I can find the audio files in BEFORE csv, but are missing in the latest CSV for those NO DIR can be found ... 
    miss_trans = diff_list( df_before[df_before.comments=='NO_DIR'].trans_txt, df_trans_meta[df_trans_meta.comments=='NO_DIR'].trans_txt )
    
    print('These transcripts for which I can NOT find the audio files in BEFORE csv, but now I found them in the latest CSV ')
    print(miss_trans)
    print('')
    
    
    
    ## These ones I can find the audio files in BEFORE csv, but are missing in the latest CSV for those DIR exists ... 
    miss_trans = diff_list( df_before[df_before.comments=='DIR_EXISTS'].trans_txt, df_trans_meta[df_trans_meta.comments=='DIR_EXISTS'].trans_txt )
    
    miss_trans = diff_list( miss_trans, already_miss_trans )
    
    
    
    if len(miss_trans) > 0:
        print('*** => =? =>These transcripts I can find the audio files in BEFORE csv, but are missing in the latest CSV for those DIR exists. Please fix this before continuing ... ')
        print(miss_trans)
        print('')
        sys.stdout.flush()
        time.sleep(100000000)
       
    
    df_trans_meta.to_csv(transcript_info_out, index=False)
    
    
    
    
    ## Step 9 : merge the transcription info CSV with the metadata for those who have transcripts and coresponding dir 
    
    df_trans_meta_final = df_trans_meta[df_trans_meta['comments']=='DIR_EXISTS']
    
    df_trans_meta_final = df_trans_meta_final.drop('comments', axis=1)
    df_trans_meta_final = df_trans_meta_final.drop('ori_path', axis=1)
    
    df_trans_meta_final['trans_txt'] = df_trans_meta_final['trans_txt']+'.txt'
    
    
    
    
    
    df_metadata_transcribed = pd.merge( df_metadata, df_trans_meta_final, on='dir_name', how='left')
    
    df_metadata_transcribed['trans_txt'] = df_metadata_transcribed['trans_txt'].fillna(NO_EXIST_STR)
    
    df_metadata_transcribed = df_metadata_transcribed.reset_index(drop=True)
    
    ## 'R_57571_240523_123636' has Q3 very long and thus the transcript is not complete ... REMOVE IT ... 
    df_metadata_transcribed.loc[df_metadata_transcribed[df_metadata_transcribed.dir_name == 'R_57571_240523_123636'].index.item(), 'trans_txt'] = NO_EXIST_STR
    
    
    
    '''
    Step 10: Here, I need to make the dir_name and trans_txt as same, otherwise I will face many problems 
    '''
    
    for ind in df_metadata_transcribed.index:
        # print(df_man_trans['dir_name'][ind])
        
        if df_metadata_transcribed['trans_txt'][ind] != NO_EXIST_STR:
            
            a_dir = df_metadata_transcribed['dir_name'][ind]
            
            a_trans = df_metadata_transcribed['trans_txt'][ind].replace('.txt', '')
            
            
            if a_dir != a_trans and not os.path.exists( transcript_all_copy_dir+df_metadata_transcribed['dir_name'][ind]+'.txt' ):
                print('dir and trans mismatch . ')
                
                # transcript_all_copy_dir
                
                mv_cmd = 'mv {} {}'.format(transcript_all_copy_dir+df_metadata_transcribed['trans_txt'][ind], transcript_all_copy_dir+df_metadata_transcribed['dir_name'][ind]+'.txt')
                
                print('mv_cmd : ')
                print(mv_cmd)
                
                do_copy_simple(mv_cmd)
                df_metadata_transcribed.loc[ind, 'trans_txt'] = a_dir+'.txt'
            
    print('Making the dir_name and trans_txt equal is complete.')
    sys.stdout.flush()
    
    ## Save the final metadata ... 
    df_metadata_transcribed.to_csv(transcript_metadata_out, index=False)
    
    
    
    
    '''
    Step 11: I need to extract answers for each question. If there is a missing question, I can find it out here ... 
    '''
    
    
    
    all_Q_types = ['Q'+str(i) for i in range(1, 15)] + ['(End)']
    
    
    
    for ind in tqdm(df_metadata_transcribed.index):
        
        if df_metadata_transcribed['trans_txt'][ind] != NO_EXIST_STR:
            
            a_dir = df_metadata_transcribed['dir_name'][ind]
            
            if len(glob.glob(transcript_all_copy_dir+a_dir+'.txt')) != 1:
                print('there is a problem. The same txt file exists more than once for : ', a_dir)
                # continue
                sys.stdout.flush()
                time.sleep(100000000)
            else:
                a_txt_file = glob.glob(transcript_all_copy_dir+a_dir+'.txt')[0]
            
            transcrpt_content = read_file( a_txt_file )
            
            for i in range(len(all_Q_types)-1):
                
                out_write_dir = manual_transcript_out+a_dir+'/'
                check_create_dir(out_write_dir)
                write_file_name = a_txt_file.replace(transcript_all_copy_dir, out_write_dir).replace( '.txt', '_'+all_Q_types[i]+'.txt' )
                
                if not os.path.exists( write_file_name ):
                    
                    try: 
                        trans__ori = find_str_between(transcrpt_content, '\n'+all_Q_types[i]+'\n', '\n'+all_Q_types[i+1]+'\n')[0]
                        
                        ## I am not processing any text at the moment 
                        # to_write_content = process_text(trans__ori)
                        to_write_content = trans__ori
                        
                        write_file(write_file_name, to_write_content)
                    except:
                        print('\n\n***** There is an issue in this transcript. Check (probably this question is missing ... ): ', all_Q_types[i])
                        print('a_dir : ', a_dir)
                        print('The original transcript path: ', df_trans_meta[df_trans_meta.dir_name == a_dir].ori_path.values[0])
                        sys.stdout.flush()
                        time.sleep(100000000)
                
    
    '''
    Step 12: Copy all the per question transcripts to the shared dir for everyone to use ... 
    '''
    
    rsync_cmd = 'rsync -rlptDvh -P --stats {} {}'.format( manual_transcript_out, transcript_per_Q_copy_dir )
    
    # print('rsync_cmd : ')
    # print(rsync_cmd)
    
    do_copy_simple(rsync_cmd)
    
    
    print('Copying all transcriptions per question is complete.')
    sys.stdout.flush()
    
    
    
    
    # '''
    # This is to answer Caitlin's question about the ISRAAC transcripts ... 
    # '''
    
    
    # df_metadata_transcribed_ISRAAC = df_metadata_transcribed[df_metadata_transcribed.referral=='ISRAAC']
    
    # # df_metadata_transcribed_ISRAAC.reset_index(drop=True, inplace=True)
    
    # df_metadata_transcribed_ISRAAC = drop_df_cols(df_metadata_transcribed_ISRAAC)
    
    # df_metadata_transcribed_ISRAAC.to_csv('../data/4_Caitlin/trans_ISRACC.csv', index=False)
    
    
    
    # df_metadata_transcribed_ISRAAC[df_metadata_transcribed_ISRAAC.trans_txt==NO_EXIST_STR].research_ID
    
    
    
    
    # I need to add a section here about splitting each questioin in a text file as processed text, something like '../data/CognoSpeak_results/data'
    
    
    # Then, I need to make sure the dir_name matches with the trans_txt 
    
    
    
    executionTime = (datetime.now() - startTime)
    current_time = datetime.now().strftime("%Y/%m/%d at %H:%M:%S")
    print('\n\nThe script completed at: ' + str(current_time))
    print('Execution time: ' + str(executionTime), ' \n\n')
    
    
    
    
    
    
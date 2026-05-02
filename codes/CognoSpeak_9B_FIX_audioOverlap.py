#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Apr 15 20:58:39 2024

@author: madhupahar
"""


'''
I created this script to check the word error rate (WER) for varoius texts ... 
#### So there are definately overlaps in the audio, but manual transcripts are okay. 
## So, I only need to fix the audio and then generate ASR text from it 
## https://github.com/hiisi13/audio-offset-finder/blob/main/audio_offset_finder.py
'''


import warnings
warnings.filterwarnings('ignore')


import os, sys, time

import math


from datetime import datetime, timedelta

from main import *
from config import *

from tqdm import tqdm

import platform
if platform.system() == 'Darwin':
    from multiprocess.pool import ThreadPool, Pool
else:
    from multiprocessing.pool import ThreadPool, Pool

import jiwer

from silero_vad import load_silero_vad, read_audio, get_speech_timestamps

import matplotlib.pyplot as plt

from scipy import signal

import librosa
import soundfile as sf

def process_text(a_text):
    
    a_text = a_text.replace('\n', ' ')
    a_text = a_text.strip()
    
    return a_text



def further_process_text(a_text):
    
    for a_str in find_str_between(a_text, '(', ')'):
        a_text = a_text.replace( '('+a_str+')', '' )
    
    a_text = a_text.replace('Pat:', '')
    
    return a_text



def get_grouped_df(df, id_col, val_col, mean_val_col):
    data = {id_col:df[[id_col, val_col]].groupby(id_col).mean().index.values, 
            mean_val_col:df[[id_col, val_col]].groupby(id_col).mean()[val_col].values}
    df_grouped = df.merge(pd.DataFrame(data), on=id_col, how='inner')
    
    return df_grouped



def check_questions_no(a_txt, text_vals, spliter):
    if text_vals.count(spliter) > 1:
        sys.exit('This question text exists more than one ', spliter, ' in the manual transcription: ', a_txt)




# def find_offset(within_file, find_file):
    
#     # print('within_file : ', within_file)
#     # print('find_file : ', find_file)
#     # print('window : ', window)
    
#     y_within, sr_within = librosa.load(within_file, sr=None)
#     y_find, _ = librosa.load(find_file, sr=sr_within)
    
#     ## Adding 10-sec silence to the 'within_file'
    
#     y_within = [0]*(10*sr_within) + list(y_within)
    
#     # c = signal.correlate(y_within, y_find[:sr_within*window], mode='valid', method='fft')
    
#     c = signal.correlate(y_within, y_find[:len(y_within)], mode='valid', method='fft')
    
#     # c = signal.correlate(y_within, y_find[:sr_within*window], mode='full', method='fft')
    
#     ## takes a long time 
#     # c = signal.correlate(y_within, y_find[:sr_within*window], mode='full', method='direct')
    
#     peak = np.argmax(c)
#     offset = round(peak / sr_within, 2)
    
#     # dx = 1
#     # # y = [1, 2, 3, 4, 4, 5, 6] # dx constant
#     # # np.diff(y, dx) # dy/dx 2nd order accurate
#     # # np.gradient(y, dx) # dy/dx 2nd order accurate
#     # delta = np.diff(c, dx) # dy/dx 2nd order accurate
#     # Delta_delta = np.gradient(c, dx) # dy/dx 2nd order accurate
    
#     # return c, delta, Delta_delta, offset
#     return c, offset



# def do_calc_audio_corr(args):
    
#     a_dir = args[0]
    
#     df_corr_temp = pd.DataFrame([], columns=['dir_name', 'find_Q', 'within_Q', 'max_C', 'offset'])
    
#     # L_Qs = ['Q'+str(x) for x in range(1, 21)]
    
#     # a_dir = 'R_53515_250214_151628'
#     # window = 60
    
#     for i in range(len(L_Qs)):
        
#         # find_file = final_extract_dir + a_dir + '/' + a_dir + '_' + L_Qs[i] + '.wav'
#         find_files = glob.glob(final_extract_dir + a_dir + '/*' + '_' + L_Qs[i] + '.wav')
        
#         for j in range(i+1, len(L_Qs)):
            
#             within_files = glob.glob(final_extract_dir + a_dir + '/*' + '_' + L_Qs[j] + '.wav')
            
#             if len(find_files) == 1 and len(within_files) == 1:
                
#                 find_file = find_files[0]
#                 within_file = within_files[0]
                
#                 # print('find_file : ', find_file)
#                 # print('within_file : ', within_file)
                
#                 # c, delta, Delta_delta, offset = find_offset(within_file, find_file, window)
#                 c, offset = find_offset(within_file, find_file)
                
#                 if max(c) > 1000:
                
#                     df_corr_temp.loc[len(df_corr_temp.index)] = [a_dir] + [find_file.split('/')[-1].split('_')[-1].split('.wav')[0]] + [within_file.split('/')[-1].split('_')[-1].split('.wav')[0]] + [max(c)] + [offset]
            
#             elif len(find_files) > 1 and len(within_files) > 1:
#                 print('It seems that there are two files for one question ... ')
#                 print('find_files: ', find_files)
#                 print('within_files : ', within_files)
#                 sys.stdout.flush()
#                 time.sleep(100000000)
                
                
#     # print('df_corr_temp : ')
#     # print(df_corr_temp)
    
#     # sys.stdout.flush()
#     # time.sleep(100000000)
    
    
#     return df_corr_temp


def copy_a_file(copy_cmd):
    if_faluty = do_exec_cmd(copy_cmd)
    
    if if_faluty == 1:
        print('This did not execute porperly: ', copy_cmd)



# def check_delete_audio(a_wav_file, target_dir):
#     dest_file = a_wav_file.replace(final_extract_dir, target_dir)
#     if os.path.exists( dest_file ):
#         rm_cmd = 'rm {}'.format( dest_file )
#         copy_a_file(rm_cmd, a_wav_file)



# def check_delete_ASR_txt(a_wav_file, target_dir):
#     dest_file = a_wav_file.replace(final_extract_dir, target_dir).replace('.wav', '.txt')
#     if os.path.exists( dest_file ):
#         rm_cmd = 'rm {}'.format( dest_file )
#         copy_a_file(rm_cmd, a_wav_file)
    
#     dest_file = a_wav_file.replace(final_extract_dir, target_dir).replace('.wav', '.dict')
#     if os.path.exists( dest_file ):
#         rm_cmd = 'rm {}'.format( dest_file )
#         copy_a_file(rm_cmd, a_wav_file)
        
#     dest_file = a_wav_file.replace(final_extract_dir, target_dir).replace('.wav', '__CHAR.csv')
#     if os.path.exists( dest_file ):
#         rm_cmd = 'rm {}'.format( dest_file )
#         copy_a_file(rm_cmd, a_wav_file)
    
#     dest_file = a_wav_file.replace(final_extract_dir, target_dir).replace('.wav', '__WORD.csv')
#     if os.path.exists( dest_file ):
#         rm_cmd = 'rm {}'.format( dest_file )
#         copy_a_file(rm_cmd, a_wav_file)
        
#     dest_file = a_wav_file.replace(final_extract_dir, target_dir).replace('.wav', '__SEG.csv')
#     if os.path.exists( dest_file ):
#         rm_cmd = 'rm {}'.format( dest_file )
#         copy_a_file(rm_cmd, a_wav_file)


def do_del_dir(base_dir, a_dir):
    
    
    if os.path.exists(base_dir+a_dir):
        rm_cmd = 'rm -rf {}'.format(base_dir+a_dir)
        # print('rm_cmd : ')
        # print(rm_cmd)
        # sys.stdout.flush()
        do_exec_cmd(rm_cmd)
    

def check_delete_dir(a_dir):
    
    do_del_dir(final_extract_dir, a_dir)
    
    do_del_dir(final_transcript_dir, a_dir)
    
    do_del_dir(final_ext_16kHz_dir, a_dir)
    
    do_del_dir(ASR_trans_out_nemo_16kHz, a_dir)
    
    do_del_dir(ASR_trans_out_wav2vec2_16kHz, a_dir)
    
    do_del_dir(ASR_trans_out_whp_med_44kHz, a_dir)
    
    do_del_dir(share_audio_dir, a_dir)
    
    
    

def do_copy2_ori(args):
    
    a_file = args[0]
    
    dest_file = a_file.replace(extracted_data_dir_backup_dir, extracted_data_dir)
    
    ## The destination file must exist ... 
    
    if not os.path.exists( dest_file ):
        
        print('The original file does not exit. Check: ', dest_file)
        sys.stdout.flush()
        # time.sleep(100000000)
    
    
    copy_cmd = 'cp {} {}'.format( a_file, dest_file )
    
    # print(copy_cmd)
    
    do_exec_cmd(copy_cmd)
    
    return 1




def do_del_temp_media(args):
    
    a_dir = args[0]
    
    rm_cmd = 'rm -rf {}'.format(extracted_data_dir_temp_dir+a_dir)
    
    do_exec_cmd(rm_cmd)
    
    return 1


def do_fix_overlap(args):
    
    ind = args[0]
    
    if_sucess = 0
    
    a_dir = df_overlap['dir_name'][ind]
    
    a_Q = df_overlap['find_Q'][ind]
    
    overlap_time = df_overlap['Overlap_len'][ind]
    
    media_Len = df_overlap['media_len'][ind]
    
    
    
    
    
    # files = [ x for x in  glob.glob( extracted_data_dir + a_dir + '/*' ) if not x.endswith('csv') and not x.endswith('json')]
    
    files = glob.glob( extracted_data_dir + a_dir + '/*' + a_Q+'.*' ) 
    if len(files) > 1:
        print('\n\nCHECK: The number of files inside: ', a_dir, ' is: ', len(files))
        sys.stdout.flush()
        time.sleep(100000000)
    
    a_file = files[0]
    
    
    
    ## Step 1: 
    ## copy the original ones from extracted_data_dir to extracted_data_dir_backup_dir
    
    dest_file = a_file.replace(extracted_data_dir, extracted_data_dir_backup_dir)
    
    # print('original file path .. ', a_file)
    # print('backup file path ',  dest_file)
    # sys.stdout.flush()
    # time.sleep(100000000)
    
    if not os.path.exists( dest_file ):
        
        ## Check if the dest dir exists ... 
        dest_dir = extracted_data_dir_backup_dir + a_dir
        
        if not os.path.isdir(dest_dir):
            os.mkdir(dest_dir)
        
        
        
        copy_cmd = 'cp {} {}'.format( a_file, a_file.replace(extracted_data_dir, extracted_data_dir_backup_dir) )
        
        do_exec_cmd(copy_cmd)
    
    
    
    
    
    ## Step 2: 
    ## Do all the necessary changes in extracted_data_dir_temp_dir
    
    
    exist_files = glob.glob( extracted_data_dir_temp_dir + a_dir + '/*' + a_Q+'.*' ) 
    if len(exist_files) > 1:
        print('\n\nCHECK: The number of files inside: ', a_dir, ' is: ', len(files))
        sys.stdout.flush()
        time.sleep(100000000)
    
    
    an_conv_v = exist_files[0]
    
    
    
    if not an_conv_v.endswith('.mp4'):
        print('\n\nThis media does not end with mp4: ', )
        sys.stdout.flush()
        time.sleep(100000000)
    
    
    ## Make the original file first 
    an_conv_v_ORI = an_conv_v.replace('.mp4', '__ORI.mp4')
    
    if os.path.exists(an_conv_v_ORI):
        rm_cmd = 'rm {}'.format(an_conv_v_ORI)
        do_exec_cmd(rm_cmd)
    
    cng_cmd = 'mv {} {}'.format(an_conv_v, an_conv_v_ORI)
    do_exec_cmd(cng_cmd)
    
    
    ## Then, create the new media using the user log time 
    an_conv_v_SORTED = an_conv_v.replace('.mp4', '__SORTED.mp4')
    
    if os.path.exists(an_conv_v_SORTED):
        rm_cmd = 'rm {}'.format(an_conv_v_SORTED)
        do_exec_cmd(rm_cmd)
    
    replace_cmd = 'ffmpeg -loglevel quiet -i {} -ss {} -t {} {}'.format(an_conv_v_ORI, overlap_time, media_Len, an_conv_v_SORTED)
    # print('replace_cmd : ')
    # print(replace_cmd)
    do_exec_cmd(replace_cmd)
    
    cng_cmd = 'mv {} {}'.format(an_conv_v_ORI, an_conv_v)
    do_exec_cmd(cng_cmd)
    
    
    ## Step 3:
    ## Update the original media in extracted_data_dir
    
    
    
    
    ## Rename the original files first ... 
    
    if not a_file.endswith('.webm'):
        print('\n\nThis media does not end with webm: ', )
        sys.stdout.flush()
        time.sleep(100000000)
    
    
    
    a_file_ORI = a_file.replace('.webm', '__ORI.webm')
    
    cng_cmd = 'mv {} {}'.format(a_file, a_file_ORI)
    do_exec_cmd(cng_cmd)
    
    # rm_cdm = 'rm {}'.format( a_file )
    # do_exec_cmd(rm_cdm)
    
    
    
    a_file_SORTED = a_file.replace('.webm', '__SORTED.webm')
    
    
    media_reverse_cmd = 'ffmpeg -loglevel quiet -i {} {}'.format( an_conv_v_SORTED, a_file_SORTED )
    
    # print('media_reverse_cmd: ')
    # print(media_reverse_cmd)
    
    ## Not sucessful 
    if do_exec_cmd(media_reverse_cmd) != 0:
        print('\n\nThis command did not work properly: ', media_reverse_cmd)
        print('Thus, the original file is being reverses back ... ')
        sys.stdout.flush()
        cng_cmd = 'mv {} {}'.format(a_file_ORI, a_file)
        do_exec_cmd(cng_cmd)
        
        rm_cmd = 'rm {}'.format(a_file_SORTED)
        do_exec_cmd(rm_cmd)
        
        
        
    ## Sucessfull ... 
    else:
        # rm_cmd = 'rm {}'.format(a_file)
        # do_exec_cmd(rm_cmd)
        
        rm_cmd = 'rm {}'.format(a_file_ORI)
        do_exec_cmd(rm_cmd)
        
        cng_cmd = 'mv {} {}'.format(a_file_SORTED, a_file)
        do_exec_cmd(cng_cmd)
        
        # print('Amending media has been sucessful')
        # sys.stdout.flush()
        
        if_sucess += 1
    
    
    
    ## Delete this dir from all other exisiting places
    check_delete_dir(a_dir)
    
    
    
    return if_sucess



if __name__=='__main__' and '__file__' in globals():
    
    
    # startTime = datetime.now()
    # current_time = startTime.strftime("%Y/%m/%d at %H:%M:%S")
    # print('\n\nThe script starting at: ' + str(current_time), ' \n\n' )
    
    
    N_jobs = int(sys.argv[1])
    
    
    
    ## First, read the audio_overlap csv ... 
    
    df_overlap = pd.read_csv( '../data/Audio_overlap_FOUND.csv' )
    
    
    # df_overlap = df_overlap.sort_values(by=["Overlap_len"], ascending=True)
    
    
    ## These are the some I need to exclude after manual checking ... 
    df_overlap = df_overlap[df_overlap.dir_name != 'R_74389_240814_121223']
    
    
    
    ## This is just checking ... 
    # df_overlap = df_overlap[(df_overlap.dir_name == 'MND_R_38885_240902_124951') & (df_overlap.find_Q == 'Q1')]
    
    
    
    df_overlap = df_overlap.sort_values(by=["dir_name", "find_Q"], ascending=True)
    
    
    
    # ## This is just testing: 
    # df_overlap = df_overlap[df_overlap.dir_name == 'R_88277_240815_150526']
    
    
    
    
    
    df_overlap = df_overlap.reset_index(drop=True)
    
    if len(list(df_overlap.media_type.value_counts())) > 1:
        
        print('It seems there are more tha just WEB_VIDEO.')
        print(df_overlap.media_type.value_counts())
        print('INVESTIGATE')
        sys.stdout.flush()
        time.sleep(100000000)
    
    
    
    
    ####################################################################
    
    '''
    This is about putting back the original files where they were ... 
    1. Copy the audio files from extracted_data_dir_backup_dir to extracted_data_dir
    2. Delete the dir in extracted_data_dir_temp_dir
    '''
    
    
    # ## Step 1 : 
    # ori_files = natsorted(find_files_in_a_dir(extracted_data_dir_backup_dir, '.webm'))
    
    
    # n_jobs = min(N_jobs, len(ori_files))
    # print('n_jobs: ', n_jobs)
    # sys.stdout.flush()
    
    # inputs = zip( ori_files )
    
    # print('Copying the original audio back. Starting ... ')   
    # sys.stdout.flush()
    
    # results = tqdm(Pool(n_jobs).imap_unordered(do_copy2_ori, inputs), total=len(ori_files))
    
    # n_res = 0
    # for result in results:
    #     n_res += result
    
    
    # time.sleep(1)
    # print('Copying the original audio back. DONE for ', n_res, ' files.')   
    # sys.stdout.flush()
    
    # sys.stdout.flush()
    # time.sleep(100000000)
    
    
    # ## Step 2 : 
    # inputs = zip( natsorted(set(df_overlap.dir_name)) )
    
    # n_jobs = min(N_jobs, len(natsorted(set(df_overlap.dir_name))))
    # print('n_jobs: ', n_jobs)
    # sys.stdout.flush()
    
    # print('Deleting the files in extracted_data_dir_temp_dir. Starting ... ')   
    # sys.stdout.flush()
    
    # results = tqdm(Pool(n_jobs).imap_unordered(do_del_temp_media, inputs), total=len(natsorted(set(df_overlap.dir_name))))
    
    # n_res = 0
    # for result in results:
    #     n_res += result
    
    # print('Deleting the files in extracted_data_dir_temp_dir. DONE for ', n_res, ' folders.')   
    # sys.stdout.flush()
    
    
    # sys.stdout.flush()
    # time.sleep(100000000)
    
    ####################################################################
    
    
    
    
    
    
    
    
    
    n_jobs = min(N_jobs, len(df_overlap))
    print('n_jobs: ', n_jobs)
    sys.stdout.flush()
    
    inputs = zip( list(df_overlap.index) )
    
    print('\n\n******** Fixing the media overlap. Starting ... for ', len(df_overlap), ' files ... ')   
    sys.stdout.flush()
    
    results = tqdm(Pool(n_jobs).imap_unordered(do_fix_overlap, inputs), total=len(list(df_overlap.index)))
    
    n_res = 0
    for result in results:
        n_res += result
    
    
    time.sleep(1)
    print('\n\n******** Fixing the media overlap. DONE for ', n_res, ' files out of: ', len(df_overlap), ' files ... ')   
    sys.stdout.flush()
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    # '''
    # I have given up on this and decided to fix the audio manually 
    # The audio overlap checking is working, but the mixup so bad, it is better to do it manually 
    # '''
    
    
    
    
    
    # ## Read the metadata ... 
    
    # # df_metadata = pd.read_csv( final_sorted_CognoSpeak_metadata )
    
    # df_metadata = pd.read_csv( '../data/CognoSpeak_metadata__2025_07_24.csv' )
    
    
    # # ## The following has been excluded as Q13 was extremely long. 
    # # df_metadata = df_metadata[df_metadata.dir_name != 'S_23555_240125_175547']
    
    
    # # ## Testing ... 
    # # df_metadata = df_metadata[df_metadata.dir_name == 'R_00013_230802_123716']
    # # df_metadata = df_metadata[df_metadata.dir_name == 'R_03190_241119_130110']
    # # df_metadata = df_metadata[df_metadata.dir_name == 'R_58844_241015_194049']
    # # df_metadata = df_metadata[df_metadata.dir_name == 'S_03399_241003_150551']
    
    
    # df_metadata = df_metadata.sort_values(by=["dir_name"])
    
    # df_metadata = df_metadata.reset_index(drop=True)
    
    
    
    
    
    
    # '''
    # This is the section responsible for fixing the manually annotated audio ... 
    # MANUAL ANNOATTION: to be done in Audacity. 
    # The file which contains the other question prompt, needs to be opened in Audacity, and then the protion will be selected (Command + B) which contains the audio for that prompt, and then the label needs to be exported to "Audacity_labels" in Documents, which will be copied to '../data/'
    # '''
    
    
    # ## Read the manual annotations 
    
    # ANNOT_DIR = '../data/Audacity_labels/'
    # backup_audio_overlap_dir = '../data/Audio_Overlap_backUp/'
    
    
    # manual_annots = glob.glob( ANNOT_DIR + '*.txt')
    
    # # ## This is just for testing .. 
    # # manual_annots = manual_annots[:1]
    
    # ## I need to change all the audio files which might appear twice under two dirs (the MND_ issue)
    
    # manual_annot_files = [x.split(ANNOT_DIR)[-1] for x in manual_annots ]
    
    # # print('manual annotated files .. ', manual_annot_files)
    
    # print('Reading the manual annotations and adjusting the audio accordingly ... ')
    # for a_file in tqdm(natsorted(manual_annot_files)):
        
        
    #     # if len(glob.glob(backup_audio_overlap_dir + '*/*' + a_file.replace('.txt', '.wav') ) ) == 0:
            
    #     wav_files = glob.glob( final_extract_dir + '*/*' + a_file.replace('.txt', '.wav')  )
        
    #     # print('Corresponding audio files: ')
    #     # print(wav_files)
        
    #     for a_wav_file in wav_files:
            
            
            
    #         ## Copy Original to backUP ... 
            
    #         dest_file = a_wav_file.replace(final_extract_dir, backup_audio_overlap_dir)
            
    #         # print('original file path .. ', a_wav_file)
    #         # print('backup file path ',  dest_file)
            
            
    #         if not os.path.exists( dest_file ):
                
    #             # sys.stdout.flush()
    #             # time.sleep(100000000)
                
    #             dest_dir = dest_file.replace(a_file.replace('.txt', '.wav'), '')
                
    #             if not os.path.isdir(dest_dir):
    #                 os.mkdir(dest_dir)
                
                
                
    #             copy_cmd = 'cp {} {}'.format( a_wav_file, a_wav_file.replace(final_extract_dir, backup_audio_overlap_dir) )
                
    #             copy_a_file(copy_cmd, a_wav_file)
                
                
                
    #             ## overwite the exiting file ... 
                
    #             annot_cont = read_file( ANNOT_DIR + a_file )
                
    #             st_T = math.floor(float(annot_cont.split('\t')[0]))
    #             end_T = math.ceil(float(annot_cont.split('\t')[1]))
                
                
    #             y_audio, SR = librosa.load(a_wav_file, offset=st_T, duration=(float(end_T)-float(st_T)), sr = None)
                
                
    #             sf.write( a_wav_file, y_audio, SR, subtype='PCM_24')
                
    #         else:
    #             print('FIle already exists: ', dest_file)
                
    # # else:
    # #     print('Audio is already sorted for: ', dest_file)
            
    #         ## I also need to update the sorted audio to the shared drive for others as well 
            
    #         dest_file = a_wav_file.replace(final_extract_dir, share_audio_dir)
            
    #         if os.path.exists( dest_file ):
    #             copy_cmd = 'cp {} {}'.format( a_wav_file, dest_file )
    #             copy_a_file(copy_cmd, a_wav_file)
            
            
            
    #         ## Delete the exisitng ASR outputs as well, if they exist ... 
            
    #         check_delete_ASR_txt(a_wav_file, ASR_trans_out_nemo_16kHz)
            
    #         check_delete_ASR_txt(a_wav_file, ASR_trans_out_wav2vec2_16kHz)
            
    #         check_delete_ASR_txt(a_wav_file, ASR_trans_out_whp_med_44kHz)
            
    #         check_delete_ASR_txt(a_wav_file, share_audio_dir)
            
            
    #         ## Delete the coverted 16 kHz audio as well 
            
    #         check_delete_audio(a_wav_file, final_ext_16kHz_dir)
            
            
            
    # print('Amending the audio according to the manual annotations is done ... ')   
            
    executionTime = (datetime.now() - startTime)
    current_time = datetime.now().strftime("%Y/%m/%d at %H:%M:%S")
    print('\n\nThe script completed at: ' + str(current_time))
    print('Execution time: ' + str(executionTime), ' \n\n')
    
    
    
    
    
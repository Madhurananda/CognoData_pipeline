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


# from silero_vad import load_silero_vad, read_audio, get_speech_timestamps

import matplotlib.pyplot as plt

from scipy import signal

# import librosa
# import soundfile as sf

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


def copy_a_file(copy_cmd, a_wav_file):
    if_faluty = do_exec_cmd(copy_cmd)
    
    if if_faluty == 1:
        
        print('This file was not copied sucessfully : ', a_wav_file)


def check_delete_audio(a_wav_file, target_dir):
    dest_file = a_wav_file.replace(final_extract_dir, target_dir)
    if os.path.exists( dest_file ):
        rm_cmd = 'rm {}'.format( dest_file )
        copy_a_file(rm_cmd, a_wav_file)



def check_delete_ASR_txt(a_wav_file, target_dir):
    dest_file = a_wav_file.replace(final_extract_dir, target_dir).replace('.wav', '.txt')
    if os.path.exists( dest_file ):
        rm_cmd = 'rm {}'.format( dest_file )
        copy_a_file(rm_cmd, a_wav_file)
    
    dest_file = a_wav_file.replace(final_extract_dir, target_dir).replace('.wav', '.dict')
    if os.path.exists( dest_file ):
        rm_cmd = 'rm {}'.format( dest_file )
        copy_a_file(rm_cmd, a_wav_file)
        
    dest_file = a_wav_file.replace(final_extract_dir, target_dir).replace('.wav', '__CHAR.csv')
    if os.path.exists( dest_file ):
        rm_cmd = 'rm {}'.format( dest_file )
        copy_a_file(rm_cmd, a_wav_file)
    
    dest_file = a_wav_file.replace(final_extract_dir, target_dir).replace('.wav', '__WORD.csv')
    if os.path.exists( dest_file ):
        rm_cmd = 'rm {}'.format( dest_file )
        copy_a_file(rm_cmd, a_wav_file)
        
    dest_file = a_wav_file.replace(final_extract_dir, target_dir).replace('.wav', '__SEG.csv')
    if os.path.exists( dest_file ):
        rm_cmd = 'rm {}'.format( dest_file )
        copy_a_file(rm_cmd, a_wav_file)














def do_find_overlap(args):
    
    a_dir = args[0]
    
    # if_overlap = False
    
    df_overlap_temp = pd.DataFrame([], columns=['dir_name', 'find_Q', 'Overlap_len', 'media_len', 'media_type'])
    
    # print('a_dir : ', a_dir)
    
    med_Tp = ''
    
    json_files = glob.glob( extracted_data_dir + a_dir + '/*.json' )
    
    # print('json_files : ')
    # print(json_files)
    
    if len(json_files) > 1:
        print('Going to stop: There are more than 1 JSON file, investigate ... ')
        sys.stdout.flush()
        time.sleep(100000000)
    
    json_file = json_files[0]
    
    
    with open(json_file, 'r') as f:
        dict_json = json.load(f)
    
    
    
    if df_metadata[df_metadata.dir_name == a_dir].assessment_type.values[0] == 'CognoStroke Short Assessment':
        INCR = 1
    else:
        INCR = 2
    
    
    
    # L_Qs = ['Q12']
    
    for aQ in L_Qs:
        
        # print(aQ)
        
        i_aQ = int(aQ.split('Q')[-1])
        
        an_ori_vS = glob.glob( extracted_data_dir + a_dir + '/*'+aQ+'.*' )
        
        if len(an_ori_vS) > 0:
            
            if len(an_ori_vS) > 1:
                print('Going to stop: There are more than 1 video file, investigate ... ')
                print('an_ori_vS : ')
                print(an_ori_vS)
                sys.stdout.flush()
                time.sleep(100000000)
            
            an_ori_v = an_ori_vS[0]
            
            if an_ori_v.endswith('wav'):
                # an_conv_v = an_ori_v
                an_conv_v = an_ori_v.replace( extracted_data_dir, extracted_data_dir_temp_dir )
                media_cmd = 'ffmpeg -loglevel quiet -i {} -vn -ab 128k -ar {} -y {}'.format(an_ori_v, SR, an_conv_v)
                med_Tp = 'WEB_AUDIO'
                
            elif an_ori_v.endswith('webm'):
                
                an_conv_v = an_ori_v.replace('.webm', '.mp4').replace( extracted_data_dir, extracted_data_dir_temp_dir )
                media_cmd = 'ffmpeg -loglevel quiet -i {} {}'.format(an_ori_v, an_conv_v)
                med_Tp = 'WEB_VIDEO'
                
            elif an_ori_v.endswith('mov'):
                
                an_conv_v = an_ori_v.replace('.mov', '.mp4').replace( extracted_data_dir, extracted_data_dir_temp_dir )
                media_cmd = 'ffmpeg -loglevel quiet -i {} -codec copy {}'.format(an_ori_v, an_conv_v)
                med_Tp = 'iPad_VIDEO'
                
            elif an_ori_v.endswith('m4a'):
                
                an_conv_v = an_ori_v.replace('.m4a', '.wav').replace( extracted_data_dir, extracted_data_dir_temp_dir )
                media_cmd = 'ffmpeg -loglevel quiet -i {} -vn -ab 128k -ar {} -y {}'.format(an_ori_v, SR, an_conv_v)
                med_Tp = 'iPad_AUDIO'
                
            else:
                print('Going to stop: It seems that there are some UNKNOWN type of media files for: ', an_ori_v, ' insdie : ', extracted_data_dir)
                sys.stdout.flush()
                time.sleep(100000000)
            
            
            ## If there is a __SORTED.mp4, then this one is already fixed, skip it ... 
            if not os.path.exists( an_conv_v.replace('.mp4', '__SORTED.mp4') ):
                
                if not os.path.exists( an_conv_v ):
                
                    # print('an_ori_v: ', an_ori_v)
                    # print('an_conv_v: ', an_conv_v)
                    
                    
                    dest_dir = extracted_data_dir_temp_dir+a_dir
                    
                    if not os.path.isdir(dest_dir):
                        os.mkdir(dest_dir)
                    
                    
                    # an_ori_v = '../data/EXTRACTED_RAW_DATA/S_17740_250215_184704/S_17740_250215_184704_Q12.webm'
                    # an_conv_v = an_ori_v.replace('.webm', '.mp4')
                    
                    # if not an_ori_v.endswith('wav'):
                    
                        # media_cmd = 'ffmpeg -loglevel quiet -i {} -codec copy {}'.format(an_ori_v, an_conv_v)
                    do_exec_cmd(media_cmd)
                    
                    
                stream = os.popen('ffprobe -i {} -show_entries format=duration -v quiet -of csv="p=0"'.format(an_conv_v))
                output = stream.read()
                
                
                
                try:
                    media_Len = float(output)
                    
                    # print('\n\n******a_dir: ', a_dir)
                    # print('aQ : ', aQ)
                    # print('media_Len: ', media_Len)
                    
                    
                    '''
                    (indexes are for results ... )
                    Here, index 0 to 2 are for practice question, index 3 starts from question1 and so on ... 
                    For example, Q12 corresponds to index: 14. 
                    
                    '''
                    
                    # if not i_aQ+2 in dict_json['assessment']['artifact']['results']:
                        
                    #     print('This question is not in here .. ', aQ)
                    
                    # print('Question :', aQ)
                    
                    ## I need the follwing line for CognoMND assessments
                    # try:
                    
                    
                        
                    if 'timestamps' in dict_json['assessment']['artifact']['results'][i_aQ+INCR]['itemResult']:
                    
                        for i in range(len(dict_json['assessment']['artifact']['results'][i_aQ+INCR]['itemResult']['timestamps'])):
                            
                            if dict_json['assessment']['artifact']['results'][i_aQ+INCR]['itemResult']['timestamps'][i]['log'] == 'started recording':
                                start_time = dict_json['assessment']['artifact']['results'][i_aQ+INCR]['itemResult']['timestamps'][i]['timestamp']
                                # print('start time: ')
                                # print(dict_json['assessment']['artifact']['results'][i_aQ+INCR]['itemResult']['timestamps'][i]['timestamp'])
                                
                            elif dict_json['assessment']['artifact']['results'][i_aQ+INCR]['itemResult']['timestamps'][i]['log'] == 'stopped recording':
                                end_time = dict_json['assessment']['artifact']['results'][i_aQ+INCR]['itemResult']['timestamps'][i]['timestamp']
                                # print('end time: ')
                                # print(dict_json['assessment']['artifact']['results'][i_aQ+INCR]['itemResult']['timestamps'][i]['timestamp'])
                            
                            
                        t1 = datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S.%f")
                        # print('Start time:', t1.time())
                        
                        t2 = datetime.strptime(end_time, "%Y-%m-%d %H:%M:%S.%f")
                        # print('End time:', t2.time())
                        
                        # get difference
                        delta = t2 - t1
                        
                        log_time_diff = float(delta.total_seconds())
                        
                        # # time difference in seconds
                        # print('log_time_diff : ', log_time_diff)
                        
                        if log_time_diff > media_Len+3:
                            
                            print('log_time_diff: ', log_time_diff)
                            print('media_Len : ', media_Len)
                            
                            print('CHECK THIS: The logged time is longer than the media, for the dir: ', a_dir, ' for question: ', aQ)
                            
                            sys.stdout.flush()
                            # time.sleep(100000000)
                            
                            
                        overlap_time = media_Len - log_time_diff
                        
                        if overlap_time > 1:
                            print('\n\n****** This question has overlap for dir: ', a_dir, ' from previous question: ', aQ, ' for ', overlap_time, ' sec \n\n' )
                            sys.stdout.flush()
                            
                            df_overlap_temp.loc[len(df_overlap_temp.index)] = [a_dir] + [aQ] + [overlap_time] + [media_Len] + [med_Tp]
                    # except:
                    #     print(' **** dir: ', a_dir, ' question: ', aQ)
                    #     sys.stdout.flush()
                    #     time.sleep(100000000)
                    
                    
                # except:
                except ValueError as e:
                    print(e, ' for dir: ', a_dir, ' question: ', aQ)
                    # print('output: ', media_Len)
                    # print('a_dir: ', a_dir)
                    # print('aQ : ', aQ)
                    # sys.exit(0)
                    sys.stdout.flush()
                    
                # time.sleep(100000000)
            
            
                
                
    return df_overlap_temp





if __name__=='__main__' and '__file__' in globals():
    
    
    # startTime = datetime.now()
    # current_time = startTime.strftime("%Y/%m/%d at %H:%M:%S")
    # print('\n\nThe script starting at: ' + str(current_time), ' \n\n' )
    
    
    N_jobs = int(sys.argv[1])
    
    # meta_csv = sys.argv[2]
    
    
    
    '''
    I have given up on this and decided to fix the audio manually 
    The audio overlap checking is working, but the mixup so bad, it is better to do it manually 
    '''
    
    
    
    
    
    ## Read the metadata ... 
    
    # df_metadata = pd.read_csv( final_sorted_CognoSpeak_metadata )
    
    # df_metadata = pd.read_csv( '../data/CognoSpeak_metadata__2025_07_24.csv' )
    
    # df_metadata = pd.read_csv( '../data/' + meta_csv )
    
    
    # df_metadata = pd.read_csv( ACE_out_all_ACE )
    
    df_metadata = pd.read_csv( Audio_info_metadata_out )
    
    
    
    
    # ## The following has been excluded as Q13 was extremely long. 
    # df_metadata = df_metadata[df_metadata.dir_name != 'S_23555_240125_175547']
    
    
    # ## Testing ... 
    # df_metadata = df_metadata[df_metadata.dir_name == 'R_00013_230802_123716']
    # df_metadata = df_metadata[df_metadata.dir_name == 'R_03190_241119_130110']
    # df_metadata = df_metadata[df_metadata.dir_name == 'R_58844_241015_194049']
    # df_metadata = df_metadata[df_metadata.dir_name == 'S_03399_241003_150551']
    
    
    
    ## I am not taking the CognoMND and Stroke assessments for now. Their log times look all messed up ...  
    # df_metadata = df_metadata[df_metadata.assessment_type != 'CognoMND Assessment']
    
    df_metadata = df_metadata[(df_metadata.assessment_type != 'CognoMND Assessment') & (df_metadata.assessment_type != 'CognoStroke Short Assessment')]
    
    # df_metadata = df_metadata[df_metadata.assessment_type == 'CognoMND Assessment']
    
    
    df_metadata = df_metadata.sort_values(by=["dir_name"])
    
    df_metadata = df_metadata.reset_index(drop=True)
    
    
    # print(df_metadata['dir_name'][966])
    
    if len(df_metadata.assessment_type.value_counts()) > 3:
        print('**** Going to stop: There are more than three types of assessmemnts, check: ')
        print(df_metadata.assessment_type.value_counts())
        sys.stdout.flush()
        time.sleep(100000000)
    
    
    
    ## Rename the previous found audio_overlap ... 
    
    if not os.path.exists( '../data/Audio_overlap_FOUND_OLD.csv' ):
        
        mv_cmd = 'mv {} {}'.format('../data/Audio_overlap_FOUND.csv', '../data/Audio_overlap_FOUND_OLD.csv')
        do_exec_cmd( mv_cmd )
    
    
    
    
    
    
    L_Qs = ['Q'+str(x) for x in range(1, 21)]
    
    
    '''
    
    THIS WAS OLD WAY by calculating audio correlations .... 
    
    I wanted to do a automatic check for audio overlap, but it seems very difficult ... 
    
    
    So, I am using the corelation threshold, which is not the best, but let's see
    
    Comnparing it using scipy signal.correlate and 'fft' method was proved the best, simple audio comparison, surprisingly didn't work 
    '''
    
    
    
    # df_corr = pd.DataFrame([], columns=['dir_name', 'find_Q', 'within_Q', 'max_C', 'offset'])
    
    # #######  muti-processing 
    # inputs = zip( list(df_metadata.dir_name) )
    
    # n_jobs = min(N_jobs, len(df_metadata))
    # print('n_jobs: ', n_jobs)
    # sys.stdout.flush()
    
    
    # print('Checking the signal corelations for possible audio overlap ... ')   
    # sys.stdout.flush()
    
    # results = tqdm(Pool(n_jobs).imap_unordered(do_calc_audio_corr, inputs), total=len(df_metadata))
    
    # for result in results:
        
    #     df_corr = pd.concat([df_corr, result], ignore_index=True, sort=False)
        
    # print('df_corr : ')
    # print(df_corr)
    
    # df_corr = df_corr.sort_values(by=["max_C"], ascending=False)
    
    # df_corr.to_csv('../data/Audio_overlap__corr.csv', index = False)
    
    
    
    # df_corr = pd.read_csv( '../data/Audio_overlap__corr.csv' )
    
    # df_corr = df_corr[df_corr.max_C > 2000]
    
    # len(set(df_corr.dir_name))
    
    
    
    
    
    
    
    
    '''
    This is the automatic way of sorting out the audio overlap 
    '''
    
    
    
    
    df_overlap = pd.DataFrame([], columns=['dir_name', 'find_Q', 'Overlap_len', 'media_len', 'media_type'])
    
    #######  muti-processing 
    inputs = zip( list(df_metadata.dir_name) )
    
    # inputs = zip( ['S_17740_250215_184704', 'S_90517_240202_133510'] )
    # inputs = zip( ['R_00320_250627_093102'] )
    
    ## An MND participant which probably has a question missing ... 
    # inputs = zip( ['MND_R_38885_240902_124951'] )
    
    # ## This ZIP has issues in making mp4, but no issues in audio ... 
    # inputs = zip( ['R_02166_240809_212100'] )
    
    # ## This one seems to have the times wrong ... 
    # inputs = zip( ['R_76622_250314_102110'] )
    
    ## This is another STROKE ... 
    # inputs = zip( ['STROKE_R_34894_250624_160501'] )
    
    
    n_jobs = min(N_jobs, len(df_metadata))
    print('n_jobs: ', n_jobs)
    sys.stdout.flush()
    
    
    print('Checking the json files for possible audio overlap ... ')   
    sys.stdout.flush()
    
    results = tqdm(Pool(n_jobs).imap_unordered(do_find_overlap, inputs), total=len(df_metadata))
    
    for result in results:
        
        df_overlap = pd.concat([df_overlap, result], ignore_index=True, sort=False)
    
    
    # sys.stdout.flush()
    # time.sleep(100000000)
    
    
    df_overlap.to_csv('../data/Audio_overlap_FOUND.csv', index = False)
    
    
    if len(df_overlap) > 0:
        print('There are new audio overlaps: : ')
        print(df_overlap)
        
        
    else:
        
        print('**** GOOD NEWWS ... NO AUDIO OVERLAP HAS BEEN FOUND. ****')
        
    sys.stdout.flush()
    
    
    
    
    
    # df_overlap_OLD = pd.read_csv( '../data/Find_Audio_overlap.csv' )
    
    # df_overlap = pd.read_csv( '../data/Audio_overlap_FOUND.csv' )
    
    
    # df_corr = df_corr.sort_values(by=["max_C"], ascending=False)
    
    
    # diff_list(df_overlap.dir_name, df_overlap_OLD.dir_name)
    
    # diff_list(df_overlap_OLD.dir_name, df_overlap.dir_name)
    
    
    
    # df_info = df_metadata.merge(df_overlap, on='dir_name', how='inner').sort_values(by=["assess_date"])[['dir_name', 'assess_date', 'find_Q']]
    
    
    
    
            
    executionTime = (datetime.now() - startTime)
    current_time = datetime.now().strftime("%Y/%m/%d at %H:%M:%S")
    print('\n\nThe script completed at: ' + str(current_time))
    print('Execution time: ' + str(executionTime), ' \n\n')
    
    
    
    
    
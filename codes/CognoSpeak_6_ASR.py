#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Apr 15 20:58:39 2024

@author: madhupahar
"""

import warnings
warnings.filterwarnings('ignore')

from main import *
from config import *

import os, sys, time



from datetime import datetime, timedelta
import glob
from tqdm import tqdm

from multiprocessing.pool import ThreadPool, Pool
from multiprocessing import cpu_count


import pandas as pd


import librosa


import soundfile as sf




## This function resmaples the audio to 16 kHz 
def do_check_resample(args):
    
    a_dir = args[0]
    
    wav_files = glob.glob( final_extract_dir+ a_dir + '/*.wav')
    
    # if len(wav_files) != 14:
    #     print('This dir does not have 14 audio files: ', a_dir)
    #     sys.stdout.flush()
    #     time.sleep(100000000)
    
    n_conv = 0
    for a_wav in wav_files:
        
        new_wav = a_wav.replace(final_extract_dir, final_ext_16kHz_dir)
        
        if not os.path.exists(new_wav):
            
            speech, rate = librosa.load(a_wav, sr=None)
            
            if rate != 16000:
                speech_16kHz = librosa.resample(speech, orig_sr=rate, target_sr=16000)
                
                check_create_dir( final_ext_16kHz_dir + new_wav.split(final_ext_16kHz_dir)[-1].split('/')[0] )
                
                sf.write(new_wav, speech_16kHz, 16000)
                
                n_conv += 1
    
    return n_conv


    
    
    
    


if __name__=='__main__' and '__file__' in globals():
    
    
    '''
    NOTES:
        Multi-processing does not work for ASR 
        I tried to use GPU but I was running out of memory 
        The audio needs to be resampled at 16 kHz, which I need to check before applying ASR 
    '''
    
    
    
    # startTime = datetime.now()
    # current_time = startTime.strftime("%Y/%m/%d at %H:%M:%S")
    # print('\n\nThe script starting at: ' + str(current_time), ' \n\n' )
    
    N_jobs = int(sys.argv[1])
    
    
    
    ## Read the metadata ... 
    
    df_metadata = pd.read_csv( final_sorted_CognoSpeak_metadata )
    
    # ## Read the Stroke and MND metadata, add two missing columns and merge with the original metadata ... 
    # df_meta_Stroke_MND = pd.read_csv( temp_ST_MND_save_out )
    # df_meta_Stroke_MND['OLD_r_ID'] = df_meta_Stroke_MND['research_ID']
    # df_meta_Stroke_MND['OLD_pseudo_unq_id'] = df_meta_Stroke_MND['pseudo_unq_id']
    
    # df_metadata = pd.concat([df_metadata, df_meta_Stroke_MND], ignore_index=True, sort=False)
    
    
    
    # ## This is testuing for a dir 
    # df_metadata = df_metadata[df_metadata.dir_name == 'R_36338_240716_112815']
    
    
    ## The following has been excluded as Q13 was extremely long. 
    df_metadata = df_metadata[df_metadata.dir_name != 'S_23555_240125_175547']
    
    ## The following assessment has some audio noise issue 
    df_metadata = df_metadata[df_metadata.dir_name != 'R_52364_240409_161809']
    
    # ## Testing ... 
    # df_metadata = df_metadata[df_metadata.dir_name == 'R_00013_230802_123716']
    # df_metadata = df_metadata[df_metadata.dir_name == 'R_03190_241119_130110']
    # df_metadata = df_metadata[df_metadata.dir_name == 'R_58844_241015_194049']
    # df_metadata = df_metadata[df_metadata.dir_name == 'S_03399_241003_150551']
    
    
    df_metadata = df_metadata.sort_values(by=["dir_name"])
    
    df_metadata = df_metadata.reset_index(drop=True)
    
    
    
    
    
    ###### Resample the audio to 16 kHz ######
    
    print('Resampling the audio to 16 kHz for Wav2Vec2 and Nemo ...')
    
    inputs = zip( list(df_metadata.dir_name) )
    
    n_jobs = min(N_jobs, len(df_metadata))
    print('n_jobs: ', n_jobs)
    sys.stdout.flush()
    
    results = Pool(n_jobs).imap_unordered(do_check_resample, inputs)
    
    N_CONV = 0
    for result in results:
        N_CONV += result
    
    print('n\n**********')
    print('Total number of audio file resampled to 16 kHz: ', N_CONV)
    print('Checking and resampling audio is complete.')
    print('**********\n\n')
    
    sys.stdout.flush()
    time.sleep(5)
    # time.sleep(100000000)
    
    
    
    ## I need to save the metadata so that it is accessible from other scripts ... 
    df_metadata.to_csv( metadata_TEMP_asr_out, index=False )
    
    
    
    
    
    
    df_ASR_repo = pd.DataFrame([], columns=['dir_name', 'audio', 'ASR', 'comment'])
    
    ASR_out_name = '../data/ASR_logs/ASR_errors__' + datetime.today().strftime('%Y_%m_%d')+ '__' + datetime.today().strftime('%H_%M_%S') + '.csv'
    
    
    
    ###########################################
    ## Whisper Medium ... 
    ## It will use the original 44.1 kHz sampled audio for better performance 
    
    print('Running Whisper Medium ASR ...')
    sys.stdout.flush()
    
    whisper_med_cmd = 'python CognoSpeak_6_ASR_whisper_med.py {} {}'.format( final_extract_dir, ASR_out_name )
    
    if os.system( whisper_med_cmd ) != 0:
        print('There is something wrong in : ', whisper_med_cmd)
    
    
    
    print('Whisper transcription is completed successfully.')
    sys.stdout.flush()
    # time.sleep(100000000)
    
    
    
    ###########################################
    ## Wav2Vec2 
    # https://huggingface.co/docs/transformers/model_doc/wav2vec2 
    ## It should use 16 kHz audio 
    
    print('Running Wav2Vec2 ASR ...')
    sys.stdout.flush()
    
    W2V2_cmd = 'python CognoSpeak_6_ASR_W2V2.py {} {}'.format( final_ext_16kHz_dir, ASR_out_name )
    
    if os.system( W2V2_cmd ) != 0:
        print('There is something wrong in : ', W2V2_cmd)
    
    
    
    print('Wav2Vec2 transcription is completed successfully.')
    sys.stdout.flush()
    # time.sleep(100000000)
    
    
    
    
    ###########################################
    ## Nvidia Nemo 
    # https://docs.nvidia.com/nemo-framework/user-guide/24.09/nemotoolkit/asr/intro.html
    ## Nvidia Nemo has cuda issues while trying to use in a loop. So, I am using it to ASR one audio at a time 
    
    print('Running Nvidia Nemo ...')
    sys.stdout.flush()
    
    for a_dir in tqdm(df_metadata.dir_name):
        
        
        wav_files = glob.glob( final_ext_16kHz_dir+ a_dir + '/*.wav')
        
        # if len(wav_files) != 14:
        #     print('This dir does not have 14 audio files: ', a_dir)
        #     sys.stdout.flush()
        #     time.sleep(100000000)
        
        for a_wav in wav_files:
            
            ###########################################
            ## Nvidia Nemo 
            # https://docs.nvidia.com/nemo-framework/user-guide/24.09/nemotoolkit/asr/intro.html
            
            
            txt_out = a_wav.replace(final_ext_16kHz_dir, ASR_trans_out_nemo_16kHz).replace('.wav', '.txt')
            # dict_out = a_wav.replace(final_ext_16kHz_dir, ASR_trans_out_nemo_16kHz).replace('.wav', '.dict')
            time_word_out = a_wav.replace(final_ext_16kHz_dir, ASR_trans_out_nemo_16kHz).replace('.wav', '__WORD.csv')
            time_char_out = a_wav.replace(final_ext_16kHz_dir, ASR_trans_out_nemo_16kHz).replace('.wav', '__CHAR.csv')
            time_seg_out = a_wav.replace(final_ext_16kHz_dir, ASR_trans_out_nemo_16kHz).replace('.wav', '__SEG.csv')
            
            check_create_dir(ASR_trans_out_nemo_16kHz+txt_out.split(ASR_trans_out_nemo_16kHz)[-1].split('/')[0])
            
            
            
            if (not os.path.exists( txt_out )) or (not os.path.exists( time_seg_out )) or  (not os.path.exists( time_word_out )) or  (not os.path.exists( time_char_out )): 
                
                nemo_cmd = 'python CognoSpeak_6_ASR_Nemo.py {} {} {} {} {} {} {}'.format( a_dir, a_wav, ASR_out_name, txt_out, time_word_out, time_char_out, time_seg_out )
                
                if os.system(nemo_cmd) != 0:
                    print('There is something wrong in : ', nemo_cmd)
                
                
                
    print('Nvidia Nemo transcription is completed successfully.')
    # sys.stdout.flush()
    # time.sleep(100000000)
    
    
    
    ## Save the metadata 
    df_metadata.to_csv(metadata_ASR_out, index=False)
    
    
    
    
    
    executionTime = (datetime.now() - startTime)
    current_time = datetime.now().strftime("%Y/%m/%d at %H:%M:%S")
    print('\n\nThe script completed at: ' + str(current_time))
    print('Execution time: ' + str(executionTime), ' \n\n')
    
    
    
    
    
    

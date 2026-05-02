#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Apr 15 20:58:39 2024

@author: madhupahar
"""


'''
This standalone script prepares the Whisper transcripts for all audio. 
This script will be called from the opther master ASR script. 
'''


import warnings
warnings.filterwarnings('ignore')

from main import *
from config import *

import os, sys, time

import whisper
import torch



from datetime import datetime, timedelta
import glob
from tqdm import tqdm


import pandas as pd





def gen_whp_word_timestamps(trans_dict, time_word_out):
    # saved_whisoer_dict = load_file( dict_out )
    
    df_word_timestamps = pd.DataFrame([], columns=['word', 'start', 'end', 'probs'])
    
    for s in trans_dict['segments']:
        # print( s )
        for a_W in s['words']:
            # print(a_W)
            a_W['word']
            a_W['start']
            a_W['end']
            a_W['probability']
            
            df_word_timestamps.loc[len(df_word_timestamps.index)] = [a_W['word']] + [a_W['start']] + [a_W['end']] + [a_W['probability']] 
    
    df_word_timestamps.to_csv(time_word_out, index=False)





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
    
    
    df_metadata = pd.read_csv( metadata_TEMP_asr_out )
    
    all_audio_dir = sys.argv[1]
    
    ASR_out_name = sys.argv[2]
    
    
    
    
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    
    
    
    
    
    ## Load ASR models ... 
    
    # model_whisper = whisper.load_model("tiny")
    # model_whisper = whisper.load_model("small")
    model_whisper = whisper.load_model("medium").to(device)
    # model_whisper = whisper.load_model("large")
    # model_whisper = whisper.load_model("turbo")
    # model_whisper = whisper.load_model("turbo.en")
    
    
    
    # ## This is just some checks with individual cases ... 
    # ## Comment out later ... 
    
    # df_metadata = df_metadata[df_metadata.dir_name == 'R_27876_231222_104522']
    # all_audio_dir = final_extract_dir
    
    
    
    
    ## This is using single CPU. It takes longer but works .... 
    
    for a_dir in tqdm(df_metadata.dir_name):
        
        
        # print('a_dir : ', all_audio_dir+ a_dir)
        
        wav_files = glob.glob( all_audio_dir+ a_dir + '/*.wav')
        
        # if len(wav_files) != 14:
        #     print('This dir does not have 14 audio files: ', a_dir)
        #     sys.stdout.flush()
        #     time.sleep(100000000)
        
        for a_wav in wav_files:
            
            
            
            ###########################################
            ## Whisper Medium ... 
            
            txt_out = a_wav.replace(all_audio_dir, ASR_trans_out_whp_med_44kHz).replace('.wav', '.txt')
            dict_out = a_wav.replace(all_audio_dir, ASR_trans_out_whp_med_44kHz).replace('.wav', '.dict')
            time_word_out = a_wav.replace(all_audio_dir, ASR_trans_out_whp_med_44kHz).replace('.wav', '__WORD.csv')
            
            
            
            check_create_dir(ASR_trans_out_whp_med_44kHz+txt_out.split(ASR_trans_out_whp_med_44kHz)[-1].split('/')[0])
            
            ## Comment out the below section to re-generate ASR for all audio files ... 
            if (not os.path.exists( txt_out )) or (not os.path.exists( dict_out )) or  (not os.path.exists( time_word_out )): 
                
                ## Check if the dict exists first ... 
                if os.path.exists( dict_out ):
                    
                    saved_whisoer_dict = load_file( dict_out )
                    
                    ## If yes, then check if the word lavel cvs file, if not generate from the saved dict
                    if not os.path.exists( time_word_out ): 
                        try:
                            gen_whp_word_timestamps(saved_whisoer_dict, time_word_out)
                        except:
                            print('\n\n**** There is a problem in loading the dictionary')
                            print('dict_out : ', dict_out)
                            print('time_word_out : ', time_word_out)
                            print('txt_out : ', txt_out)
                            print('INVESTIGATE ... ')
                            sys.stdout.flush()
                            time.sleep(100000000)
                            
                    
                    ## If yes, then check if the transcript is there, if not generate from the saved dict
                    if not os.path.exists( txt_out ):
                        write_file(txt_out, saved_whisoer_dict['text'])
                
                else:
                    
                    try:
                        
                        ## This is high lavel ... 
                        transcript = model_whisper.transcribe(
                            word_timestamps=True,
                            audio=a_wav,
                            language="en"
                        )
                        
                        # print('transcript: ')
                        # print(transcript)
                        
                        
                        
                        ## save the entire transcript and word timestamps ... 
                        save_file(dict_out, transcript)
                        gen_whp_word_timestamps(transcript, time_word_out)
                        
                        
                        
                        ## save the final transcript files ... 
                        # append_file(txt_out, transcript['text'])
                        # write_file(txt_out, transcript['text'])
                        write_file(txt_out, str(transcript['text']))
                        
                        # torch.cuda.empty_cache()
                        
                        
                    except Exception as e:
                        
                        if os.path.exists( ASR_out_name ):
                            df_ASR_repo = pd.read_csv( ASR_out_name )
                        else:
                            
                            df_ASR_repo = pd.DataFrame([], columns=['dir_name', 'audio', 'ASR', 'comment'])
                        
                        print('Error message: ')
                        print(e)
                        df_ASR_repo.loc[len(df_ASR_repo.index)] = [a_dir] + [a_wav] + ['Whisper_medium'] + [e] 
                        df_ASR_repo.to_csv(ASR_out_name, index=False)
            
            
            
    
    
    executionTime = (datetime.now() - startTime)
    current_time = datetime.now().strftime("%Y/%m/%d at %H:%M:%S")
    print('\n\nThe Whisper ASR script completed at: ' + str(current_time))
    print('Execution time: ' + str(executionTime), ' \n\n')
    
    
    
    
    
    

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

import torch


from datetime import datetime, timedelta
import glob
from tqdm import tqdm



import pandas as pd


# Wav2Vec2
from transformers import AutoTokenizer, AutoFeatureExtractor, AutoModelForCTC
import librosa







def gen_w2v2_word_timestamps(outputs, time_word_out):
    
    df_word_timestamps = pd.DataFrame([], columns=['word', 'start', 'end'])
    for w in outputs.word_offsets:
        
        word = w["word"]
        start = w["start_offset"] * time_offset
        end = w["end_offset"] * time_offset
        
        df_word_timestamps.loc[len(df_word_timestamps.index)] = [word] + [start] + [end] 
        
    # print(df_word_timestamps)
    df_word_timestamps.to_csv(time_word_out, index=False)



def gen_w2v2_char_timestamps(outputs, time_char_out):
    
    df_char_timestamps = pd.DataFrame([], columns=['char', 'start', 'end'])
    for c in outputs.char_offsets:
        
        char = c["char"]
        start = c["start_offset"] * time_offset
        end = c["end_offset"] * time_offset
        
        df_char_timestamps.loc[len(df_char_timestamps.index)] = [char] + [start] + [end] 
    
    # print(df_char_timestamps)
    df_char_timestamps.to_csv(time_char_out, index=False)







if __name__=='__main__' and '__file__' in globals():
    
    
    '''
    NOTES:
        Multi-processing does not work for ASR 
        I tried to use GPU but I was running out of memory 
        The audio needs to be resampled at 16 kHz, which I need to check before applying ASR 
    '''
    
    startTime = datetime.now()
    current_time = startTime.strftime("%Y/%m/%d at %H:%M:%S")
    print('\n\nThe script starting at: ' + str(current_time), ' \n\n' )
    
    
    df_metadata = pd.read_csv( metadata_TEMP_asr_out )
    
    all_audio_dir = sys.argv[1]
    
    ASR_out_name = sys.argv[2]
    
    
    
    
    ## Load ASR models ... 
    
    
    model_wav2vec2 = AutoModelForCTC.from_pretrained("facebook/wav2vec2-base-960h")
    tokenizer_wav2vec2 = AutoTokenizer.from_pretrained("facebook/wav2vec2-base-960h")
    feature_extractor_wav2vec2 = AutoFeatureExtractor.from_pretrained("facebook/wav2vec2-base-960h")
    
    ## The sampling rate for Wav2Vec2 
    SR_WAV2VEC2 = 16000
    
    
    
    
    
    
    
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
            ## Wav2Vec2 
            # https://huggingface.co/docs/transformers/model_doc/wav2vec2 
            
            
            txt_out = a_wav.replace(all_audio_dir, ASR_trans_out_wav2vec2_16kHz).replace('.wav', '.txt')
            dict_out = a_wav.replace(all_audio_dir, ASR_trans_out_wav2vec2_16kHz).replace('.wav', '.dict')
            time_word_out = a_wav.replace(all_audio_dir, ASR_trans_out_wav2vec2_16kHz).replace('.wav', '__WORD.csv')
            time_char_out = a_wav.replace(all_audio_dir, ASR_trans_out_wav2vec2_16kHz).replace('.wav', '__CHAR.csv')
            
            check_create_dir(ASR_trans_out_wav2vec2_16kHz+txt_out.split(ASR_trans_out_wav2vec2_16kHz)[-1].split('/')[0])
            
            
            if (not os.path.exists( txt_out )) or (not os.path.exists( dict_out )) or  (not os.path.exists( time_word_out )) or  (not os.path.exists( time_char_out )): 
                
                ## Check if the dict exists first ... 
                if os.path.exists( dict_out ):
                    
                    saved_w2v2_dict = load_file( dict_out )
                    
                    ## If yes, then check if the word lavel csv file, if not generate from the saved dict
                    if not os.path.exists( time_word_out ): 
                        gen_w2v2_word_timestamps(saved_w2v2_dict, time_word_out)
                    
                    ## If yes, then check if the char lavel csv file, if not generate from the saved dict
                    if not os.path.exists( time_char_out ): 
                        gen_w2v2_char_timestamps(saved_w2v2_dict, time_char_out)
                    
                    ## If yes, then check if the transcript is there, if not generate from the saved dict
                    if not os.path.exists( txt_out ):
                        # write_file(txt_out, saved_whisoer_dict['text'])
                        write_file(txt_out, saved_w2v2_dict.text)
                
                else:
                    
                    try:
                        
                        # model_wav2vec2 = AutoModelForCTC.from_pretrained("facebook/wav2vec2-base-960h").to(device)
                        # tokenizer_wav2vec2 = AutoTokenizer.from_pretrained("facebook/wav2vec2-base-960h")
                        # feature_extractor_wav2vec2 = AutoFeatureExtractor.from_pretrained("facebook/wav2vec2-base-960h")
                        
                        speech, rate = librosa.load(a_wav, sr=SR_WAV2VEC2)
                        
                        
                        
                        # forward sample through model to get greedily predicted transcription ids
                        # input_values = feature_extractor(sample["audio"]["array"], return_tensors="pt").input_values
                        input_values = feature_extractor_wav2vec2(speech, return_tensors="pt", sampling_rate = SR_WAV2VEC2).input_values
                        # input_values = tokenizer(speech, return_tensors = 'pt').input_values
                        logits = model_wav2vec2(input_values).logits[0]
                        pred_ids = torch.argmax(logits, axis=-1)
                        
                        # retrieve word stamps (analogous commands for `output_char_offsets`)
                        outputs = tokenizer_wav2vec2.decode(pred_ids, output_word_offsets=True, output_char_offsets=True)
                        # outputs = tokenizer.decode(pred_ids, output_word_offsets=True, output_char_offsets=True)
                        
                        # compute `time_offset` in seconds as product of downsampling ratio and sampling_rate
                        time_offset = model_wav2vec2.config.inputs_to_logits_ratio / feature_extractor_wav2vec2.sampling_rate
                        
                        
                        
                        ## save the final transcript files ... 
                        write_file(txt_out, outputs.text)
                        
                        
                        ## save the entire transcript and word timestamps ... 
                        save_file(dict_out, outputs)
                        
                        
                        
                        gen_w2v2_char_timestamps(outputs, time_char_out)
                        
                        gen_w2v2_word_timestamps(outputs, time_word_out)
                        
            
                    except Exception as e:
                        
                        if os.path.exists( ASR_out_name ):
                            df_ASR_repo = pd.read_csv( ASR_out_name )
                        else:
                            
                            df_ASR_repo = pd.DataFrame([], columns=['dir_name', 'audio', 'ASR', 'comment'])
                            
                        print('Error message: ')
                        print(e)
                        df_ASR_repo.loc[len(df_ASR_repo.index)] = [a_dir] + [a_wav] + ['Wav2Vec2'] + [e] 
                        df_ASR_repo.to_csv(ASR_out_name, index=False)
            
            
            
            
    
    executionTime = (datetime.now() - startTime)
    current_time = datetime.now().strftime("%Y/%m/%d at %H:%M:%S")
    print('\n\nThe Wav2Vec2 script completed at: ' + str(current_time))
    print('Execution time: ' + str(executionTime), ' \n\n')
    
    
    
    
    
    

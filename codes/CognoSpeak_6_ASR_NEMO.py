#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Apr 15 20:58:39 2024

@author: madhupahar
"""

import warnings
warnings.filterwarnings('ignore')

from main import *

import os, sys, time

import torch


import pandas as pd



import nemo.collections.asr as nemo_asr
from omegaconf import OmegaConf, open_dict






if __name__=='__main__' and '__file__' in globals():
    
    
    
    '''
    NOTES:
        I realised that I need to run Nemo for each audio file seperately otherwise I will run out of cuda memory. 
    '''
    
    
    
    
    a_dir = sys.argv[1]
    
    a_wav = sys.argv[2]
    
    ASR_out_name = sys.argv[3]
    
    txt_out = sys.argv[4]
    time_word_out = sys.argv[5]
    time_char_out = sys.argv[6]
    time_seg_out = sys.argv[7]
    
    
    
    
    
    
    
    ###########################################
    ## Nvidia Nemo 
    # https://docs.nvidia.com/nemo-framework/user-guide/24.09/nemotoolkit/asr/intro.html
    
    
    try: 
        
        ## Here, stt_en_fastconformer_transducer_large is the English corpus, so the output will be in English ... 
        model_nemo = nemo_asr.models.ASRModel.from_pretrained("stt_en_fastconformer_transducer_large")
        
        decoding_cfg = model_nemo.cfg.decoding
        with open_dict(decoding_cfg):
            decoding_cfg.preserve_alignments = True
            decoding_cfg.compute_timestamps = True
            decoding_cfg.segment_seperators = [".", "?", "!"]
            decoding_cfg.word_seperator = " "
            model_nemo.change_decoding_strategy(decoding_cfg)
        
        # specify flag `return_hypotheses=True``
        hypotheses = model_nemo.transcribe([a_wav], return_hypotheses=True)
        
        # if hypotheses form a tuple (from RNNT), extract just "best" hypotheses
        if type(hypotheses) == tuple and len(hypotheses) == 2:
            hypotheses = hypotheses[0]
        
        timestamp_dict = hypotheses[0].timestep # extract timesteps from hypothesis of first (and only) audio file
        # print("Hypothesis contains following timestep information :", list(timestamp_dict.keys()))
        
        
        # print('a_wav: ', a_wav)
        # print('timestamp_dict : ', timestamp_dict)
        
        # sys.stdout.flush()
        # time.sleep(100000000)
        
        
        
        # For a FastConformer model, you can display the word timestamps as follows:
        # 80ms is duration of a timestep at output of the Conformer
        time_stride = 8 * model_nemo.cfg.preprocessor.window_stride
        
        # char_timestamps = timestamp_dict['char']
        # word_timestamps = timestamp_dict['word']
        # segment_timestamps = timestamp_dict['segment']
        
        
        
        df_char_timestamps = pd.DataFrame([], columns=['char', 'start', 'end'])
        
        for ch in timestamp_dict['char']:
            start = ch['start_offset'] * time_stride
            end = ch['end_offset'] * time_stride
            char = ch['char'] if 'char' in ch else ch['word']
            
            df_char_timestamps.loc[len(df_char_timestamps.index)] = [char] + [start] + [end] 
        
        df_char_timestamps.to_csv(time_char_out, index=False)
        
        
        
        df_word_timestamps = pd.DataFrame([], columns=['word', 'start', 'end'])
        
        for stamp in timestamp_dict['word']:
            start = stamp['start_offset'] * time_stride
            end = stamp['end_offset'] * time_stride
            word = stamp['char'] if 'char' in stamp else stamp['word']
            
            df_word_timestamps.loc[len(df_word_timestamps.index)] = [word] + [start] + [end] 
        
        df_word_timestamps.to_csv(time_word_out, index=False)
        
        
        
        df_segment_timestamps = pd.DataFrame([], columns=['segment', 'start', 'end'])
        
        for stamp in timestamp_dict['segment']:
            start = stamp['start_offset'] * time_stride
            end = stamp['end_offset'] * time_stride
            segment = stamp['segment']
            
            df_segment_timestamps.loc[len(df_segment_timestamps.index)] = [segment] + [start] + [end] 
        
        df_segment_timestamps.to_csv(time_seg_out, index=False)
        
        if len(df_segment_timestamps.segment) > 1:
            print('The transcript from Nemo should not be longer than 1. Check the audio:  ', a_wav)
            sys.stdout.flush()
            time.sleep(100000000)
        else:
            
            if len(df_segment_timestamps.segment) > 0:
            
                transcript_val = df_segment_timestamps.segment[0]
            else:
                transcript_val = ''
                
            write_file(txt_out, transcript_val)
        
        torch.cuda.empty_cache()
    
    except Exception as e:
        
        if os.path.exists( ASR_out_name ):
            df_ASR_repo = pd.read_csv( ASR_out_name )
        else:
            
            df_ASR_repo = pd.DataFrame([], columns=['dir_name', 'audio', 'ASR', 'comment'])
        
        print('Error message: ')
        print(e)
        df_ASR_repo.loc[len(df_ASR_repo.index)] = [a_dir] + [a_wav] + ['Nemo'] + [e] 
        df_ASR_repo.to_csv(ASR_out_name, index=False)
        
    
    
    
    
    
    

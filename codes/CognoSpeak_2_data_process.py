#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Feb 15 10:38:17 2024

@author: madhurananda
"""

import subprocess

from main import *
from config import *
check_env('ACONDA')


import numpy as np
import pandas as pd
import time

import json

import shutil
import pickle
import csv
# import librosa
import sklearn

import matplotlib.pyplot as plt
import random

from datetime import datetime, timedelta
from tqdm import tqdm
import zipfile
import glob

import librosa
import soundfile as sf



import warnings

import platform
if platform.system() == 'Darwin':
    from multiprocess.pool import ThreadPool, Pool
else:
    from multiprocessing.pool import ThreadPool, Pool
    
from multiprocessing import cpu_count

from natsort import natsorted



# # Live on the wild side
# pd.options.mode.chained_assignment = None
# warnings.simplefilter(action = "ignore",category = FutureWarning)


def do_extract_ZIPs(args):
    a_zip_file = args[0]
    
    r_ID = a_zip_file.split('/')[-1].split('.zip')[0]
    # to_extract_dir = extracted_data_dir + r_ID
    to_extract_dir = extracted_data_dir + r_ID.replace('__', '_')
    if_extract = 0
    
    # print('\na_zip_file :', a_zip_file)
    # print('r_ID : ', r_ID)
    # print('to_extract_dir : ', to_extract_dir)
    # sys.stdout.flush()
    # time.sleep(100000000)
    
    if not os.path.isdir(to_extract_dir):
        print('\nUnzipping now .... ', r_ID, '\n')
        sys.stdout.flush()
        with zipfile.ZipFile(a_zip_file, 'r') as zip_ref:
            zip_ref.extractall(to_extract_dir)
        if_extract = 1
        
    return if_extract



    



## Generate 10 seconds of white noise 
def gen_whiteNoise(if_save):
    num_samples = 10*SR
    random.seed(1)
    white_noise = []
    # generate random numbers between 0-1
    for _ in range(int(num_samples/2)):
        value = random.random()
        white_noise.append(value)
        # print(value)
    for _ in range(int(num_samples/2)):
        value = - random.random()
        white_noise.append(value)
    
    white_noise = [i*wht_ns_mult for i in white_noise]
    
    random.shuffle( white_noise )
    
    if if_save == 1:
        ## Save this white noise ... 
        sf.write(wht_ns_path, white_noise, SR)
    
    # plt.plot(  white_noise )
    
    return white_noise


## Generate 10 seconds of silence 
def gen_silence(if_save):
    num_samples = 10*SR
    silence = [0]*num_samples
    
    if if_save == 1:
        ## Save this white noise ... 
        # sf.write(silence_path, silence, SR)
        # I tried with librosa but it did npt work, so using sox 
        
        # sox -n -r 44100 silent10sec.wav trim 0.0 10.0
        
        sox_silence_cmd = 'sox -n -r {} {} trim 0.0 10.0'.format(SR, silence_path)
        
        os.system(sox_silence_cmd)
        
    return silence


def convert_media_file(a_file, output_audio_list, no_librosa):
    ## Collected via web video
    if '.webm' in a_file: 
        output_audio = a_file.replace(extracted_data_dir, final_extract_dir).replace('.webm', '.wav')
    ## Collected via iPad video
    elif '.mov' in a_file: 
        output_audio = a_file.replace(extracted_data_dir, final_extract_dir).replace('.mov', '.wav')
    ## Collected via iPad audio
    elif '.m4a' in a_file: 
        output_audio = a_file.replace(extracted_data_dir, final_extract_dir).replace('.m4a', '.wav')
    ## Collected via web audio
    elif '.wav' in a_file: 
        output_audio = a_file.replace(extracted_data_dir, final_extract_dir)
    else: 
        print('There must nbe something very wronggg ... ')
    
    
    output_audio_list.append( output_audio )
    
    # print('a_file : ', a_file)
    # print('output_audio: ', output_audio)
    # sys.stdout.flush()
    # time.sleep(100000000)
    
    
    # If the audio already exists, then do nothing 
    if not os.path.exists(output_audio): 
        
        out_dir = output_audio.replace(output_audio.split('/')[-1], '')
        
        # print('out_dir : ', out_dir)
        # print('Does it exist: ', os.path.exists(out_dir))
        # sys.stdout.flush()
        
        if not os.path.isdir(out_dir): 
            os.mkdir(out_dir)
            
        
        video_audio_cmd = 'ffmpeg -loglevel quiet -i {} -vn -ab 128k -ar {} -y {}'.format(a_file, SR, output_audio)
        os.system(video_audio_cmd)
    
    
    

    if not os.path.exists(output_audio):
        print('WARNING: output audio not created:', output_audio)
        sys.stdout.flush()
        return output_audio_list, output_audio, 1  # force no_librosa
    
    ## If the audio is greater than 300 MB, raise a message ... 
    if os.path.getsize(output_audio)/(1024*1024) > 300:
        print('This is a large audio file: ', output_audio, ' ; will take time to read the converted wav file ... ')
        sys.stdout.flush()
        no_librosa = 1
    
    return output_audio_list, output_audio, no_librosa


# def do_convert_video_audio(args):
    
#     a_file_ID = args[0]
    
#     print(f"[{datetime.now()}] PID {os.getpid()} starting {a_file_ID}", flush=True)
    
#     if_N_complete = 0
#     l_N_complete = ''
#     # no_SOX_IDs = []
    
#     all_files = natsorted(glob.glob(extracted_data_dir + a_file_ID+'/*'))
    
    
#     if len(all_files) == 0:
#         print('Skipping empty dir:', a_file_ID)
#         sys.stdout.flush()
#         return a_file_ID, [NO_EXIST_STR]*(MAX_LEN_MEDIA_FILES-1), 1, a_file_ID, '', '', 'NO'
    
    
#     to_transcrpt_audio = []
#     to_ASR_audio = []
    
#     transcript_out_dir = final_transcript_dir + a_file_ID + '/'
#     transcript_out_audio = transcript_out_dir + a_file_ID + '.wav'
#     ASR_out_audio = transcript_out_dir + a_file_ID + '_ASR.wav'
#     transcript_out_audio_mp3 = transcript_out_dir + a_file_ID + '.mp3'
    
#     # print('\n\na_file_ID : ', a_file_ID)
#     # print('transcript_out_dir : ', transcript_out_dir)
#     # print('transcript_out_audio : ', transcript_out_audio, '\n\n')
#     # sys.stdout.flush()
#     # time.sleep(100000000)
    
    
#     ## Get the json file, it will give an error if there are no json file inside .... 
#     the_json = [ x for x in all_files if x.endswith('.json') ][0]
    
#     with open(the_json, 'r') as f:
#         dict_json = json.load(f)
    
#     assessment_ID = dict_json['assessment']['taskInstanceIdentity']
    
#     assessment_type = dict_json['assessment']['assessmentName']
    
    
#     ####### Get the information about the audio/video files ... 
    
#     ## drop the files ends with .csv and .json and those with 'caregiver' in it ... 
    
#     # all_media_files = [ x for x in all_files if not x.endswith('.csv') and not x.endswith('.json') ]
    
    
#     all_media_files = [
#         x for x in all_files
#         if not x.endswith('.csv')
#         and not x.endswith('.json')
#         and 'caregiver' not in x.lower()
#     ]
    
    
#     if len(all_media_files) == 0:
#         print('No media files in:', a_file_ID)
#         sys.stdout.flush()
#         return a_file_ID, [NO_EXIST_STR]*(MAX_LEN_MEDIA_FILES-1), 1, a_file_ID, '', '', 'NO'
    
#     file_type_list = []
    
#     for i in range(1,MAX_LEN_MEDIA_FILES):
        
#         m_f_exist = 0
        
#         for a_m_f in all_media_files:
#             if '_Q'+str(i)+'.' in a_m_f:
#                 m_f_exist = 1
#                 if a_m_f.endswith('.webm'):
#                     file_type_list.append('VIDEO_WEB')
#                 elif a_m_f.endswith('.mov'):
#                     file_type_list.append('VIDEO_iPad')
#                 elif a_m_f.endswith('.m4a'):
#                     file_type_list.append('AUDIO_iPad')
#                 elif a_m_f.endswith('.wav'):
#                     file_type_list.append('AUDIO_WEB')
#                 else:
#                     print('It seems that there are some UNKNOWN type of media files for: ', a_file_ID, ' insdie : ', extracted_data_dir)
#                     sys.stdout.flush()
#                     sys.exit(0)
#                     # time.sleep(100000000)
#         if m_f_exist == 0:
#             file_type_list.append(NO_EXIST_STR)
    
    
    
    
#     # if not os.path.exists(transcript_out_audio): 
    
#     if not os.path.exists(ASR_out_audio) or not os.path.exists(transcript_out_audio) or not os.path.exists(transcript_out_audio_mp3): 
        
        
#         L_files = 0
        
#         ## Only save the final transcription files for those who have all their questions 
        
#         ## CognoMemory: each dir should have 2 csv, 1 json and 14 media (audio/video) files: Total = 17
#         ## CognoMND: 19 media files + 3 others: Total = 22
#         ## CognoStroke: 4 media files + 3 others: Total = 7
        
#         if assessment_type == 'CognoSpeak Assessment' or assessment_type == 'CognoMemory Assessment':
#             L_files = 17
            
#         elif assessment_type == 'CognoMND Assessment' or assessment_type == 'CognoMND - Care partner task': 
#             L_files = 22
            
#         elif assessment_type == 'CognoStroke Short Assessment': 
#             L_files = 7
            
#         elif assessment_type == 'CognoStroke Long Assessment': 
#             L_files = 17
        
#         else:
#             print(' The assessment type is: ', assessment_type, ' for dir: ', a_file_ID)
#             print('Check this .... ')
#             sys.stdout.flush()
#             sys.exit(0)
#             # time.sleep(100000000)
            
#         if len(all_files) == L_files:
            
#             sox_cmd = 'sox '
            
#             sox_ASR_cmd = 'sox '
            
#             no_librosa = 0
            
            
#             output_audio_list = []
            
#             for i in range(len(all_files)):
                
#                 a_file = all_files[i]
                
#                 ## Convert the file 
#                 # output_audio_list, output_audio, no_librosa = convert_media_file(a_file, output_audio_list)
                
#                 if a_file.endswith('.webm') or a_file.endswith('.m4a') or a_file.endswith('.mov') or a_file.endswith('.wav'):
                    
#                     # print('The input video file: ', a_file)
#                     output_audio_list, output_audio, no_librosa = convert_media_file(a_file, output_audio_list, no_librosa)
                    
                    
#                     if i == 0:    
#                         sox_cmd += output_audio + ' ' 
#                         sox_ASR_cmd += output_audio + ' ' 
#                     else:
#                         sox_cmd += wht_ns_path + ' ' + output_audio + ' ' 
#                         sox_ASR_cmd += silence_path + ' ' + output_audio + ' ' 
                
                
#                 # print('')
#                 # print('i : ', i)
#                 # print('sox_cmd : ', sox_cmd)
#                 # print('')
#                 # sys.stdout.flush()
            
            
            
            
            
            
#             if not os.path.isdir(transcript_out_dir):
#                 os.mkdir(transcript_out_dir)
            
            
            
            
            
#             sox_cmd += transcript_out_audio
            
#             # print('\n\nsox_cmd : ', sox_cmd, '\n\n')
#             # sys.stdout.flush()
#             # time.sleep(2)
#             # time.sleep(100000000)
            
#             ## If SOX can't do the job, try librosa only if the file size isn't too large to read 
#             if os.system(sox_cmd) != 0:
#                 # print('sox_cmd : ', sox_cmd)
                
#                 if no_librosa == 1:
#                     print('\n***** This is unfortunate that SOX has failed and the files were too large to be read by librosa as well for : ', a_file_ID, ' *****\n' )
#                 else:
#                     print('SOX has failed, thus using librosa for ', a_file_ID, '\n')
                    
                    
#                     for output_audio in output_audio_list:
#                         audio_data, _ = librosa.load( output_audio, sr=SR)
                        
#                         if i == 0:
#                             to_transcrpt_audio.extend( list(audio_data) )
#                         else:
#                             to_transcrpt_audio.extend( gen_whiteNoise(0) + list(audio_data) )
#                         audio_data = []
                    
#                     sf.write(transcript_out_audio, to_transcrpt_audio, SR)
#                     to_transcrpt_audio = []
            
            
            
#             sox_ASR_cmd += ASR_out_audio
            
#             if os.system(sox_ASR_cmd) != 0:
#                 # print('sox_ASR_cmd : ', sox_ASR_cmd)
                
#                 if no_librosa == 1:
#                     print('\n***** This is unfortunate that SOX has failed and the files were too large to be read by librosa as well for : ', a_file_ID, ' *****\n' )
#                 else:
#                     print('SOX has failed, thus using librosa for ', a_file_ID, '\n')
                    
#                     for output_audio in output_audio_list:
#                         audio_data, _ = librosa.load( output_audio, sr=SR)
                        
#                         if i == 0:
#                             to_ASR_audio.extend( list(audio_data) )
#                         else:
#                             to_ASR_audio.extend( gen_silence(0) + list(audio_data) )
#                         audio_data = []
                    
#                     sf.write(ASR_out_audio, to_ASR_audio, SR)
#                     to_ASR_audio = []
            
            
            
#             ## Next, convert the wav file into mp3 ... 
            
#             audio_cnvrt_cmd = 'ffmpeg -loglevel quiet -i {} -vn -ab 128k -ar {} -y {}'.format(transcript_out_audio, SR, transcript_out_audio_mp3)
            
#             # if a_file_ID == 3479:
#             #     print('audio_cnvrt_cmd: ', audio_cnvrt_cmd)
#             #     sys.stdout.flush()
#             #     time.sleep(5)
                
#             # os.system(audio_cnvrt_cmd)
#             if os.system(audio_cnvrt_cmd) != 0:
#                 print('This command did not execute successfully: ', audio_cnvrt_cmd)
#                 sys.stdout.flush()
#                 sys.exit(0)
#                 # time.sleep(5)
            
#         else:
            
            
#             print('\n\n** There are only ', len(all_files), ' files for ', a_file_ID, ' ; No audio transcription using SOX will be applied to prepare the final audio for transcription.\n')
#             sys.stdout.flush()
            
            
            
#             for i in range(len(all_files)):
                
#                 a_file = all_files[i]
                
#                 ## Convert the file 
#                 # output_audio_list, output_audio, no_librosa = convert_media_file(a_file, output_audio_list)
                
#                 if a_file.endswith('.webm') or a_file.endswith('.m4a') or a_file.endswith('.mov') or a_file.endswith('.wav'):
                    
#                     output_audio_list, output_audio, no_librosa = convert_media_file(a_file, [], 0)
                    
            
#             if_N_complete = 1
            
#             # l_weird = a_file_ID.split('_')[1]
#             l_N_complete = a_file_ID
            
        
#         # print('Length of to_transcrpt_audio: ', len(to_transcrpt_audio))
#         # print('Length of to_ASR_audio: ', len(to_ASR_audio))
        
#         to_transcrpt_audio= []
#         to_ASR_audio = []
        
        
    
#     # else:
#     #     print(ASR_out_audio, ' and ', transcript_out_audio, ' already exists')
    
#     sys.stdout.flush()
    
#     return a_file_ID, file_type_list, if_N_complete, l_N_complete, assessment_ID, assessment_type, 'YES' if if_N_complete == 0 else 'NO'



def do_convert_video_audio(args):
    a_file_ID = args[0]

    # # log the start immediately (helps to see which task gets stuck)
    # print(f"[{datetime.now()}] PID {os.getpid()} starting {a_file_ID}", flush=True)

    if_N_complete = 0
    l_N_complete = ''

    all_files = natsorted(glob.glob(extracted_data_dir + a_file_ID + '/*'))

    if len(all_files) == 0:
        print('Skipping empty dir:', a_file_ID, flush=True)
        return a_file_ID, [NO_EXIST_STR] * (MAX_LEN_MEDIA_FILES - 1), 1, a_file_ID, '', '', 'NO'

    to_transcrpt_audio = []
    to_ASR_audio = []

    transcript_out_dir = final_transcript_dir + a_file_ID + '/'
    transcript_out_audio = transcript_out_dir + a_file_ID + '.wav'
    ASR_out_audio = transcript_out_dir + a_file_ID + '_ASR.wav'
    transcript_out_audio_mp3 = transcript_out_dir + a_file_ID + '.mp3'

    # Get the json file
    the_json = [x for x in all_files if x.endswith('.json')]
    if not the_json:
        print(f"No JSON found in {a_file_ID}", flush=True)
        return a_file_ID, [NO_EXIST_STR] * (MAX_LEN_MEDIA_FILES - 1), 1, a_file_ID, '', '', 'NO_JSON'
    the_json = the_json[0]

    with open(the_json, 'r') as f:
        dict_json = json.load(f)

    assessment_ID = dict_json['assessment']['taskInstanceIdentity']
    assessment_type = dict_json['assessment']['assessmentName']

    # Media files (exclude csv, json, and caregiver)
    all_media_files = [
        x for x in all_files
        if not x.endswith('.csv')
           and not x.endswith('.json')
           and 'caregiver' not in x.lower()
    ]

    if len(all_media_files) == 0:
        print('No media files in:', a_file_ID, flush=True)
        return a_file_ID, [NO_EXIST_STR] * (MAX_LEN_MEDIA_FILES - 1), 1, a_file_ID, assessment_ID, assessment_type, 'NO'

    # Build the list of file types for questions 1..MAX_LEN_MEDIA_FILES-1
    file_type_list = []
    for i in range(1, MAX_LEN_MEDIA_FILES):
        m_f_exist = 0
        for a_m_f in all_media_files:
            if f'_Q{i}.' in a_m_f:
                m_f_exist = 1
                if a_m_f.endswith('.webm'):
                    file_type_list.append('VIDEO_WEB')
                elif a_m_f.endswith('.mov'):
                    file_type_list.append('VIDEO_iPad')
                elif a_m_f.endswith('.m4a'):
                    file_type_list.append('AUDIO_iPad')
                elif a_m_f.endswith('.wav'):
                    file_type_list.append('AUDIO_WEB')
                else:
                    print(f'UNKNOWN media type in {a_file_ID}', flush=True)
                    return a_file_ID, [NO_EXIST_STR] * (MAX_LEN_MEDIA_FILES - 1), 1, a_file_ID, assessment_ID, assessment_type, 'UNKNOWN_TYPE'
        if m_f_exist == 0:
            file_type_list.append(NO_EXIST_STR)

    # Check if output audio already exists
    if os.path.exists(ASR_out_audio) and os.path.exists(transcript_out_audio) and os.path.exists(transcript_out_audio_mp3):
        # Already done
        return a_file_ID, file_type_list, 0, l_N_complete, assessment_ID, assessment_type, 'YES'

    # Determine required file count for completeness
    if assessment_type in ['CognoSpeak Assessment', 'CognoMemory Assessment']:
        L_files = 17
    elif assessment_type in ['CognoMND Assessment', 'CognoMND - Care partner task']:
        L_files = 22
    elif assessment_type == 'CognoStroke Short Assessment':
        L_files = 7
    elif assessment_type == 'CognoStroke Long Assessment':
        L_files = 17
    else:
        print(f'Unknown assessment type: {assessment_type} for {a_file_ID}', flush=True)
        return a_file_ID, file_type_list, 1, a_file_ID, assessment_ID, assessment_type, 'UNKNOWN_ASSESSMENT'

    if len(all_files) != L_files:
        # Incomplete – just convert individual files to wav, don't merge
        print(f"\n\n** Only {len(all_files)} files for {a_file_ID}; no SOX merging.\n", flush=True)
        output_audio_list = []
        no_librosa = 0
        for a_file in all_files:
            if a_file.endswith(('.webm', '.m4a', '.mov', '.wav')):
                output_audio_list, _, no_librosa = convert_media_file(a_file, [], no_librosa)
        return a_file_ID, file_type_list, 1, a_file_ID, assessment_ID, assessment_type, 'NO'

    # ---- Complete assessment: merge the media files ----
    sox_cmd = 'sox '
    sox_ASR_cmd = 'sox '
    no_librosa = 0
    output_audio_list = []

    for idx, a_file in enumerate(all_files):
        if a_file.endswith(('.webm', '.m4a', '.mov', '.wav')):
            output_audio_list, output_audio, no_librosa = convert_media_file(a_file, output_audio_list, no_librosa)
            if idx == 0:
                sox_cmd += output_audio + ' '
                sox_ASR_cmd += output_audio + ' '
            else:
                sox_cmd += wht_ns_path + ' ' + output_audio + ' '
                sox_ASR_cmd += silence_path + ' ' + output_audio + ' '

    if not os.path.isdir(transcript_out_dir):
        os.mkdir(transcript_out_dir)

    # ---- MERGE WITH SOX (with timeout) ----
    sox_cmd += transcript_out_audio
    try:
        subprocess.run(sox_cmd, shell=True, check=True, timeout=SUB_TIMEOUT)
    except subprocess.TimeoutExpired:
        print(f"SOX timed out for {a_file_ID}", flush=True)
        return a_file_ID, file_type_list, 1, a_file_ID, assessment_ID, assessment_type, 'ERROR_SOX_TIMEOUT'
    except subprocess.CalledProcessError:
        # Fallback to librosa if file size allows
        print(f"SOX failed for {a_file_ID}, trying librosa fallback", flush=True)
        if no_librosa == 1:
            print(f"File too large for librosa in {a_file_ID}", flush=True)
            return a_file_ID, file_type_list, 1, a_file_ID, assessment_ID, assessment_type, 'ERROR_SOX_AND_NO_LIBROSA'
        try:
            for out_audio in output_audio_list:
                audio_data, _ = librosa.load(out_audio, sr=SR)
                if out_audio == output_audio_list[0]:
                    to_transcrpt_audio.extend(list(audio_data))
                else:
                    to_transcrpt_audio.extend(gen_whiteNoise(0) + list(audio_data))
            sf.write(transcript_out_audio, to_transcrpt_audio, SR)
        except Exception as e:
            print(f"Librosa fallback also failed for {a_file_ID}: {e}", flush=True)
            return a_file_ID, file_type_list, 1, a_file_ID, assessment_ID, assessment_type, 'ERROR_SOX_AND_LIBROSA_FAILED'

    # ---- MERGE FOR ASR (with timeout) ----
    sox_ASR_cmd += ASR_out_audio
    try:
        subprocess.run(sox_ASR_cmd, shell=True, check=True, timeout=SUB_TIMEOUT)
    except subprocess.TimeoutExpired:
        print(f"SOX (ASR) timed out for {a_file_ID}", flush=True)
        return a_file_ID, file_type_list, 1, a_file_ID, assessment_ID, assessment_type, 'ERROR_SOX_TIMEOUT'
    except subprocess.CalledProcessError:
        print(f"SOX (ASR) failed for {a_file_ID}, trying librosa fallback", flush=True)
        if no_librosa == 1:
            print(f"File too large for librosa (ASR) in {a_file_ID}", flush=True)
            return a_file_ID, file_type_list, 1, a_file_ID, assessment_ID, assessment_type, 'ERROR_SOX_AND_NO_LIBROSA'
        try:
            for out_audio in output_audio_list:
                audio_data, _ = librosa.load(out_audio, sr=SR)
                if out_audio == output_audio_list[0]:
                    to_ASR_audio.extend(list(audio_data))
                else:
                    to_ASR_audio.extend(gen_silence(0) + list(audio_data))
            sf.write(ASR_out_audio, to_ASR_audio, SR)
        except Exception as e:
            print(f"Librosa fallback (ASR) failed for {a_file_ID}: {e}", flush=True)
            return a_file_ID, file_type_list, 1, a_file_ID, assessment_ID, assessment_type, 'ERROR_SOX_AND_LIBROSA_FAILED'

    # ---- CONVERT TO MP3 (with timeout) ----
    audio_cnvrt_cmd = f'ffmpeg -loglevel quiet -i {transcript_out_audio} -vn -ab 128k -ar {SR} -y {transcript_out_audio_mp3}'
    try:
        subprocess.run(audio_cnvrt_cmd, shell=True, check=True, timeout=SUB_TIMEOUT)
    except subprocess.TimeoutExpired:
        print(f"FFmpeg timed out for {a_file_ID}", flush=True)
        return a_file_ID, file_type_list, 1, a_file_ID, assessment_ID, assessment_type, 'ERROR_FFMPEG_TIMEOUT'
    except subprocess.CalledProcessError:
        print(f"FFmpeg failed for {a_file_ID}", flush=True)
        # Don't exit – just return an error status
        return a_file_ID, file_type_list, 1, a_file_ID, assessment_ID, assessment_type, 'ERROR_FFMPEG'

    # If we get here, everything succeeded
    return a_file_ID, file_type_list, 0, l_N_complete, assessment_ID, assessment_type, 'YES'



def save_df_csv_rIDs(list_IDs, out_csv, idx):
    # for Andrew
    if idx == 0: 
        df = pd.DataFrame(list_IDs, columns=['Research_IDs'])
    # for Fuxiang 
    else:
        data = {'Research_IDs': list_IDs,
            'Comments': ['']*len(list_IDs)}
        df = pd.DataFrame(data)
    
    df.to_csv(out_csv, index=False)







if __name__=='__main__' and '__file__' in globals():

    
    if len(sys.argv) < 2:
        print('\n\nPlease use : python CognoSpeak_2_data_process.py 15 [where 15 is the number of CPU]\n\n')
        sys.exit()
    
    # startTime = datetime.now()
    # current_time = startTime.strftime("%Y/%m/%d at %H:%M:%S")
    # print('\n\nThe script starting at: ' + str(current_time), ' \n\n' )
    
    N_jobs = int(sys.argv[1])
    
    if N_jobs >= cpu_count():
        print('The max no of CPU available : ', cpu_count())
        sys.exit("Lower the number of CPU\n\n")
    
    
    ct = datetime.now()
    
    
    # Maximum time (seconds) an external command is allowed to run.
    SUB_TIMEOUT = 60   # 5 minutes – adjust if your files are larger
    
    
    '''
    Step 1: Download the ZIP files from the server. This is done on a seperate script. 
    '''
    
    
    
    '''
    Step 2: Extract the ZIP files which are not the known test cases .... 
    '''
    
    zip_files_list = glob.glob(raw_data_dir+"*.zip")
    
    zip_file_ID_list, zip_r_ID_list = do_get_ZIP_4M_logs(zip_files_list)
    
    ## As, I have changed the __ to _, I need to make changes to the names as well 
    zip_file_ID_list = [i.replace('__', '_') for i in zip_file_ID_list]
    
    check_list_len(zip_r_ID_list, zip_file_ID_list)
    check_list_len(zip_files_list, zip_r_ID_list)
    
    print('The number of IDs on the ZIP files : ', len(zip_r_ID_list))
    print('The number of unique IDs on the ZIP files : ', len(list(set(zip_r_ID_list))))
    
    
    
    
    ####### Manually add the TEST IDs here .... 
    ###########################################################################
    test_list_IDs = []
    test_list_firstN = []
    test_list_lastN = []
    test_list_practitionerEmail = []
    test_comments = []
    
    ## I got the following IDs from Fuxiang on 15/04/2024 as test IDs: 
    test_IDs_4M_Fuxiang = ['78826', '53078', '39999', '09737', '77619', '74433', '24524', '38614', '17841', '49164', '31868', '63126', '78179', '34977', '85668', '86793', '31413', '16005', '22454', '93730', '79490', '65795', '05705', '20093', '01328', '31096', '22808', '76549', '93987', '96962', '50186', '59774', '61464', '98063', '32352', '22051', '53385', '90059', '28585', '02367', '85603', '30447', '86691', '77902', '35032', '84971', '70976', '21613', '49515', '61754', '46671', '40881', '93711', '96932', '07421', '62309', '74727', '07404', '33382', '23793', '31745', '57857', '70883', '10108', '17083', '84776', '19433', '05160', '18301', '30205', '12750', '15241', '62166', '00409', '83822', '11006']
    
    ## These are the IDs I got from Fuxiang as the spreadsheet is still populating the IDs even after they are marked as test cases by Fuxiang (updated on 18/07/2024)
    
    test_IDs_4M_Fuxiang.extend(['05245', '08683', '11561', '13899', '17491', '18345', '25957', '27313', '29300', '34420', '39197', '46088', '52382', '67148', '68003', '68762', '70146', '70605', '74987', '76329', '79524', '83513', '87723', '88666', '91674', '93551', '95787', '95859', '96703', '98645', '05126', '27390', '49060', '55053', '10234', '35591', '24970', '11006', '51410', '82817', '35591', '83822', '77370', '43172', '90239', '98007', '32729', '70729', '43817', '23500', '18346', '58978', '18301', '51410', '35729', '81526', '01233', '57378', '27259', '61270', '95743', '72100', '63314', '03019', '27818', '83626', '42856', '07655', '63314', '93673', '52240', '46710', '71981', '45262', '44117', '97349', '30389', '16059', '25871', '29828', '99608', '45889', '34237'])
    
    ## These are the ones which I found as test cases 
    test_IDs_4M_Fuxiang.extend(['41861', '80706', '50150'])
    
    ## These are the ones which I got from Caitlin 
    test_IDs_4M_Fuxiang.extend(['31868', '93970', '71491'])
    
    ## This one I got as another test case after a long email conversation with Caitlin 
    test_IDs_4M_Fuxiang.extend(['91053'])
    
    ## This is the one which has been created by someone in Edinburgh 
    test_IDs_4M_Fuxiang.extend(['71981'])
    
    ## This ID wants their assessments to be removed, as informed by Dora on 21/02/2025. I have added it as an test ID to exclude it from the experiments 
    test_IDs_4M_Fuxiang.extend(['01867'])
    
    ## Another test 
    test_IDs_4M_Fuxiang.extend(['46420'])
    
    ## test IDs from Dora and Leslie
    test_IDs_4M_Fuxiang.extend(['58469', '99214'])
    
    ## test IDs for Rithika, who was testing the system ... 
    test_IDs_4M_Fuxiang.extend(['69744', '89146'])
    
    ## these are IDs for Rithika, while the video can't be uploaded and seen on the portal 
    test_IDs_4M_Fuxiang.extend(['22496', '90693', '98974', '00321'])
    
    ## These IDs I found upon checking ... 
    test_IDs_4M_Fuxiang.extend(['12345'])
    
    ## These IDs Sara mentioned as having some issues ... 
    test_IDs_4M_Fuxiang.extend(['64411'])
    
    ## These IDs I have found not worth having in the experiemnts after checking the audio 
    test_IDs_4M_Fuxiang.extend(['08631', '21747', '22909', '56344', '64411'])
    
    
    
    test_IDs_4M_Fuxiang = natsorted(set(test_IDs_4M_Fuxiang))
    
    test_list_IDs.extend( [int(i) for i in test_IDs_4M_Fuxiang] )
    test_list_firstN.extend( ['']*len(test_list_IDs) )
    test_list_lastN.extend( ['']*len(test_list_IDs) )
    test_list_practitionerEmail.extend( ['']*len(test_list_IDs) )
    test_comments.extend( ['manually added']*len(test_list_IDs) )
    
    
    # int_test_list_IDs = [int(i) for i in test_IDs_4M_Fuxiang]
    
    # print('The number of test cases added manually : ', len(int_test_IDs_4M_Fuxiang))
    
    
    # print('test cases which appear among zip files ... ', natsorted(intersection(zip_r_ID_list, int_test_IDs_4M_Fuxiang )) )
    # print('test cases which do not appear among zip files ... ', natsorted(diff_list(int_test_IDs_4M_Fuxiang, zip_r_ID_list)) )
    
    print('The number of manually added test cases : ', len(test_list_IDs))
    
    ###########################################################################
    
    
    
    ## I will not extract ZIP files for manually added test cases 
    
    to_extract_zip_files_list = []
    to_extract_zip_file_ID_list = []
    to_extract_zip_r_ID_list = []
    
    for i in range(len(zip_file_ID_list)):
        if not zip_r_ID_list[i] in test_list_IDs:
            to_extract_zip_files_list.append( zip_files_list[i] )
            to_extract_zip_file_ID_list.append(zip_file_ID_list[i])
            to_extract_zip_r_ID_list.append( zip_r_ID_list [i] )
    
    
    
    print('The number of IDs on the ZIP files to be extracted : ', len(to_extract_zip_r_ID_list))
    print('The number of unique IDs on the ZIP files to be extracted : ', len(list(set(to_extract_zip_r_ID_list))))
    
    
    
    inputs = zip(to_extract_zip_files_list)
    
    n_jobs = min(N_jobs, len(to_extract_zip_files_list))
    print('n_jobs: ', n_jobs)
    sys.stdout.flush()
    
    c_ZIP = 0
    results = tqdm(Pool(n_jobs).imap_unordered(do_extract_ZIPs, inputs), total=len(to_extract_zip_files_list))
    for result in results:
        if result == 1:
            c_ZIP += 1
    
    print('\nTotal number of IDs extracted: ', c_ZIP)
    print('\n\n***** STEP 2 (ZIP EXTRACTION) IS COMPLETE *****\n')
    
    
    # print('I am done, waiting to be  cancelled ....... ')
    # sys.stdout.flush()
    # time.sleep(100000000)
    
    
    
    sys.stdout.flush()
    time.sleep(1)
    # time.sleep(100000000)
    
    
    
    
    
    
    '''
    Extra step: this is done because some IDs were duplicated for participants 
    The ZIP files were renamed in CognoSpeak_1, here I need to rename the extracted files ... 
    '''
    
    
    dirs_inside = glob.glob(extracted_data_dir+'*_99*99_*')
    
    for a_dir in dirs_inside:
        
        dir_to_consider = a_dir.split('/')[-1]
        ori_id = dir_to_consider.split('_')[1][2:7]
        rplc_id = dir_to_consider.split('_')[1]
        
        rename_files_inside(dir_to_consider, '_'+ori_id+'_', '_'+rplc_id+'_')
    
    
    
    
    
    '''
    Extra step: check the IDs with practitioner email address including therapy-box
    '''
    print('Getting all the json files .... ')
    sys.stdout.flush()
    all_jsons = natsorted(glob.glob(extracted_data_dir + '*/*.json'))
    print('Getting all the json files is COMPLETE.\n\n')
    sys.stdout.flush()
    
    
    print('Searching for the test cases among the json files ...')
    sys.stdout.flush()
    auto_check_test_IDs = []
    
    # # This is a case where external ID appears as from therapy-box ... 
    # for i in all_jsons:
    #     if '_48152_' in i:
    #         print(i)
    
    
    
    #############################################
    ## This is using SINGLE CPU ... 
    for a_json in tqdm(all_jsons):
        with open(a_json, 'r') as f:
            dict_json = json.load(f)
        
        
        
        
        if 'therapy-box' in dict_json['patient']['profile']['email'] or 'vishalsablec6@gmail.com' in dict_json['patient']['profile']['email'] or 'n.pevy@sheffield.ac.uk' in dict_json['patient']['profile']['email']:
            # print(a_json)
            # print('ID: ', dict_json['patient']['profile']['researchNumber'])
            # print('FirstName : ', dict_json['patient']['profile']['firstName'])
            # print('LastName: ', dict_json['patient']['profile']['lastName'])
            # print('practitionerEmail : ', dict_json['patient']['practitionerEmail'])
            
            
            
            # test_list_IDs.append( a_json.split('/')[-1].split('_')[1] )
            test_list_IDs.append( int(a_json.split('/')[-1].split('_')[1]) )
            test_list_firstN.append( dict_json['patient']['profile']['firstName'] )
            test_list_lastN.append( dict_json['patient']['profile']['lastName'] )
            test_list_practitionerEmail.append( dict_json['patient']['practitionerEmail'] )
            test_comments.append( 'test practitioner email is detected' )
            
            auto_check_test_IDs.append( int(a_json.split('/')[-1].split('_')[1]) )
        
        
        
        if 'therapy-box' in dict_json['patient']['practitionerEmail'] or 'vishalsablec6@gmail.com' in dict_json['patient']['practitionerEmail'] or 'n.pevy@sheffield.ac.uk' in dict_json['patient']['practitionerEmail']:
            # print(a_json)
            # print('ID: ', dict_json['patient']['profile']['researchNumber'])
            # print('FirstName : ', dict_json['patient']['profile']['firstName'])
            # print('LastName: ', dict_json['patient']['profile']['lastName'])
            # print('practitionerEmail : ', dict_json['patient']['practitionerEmail'])
            
            
            
            # test_list_IDs.append( a_json.split('/')[-1].split('_')[1] )
            test_list_IDs.append( int(a_json.split('/')[-1].split('_')[1]) )
            test_list_firstN.append( dict_json['patient']['profile']['firstName'] )
            test_list_lastN.append( dict_json['patient']['profile']['lastName'] )
            test_list_practitionerEmail.append( dict_json['patient']['practitionerEmail'] )
            test_comments.append( 'test practitioner email is detected' )
            
            auto_check_test_IDs.append( int(a_json.split('/')[-1].split('_')[1]) )
            
            
            
        if 'test' in dict_json['patient']['profile']['firstName'].lower() or 'vishal' in dict_json['patient']['profile']['firstName'].lower() or 'test' in dict_json['patient']['profile']['lastName'].lower() or 'sable' in dict_json['patient']['profile']['lastName'].lower():
            # print(a_json)
            # print('ID: ', dict_json['patient']['profile']['researchNumber'])
            # print('FirstName : ', dict_json['patient']['profile']['firstName'])
            # print('LastName: ', dict_json['patient']['profile']['lastName'])
            # print('practitionerEmail : ', dict_json['patient']['practitionerEmail'])
            
            
            
            # test_list_IDs.append( a_json.split('/')[-1].split('_')[1] )
            test_list_IDs.append( int(a_json.split('/')[-1].split('_')[1]) )
            test_list_firstN.append( dict_json['patient']['profile']['firstName'] )
            test_list_lastN.append( dict_json['patient']['profile']['lastName'] )
            test_list_practitionerEmail.append( dict_json['patient']['practitionerEmail'] )
            test_comments.append( 'test appears in first or last name' )
            
            
            
            auto_check_test_IDs.append( int(a_json.split('/')[-1].split('_')[1]) )
        
        
    #############################################
    
    
    
    
    
    
    
    auto_check_test_IDs = natsorted(set(auto_check_test_IDs))
    print('IDs found as test using json file reading: ', len(auto_check_test_IDs))
    # test_list_IDs.extend( auto_check_test_IDs )
    print('Total Length of test IDs : ', len(set(test_list_IDs)))
    
    sys.stdout.flush()
    # time.sleep(100000000)
    
    
    
    
    test_data = {'research_IDs': make_5_chars(test_list_IDs),
        'First_Names': test_list_firstN,
        'LastNames':test_list_lastN,
        'practitionerEmail': test_list_practitionerEmail,
        'comments': test_comments}
    
    # Create DataFrame
    df_test = pd.DataFrame(test_data)
    
    df_test = df_test.drop_duplicates(subset=["research_IDs"])
    
    # df_test['research_IDs'] = df_test['research_IDs'].astype('object')
    
    df_test.to_csv(test_ID_out_csv, index=False)
    # df_test.to_csv(test_ID_out_csv, index=False, quoting=csv.QUOTE_NONNUMERIC)
    # df_test.to_csv(test_ID_out_csv, index=False, quoting=1)
    
    time.sleep(5)
    
    final_test_list_IDs = natsorted(df_test['research_IDs'])
    
    
    
    
    
    
    
    
    
    
    '''
    Step 3: Get audio files from those extracted ZIP files  
    '''
    
    
    ## Check if the white noise exists .... 
    if not os.path.exists(wht_ns_path):
        print('The white noise was not there, it has been generated at: ', wht_ns_path)
        sys.stdout.flush()
        gen_whiteNoise(1)
    
    
    ## Check if the silence exists .... 
    if not os.path.exists(silence_path):
        print('The silence was not there, it has been generated at: ', silence_path)
        sys.stdout.flush()
        gen_silence(1)
    
    
    
    ## This one I used for test ... 
    # final_file_ID_list = ['R_13135__230706_203755']
    ## This one to try with all the audio files ... 
    # final_file_ID_list = ['R_79479__230523_230529']
    
    
    ## Next, remove the test cases from the ZIP files which are to be converted .... 
    
    to_convert_zip_file_ID_list = []
    
    for i in to_extract_zip_file_ID_list:
    # for i in [i.replace('__', '_') for i in to_extract_zip_file_ID_list]:
        to_remove = 0
        for j in final_test_list_IDs:
            
            if '_'+make_N_chars_a_val(j, 5)+'_' in i:
            
                to_remove = 1
        
        if to_remove == 0:
            to_convert_zip_file_ID_list.append( i )
    
    
    
    
    
    
    
    # c_incomplete_pats = 0
    list_incomplete_file_IDs = []
    # no_SOX_IDs = []
    
    
    # final_file_ID_list = []
    '''
    'S_23555__240125_175547' has a large audio which can't be loaded using librosa ... 
    I am excluding it for now .... 
    I have used sox to get those large files fixed 
    '''
    
    # final_file_ID_list.remove( 'S_23555__240125_175547' )
    
    # final_file_ID_list = ['S_23555__240125_175547']
    
    # ## This is testing the media inforamtion for those dirs which have no media file ... 
    # to_convert_zip_file_ID_list = to_convert_zip_file_ID_list[0:5] 
    # to_convert_zip_file_ID_list = to_convert_zip_file_ID_list[0:2] + ['R_02166_240807_202127', 'R_01776_240617_094812', 'R_02166_240808_161315']
    
    ## This is testing extracting missing audio files as well 
    ## All files: R_00013_230802_123716
    ## No media file: R_01688_240604_105548
    ## Q14 is missing: R_04392_240723_155717
    # to_convert_zip_file_ID_list = ['R_00013_230802_123716', 'R_01688_240604_105548', 'R_04392_240723_155717']
    # to_convert_zip_file_ID_list = ['R_00013_230802_123716']
    
    
    # to_convert_zip_file_ID_list = ['MND_R_00762_230327_173615']
    
    # to_convert_zip_file_ID_list = ['MND_R_10137_250509_122523']
    
    #############################################
    ## This is using multiple CPU ... 
    
    # inputs = zip(natsorted(to_convert_zip_file_ID_list))
    
    # n_jobs = min(N_jobs, len(to_convert_zip_file_ID_list))
    # print('n_jobs: ', n_jobs)
    # sys.stdout.flush()
    
    
    # # n_jobs = 1
    
    # df_file_type_info = pd.DataFrame([], columns=['dir_name']+['Q'+str(i)+'_type' for i in range(1, MAX_LEN_MEDIA_FILES)]+['assessment_ID'] + ['assessment_type'] +['if_COMPLETE'])
    
    # results = tqdm(Pool(n_jobs).imap_unordered(do_convert_video_audio, inputs), total=len(to_convert_zip_file_ID_list))
    
    # for result in results:
        
    #     # if len(result) != len(df_file_type_info.columns): 
            
    #     #     print(len(result))
    #     #     print(len(df_file_type_info.columns))
            
    #     #     print('result : ')
    #     #     print(result)
    #     #     sys.stdout.flush()
    #     #     sys.exit(0)
    #     #     # time.sleep(100000000)
        
    #     row = [result[0]] + result[1] + [result[4]] + [result[5]] + [result[6]]

    #     if len(row) != len(df_file_type_info.columns):
    #         print("Mismatch detected!")
    #         print("len(row):", len(row))
    #         print("expected:", len(df_file_type_info.columns))
    #         print("file_type_list len:", len(result[1]))
    #         print("dir:", result[0])
    #         print('result : ')
    #         print(result)
            
    #         sys.exit(0)
        
        
        
    #     df_file_type_info.loc[len(df_file_type_info.index)] = [result[0]] + result[1] + [result[4]] + [result[5]] + [result[6]]
        
    #     if result[2] == 1:
    #         list_incomplete_file_IDs.append(result[3])
    
    
    
    inputs = list(zip(natsorted(to_convert_zip_file_ID_list)))  # make a list for len()
    n_jobs = min(N_jobs, len(inputs))
    print('n_jobs: ', n_jobs)
    sys.stdout.flush()
    
    columns = ['dir_name'] + [f'Q{i}_type' for i in range(1, MAX_LEN_MEDIA_FILES)] + ['assessment_ID', 'assessment_type', 'if_COMPLETE']
    df_file_type_info = pd.DataFrame(columns=columns)
    
    # Use maxtasksperchild=1 so any process that hangs gets replaced
    with Pool(n_jobs, maxtasksperchild=1) as pool:
        # results = tqdm(pool.imap_unordered(do_convert_video_audio, inputs), total=len(inputs))
        
        results = tqdm(pool.imap_unordered(do_convert_video_audio, inputs),
               total=len(inputs),
               mininterval=2,   # update the bar only every 2 seconds
               miniters=1)
        
        for result in results:
            # result is a tuple: (a_file_ID, file_type_list, if_N_complete, l_N_complete, assessment_ID, assessment_type, status)
            # We expect exactly 7 items.
            if len(result) != 7:
                print(f"Worker returned unexpected length {len(result)}: {result}", flush=True)
                continue
    
            a_file_ID, file_type_list, if_N_complete, l_N_complete, assessment_ID, assessment_type, status = result
    
            # Build the row for the DataFrame
            row = [a_file_ID] + file_type_list + [assessment_ID, assessment_type, status]
    
            if len(row) != len(columns):
                print(f"Row length mismatch for {a_file_ID}: got {len(row)}, expected {len(columns)}", flush=True)
                continue
    
            df_file_type_info.loc[len(df_file_type_info)] = row
    
            if if_N_complete == 1:
                list_incomplete_file_IDs.append(l_N_complete)
    
    
    
    
    
    #############################################
    
    # print('df_file_type_info')
    # print(df_file_type_info)
    
    
    
    
    
    
    
    
    
    #############################################
    # 04/12/2025: I need to sort out the MND_extension.. 
    # Remove all those with extension 'MND_' if their type is CognoSpeak/CognoMemory ... 
    #############################################
    
    df_file_type_info = df_file_type_info.reset_index(drop=True)
    
    if_Brk = 0
    for ind in df_file_type_info.index:
        
        if df_file_type_info['assessment_type'][ind] == 'CognoSpeak Assessment' or df_file_type_info['assessment_type'][ind] == 'CognoMemory Assessment':
            
            if ('MND_' in df_file_type_info['dir_name'][ind] or 'STROKE_' in df_file_type_info['dir_name'][ind]) and df_file_type_info['if_COMPLETE'][ind] == 'YES':
                print(df_file_type_info['dir_name'][ind])
                if_Brk = 1
                
                # a_DIr = df_file_type_info['dir_name'][ind]
                
                
                # a_fL in glob.glob(extracted_data_dir + a_DIr + '/')
                
                # mv_cmd = 'mv {} {}'.format( extracted_data_dir + a_DIr + '/' , extracted_data_dir + a_DIr.replace(a_DIr.split('_')[0] + '_', '') + '/' )
                
                
                # mv_cmd = 'mv {} {}'.format( final_extract_dir + a_DIr + '/' , final_extract_dir + a_DIr.replace(a_DIr.split('_')[0] + '_', '') + '/' )
                
    
    
    if if_Brk == 1:
        print('The following have MND_ or STROKE_ at the beginning but from CognoSpeak/Memory ... ')
        print('Just ignore them by adding them "to_ignore_assessments" in config.py ')
        
        print('For one dir, add both. Like for MND_R_74765_231116_225719, add: MND_R_74765__231116_225719, R_74765__231116_225719 in "to_ignore_assessments"')
        print('DO not forget to add __, in stead of _')
        sys.stdout.flush()
        sys.exit(0)
        # time.sleep(100000000)
    
    
    
    
    
    #############################################
    
    
    
    
    
    
    
    
    
    df_file_type_info['assoc_rIDs'] = [int(x.split('_')[2]) if x.startswith('STROKE') or x.startswith('MND') else int(x.split('_')[1]) for x in df_file_type_info.dir_name]
    
    df_file_type_info.sort_values(['dir_name']).to_csv( dir_media_info_out, index=False )
    
    # df_file_type_info.to_csv( dir_media_info_out, index=False )
    print('The media file information has been saved at: ', dir_media_info_out)
    
    
    
    df_file_type_info = pd.read_csv( dir_media_info_out )
    
    
    
    print('\n\n***** STEP 3 (AUDIO CONVERSION) IS COMPLETE *****\n')
    sys.stdout.flush()
    time.sleep(1)
    
    # print('I am done, waiting to be  cancelled ....... ')
    
    # sys.stdout.flush()
    # # time.sleep(1)
    # time.sleep(100000000)
    
    
    
    
    '''
    Step 4: Get the list of file_IDs which are finally converted to audio. They are the ones I need to consider as those non-converted ones are empty. 
    '''
    
    
    # df_missing_assess = df_JSON[df_JSON.assessment_ID.isin(diff_list( list(df_JSON[df_JSON.N_results >= 5].assessment_ID), list(df_file_type_info[df_file_type_info.if_COMPLETE == 'YES'].assessment_ID)  ))]
    
    # df_missing_assess = df_missing_assess[df_missing_assess.research_ID.isin( diff_list( list(df_missing_assess.research_ID), [int(x) for x in final_test_list_IDs] ) )]
    
    
    
    
    ## Drop all those less thn 5 results 
    df_missing_assess = df_JSON[df_JSON.N_results >=7]
    
    
    # df_missing_assess = df_missing_assess[ ~ df_missing_assess.assessment_ID.isin( df_file_type_info[df_file_type_info.if_COMPLETE == 'YES'].assessment_ID ) ]
    
    df_missing_assess = df_missing_assess[ ~ df_missing_assess.assessment_ID.isin( df_file_type_info.assessment_ID ) ]
    
    # df_missing_assess = df_missing_assess[ ~ df_missing_assess.assessment_ID.isin( to_ignore_assessments ) ]
    
    
    
    
    
    for an_assess_type in list(set(df_missing_assess.assessment_type)):
        
        if an_assess_type == 'cognospeak-assessment' or an_assess_type == 'cognostroke-long-assessment':
            
            df_missing_assess_1 = df_missing_assess[ (df_missing_assess.N_results >=17) & (df_missing_assess.assessment_type == an_assess_type)]
        
        elif an_assess_type == 'cognomnd-assessment':
            
            df_missing_assess_2 = df_missing_assess[ (df_missing_assess.N_results >=21) & (df_missing_assess.assessment_type == an_assess_type)]
        
        elif an_assess_type == 'cognostroke-short-assessment':
            
            df_missing_assess_3 = df_missing_assess[ (df_missing_assess.N_results >=9) & (df_missing_assess.assessment_type == an_assess_type)]
        
        elif an_assess_type == NO_EXIST_STR:
            
            df_missing_assess_4 = df_missing_assess[ df_missing_assess.assessment_type == an_assess_type]
            
        else:
            
            print('There is new assessment type. Check this ... ', an_assess_type)
            
            sys.stdout.flush()
            sys.exit(0)
            # time.sleep(100000000)
    
    
    
    
    df_missing_assess = pd.concat([df_missing_assess_1, df_missing_assess_2, df_missing_assess_3, df_missing_assess_4], ignore_index=True, sort=False)
    
    df_missing_assess = df_missing_assess[df_missing_assess.research_ID.isin( diff_list( list(df_missing_assess.research_ID), [int(x) for x in final_test_list_IDs] ) )]
    
    df_missing_assess = df_missing_assess[~df_missing_assess.research_ID.isin( [int(x.split('_')[2]) if x.startswith('STROKE') or x.startswith('MND') else int(x.split('_')[1]) for x in to_ignore_assessments] ) ]
    
    
    ## Exclude the test IDs ... 
    df_test = pd.read_csv(test_ID_out_csv)
    df_missing_assess = df_missing_assess[~df_missing_assess.research_ID.isin(df_test.research_IDs)]
    
    
    df_missing_assess = df_missing_assess.sort_values(by=["diagnosis", "N_results"], ascending=False)
    
    
    
    df_missing_assess.to_csv( out_missing_assess, index = False )
    
    
    
    
    
    
    # df_file_type_info = pd.read_csv( '../data/CognoSpeak_2__dir_media_info.csv' )
    # df_missing_assess = pd.read_csv( '../data/CognoSpeak_2__assess_missing.csv' )
    
    
    
    print('The list of missing assessments has been saved at: ', out_missing_assess)
    
    
    
    executionTime = (datetime.now() - startTime)
    current_time = datetime.now().strftime("%Y/%m/%d at %H:%M:%S")
    print('\n\nThe script completed at: ' + str(current_time))
    print('Execution time: ' + str(executionTime), ' \n\n')

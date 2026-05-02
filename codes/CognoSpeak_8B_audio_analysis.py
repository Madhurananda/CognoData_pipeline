#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jul 24 22:12:12 2025

@author: madhupahar
"""


'''
This script checks the voice activities and SNR in the audio ... 
The VAD is downloaded from: 
    https://github.com/snakers4/silero-vad
'''


import warnings
warnings.filterwarnings('ignore')



# import whisper
# import torch

import librosa

# from jiwer import wer



from main import *
from config import *


import platform
if platform.system() == 'Darwin':
    from multiprocess.pool import ThreadPool, Pool
else:
    from multiprocessing.pool import ThreadPool, Pool

import jiwer

from silero_vad import load_silero_vad, read_audio, get_speech_timestamps

from torch import tensor
from torchmetrics.audio import SignalNoiseRatio


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




def make_2_list_same_len( a, b):
    
    
    
    if len(a) > len(b):
        
        # long_list = a
        # short_list = b
        
        b.extend( [np.mean(b)]*(len(a)-len(b)) )
        
        
    else:
        
        a.extend( [np.mean(a)]*(len(b)-len(a)) )
        
        # long_list = b
        # short_list = a
    
    ## Get ythe mean of the shorter list 
    
    # m_l = np.mean(short_list)
    
    # short_list.extend( [m_l]*(len(long_list)-len(short_list)) )
    
    return a, b



def do_calc_Auduio_analysis(args):
    
    a_dir = args[0]
    
    audio_files = glob.glob( final_extract_dir+ a_dir + '/*.wav')
    
    # print('audio files: ')
    # print(audio_files)
    
    # # # print('ori_txt_files: ')
    # # # print(ori_txt_files)
    # sys.stdout.flush()
    # time.sleep(100000000)
    
    # I have to use 
    
    # signaltonoise_dB(a, axis=0, ddof=0)
    
    
    
    df_temp_Audio = pd.DataFrame([], columns=OUT__audio_COL_NAMES)
    
    for audio_file in audio_files:
        
        
        
        
        # print('audio file: ')
        # print(audio_file)
        
        
        wav = read_audio(audio_file)
        
        # speech_timestamps = get_speech_timestamps(
        #   wav,
        #   VAD_model,
        #   return_seconds=True,  # Return speech timestamps in seconds (default is samples)
        # )
        
        speech_timestamps_samples = get_speech_timestamps(
          wav,
          VAD_model,
          return_seconds=False,  # Return speech samples
        )
        
        
        
        Y, SR = librosa.load(audio_file, sr=VAD_sr)
        
        ## Normalise 
        Y = normalise_sig(Y)
        
        
        
        # print(type(wav))
        
        # print( len(wav.tolist()) )
        
        # print(speech_timestamps_samples)
        
        
        # print('max Y:', max(abs(Y)))
        # print('min Y:', min(abs(Y)))
        
        
        
        # sys.stdout.flush()
        # time.sleep(100000000)
        
        
        
        
        
        list_starts = []
        list_ends = []
        
        audio_speech = []
        audio_pause = []
        
        data = []
        
        if len(speech_timestamps_samples) > 0:
            
            for i in range(len(speech_timestamps_samples)):
                
                Start_T = speech_timestamps_samples[i]['start']/VAD_sr
                End_T = speech_timestamps_samples[i]['end']/VAD_sr
                
                list_starts.append( Start_T )
                list_ends.append( End_T )
                
                audio_speech.extend( Y[speech_timestamps_samples[i]['start'] : speech_timestamps_samples[i]['end'] ] )
                
                if i == 0:
                    audio_pause.extend( Y[ 0 : speech_timestamps_samples[i]['start'] ] )
                else:
                    audio_pause.extend( Y[ speech_timestamps_samples[i-1]['end'] : speech_timestamps_samples[i]['start'] ] )
                
                if i == len(speech_timestamps_samples)-1:
                    audio_pause.extend( Y[speech_timestamps_samples[i]['end'] : ] )
                
                
                
            data.append([a_dir]*len(list_starts))
            
            data.append([audio_file.split('/')[-1].split('.wav')[0].split('_')[-1]]*len(list_starts))
            
            data.append(['VAD_OUT']*len(list_starts))
            
            data.append(list_starts)
            
            data.append(list_ends)
            
            data.append([round(len(audio_speech)/VAD_sr, 2)]*len(list_starts))
            
            data.append([round(len(audio_pause)/VAD_sr, 2)]*len(list_starts))
            
            data.append([round(len(Y)/VAD_sr, 2)]*len(list_starts))
            
            
            target, preds = make_2_list_same_len( audio_pause, audio_speech)
            snr = SignalNoiseRatio()
            SNR = snr( tensor(preds), tensor(target)).tolist()
            
            data.append([ round(SNR, 2) ]*len(list_starts))
            
        else:
            
            data.append([a_dir])
            
            data.append([audio_file.split('/')[-1].split('.wav')[0].split('_')[-1]])
            
            data.append(['NO_VAD'])
            
            data.append([0])
            
            data.append([0])
            
            data.append([0])
            
            data.append([0])
            
            data.append([0])
            
            data.append([0])
            
        
        # print('data')
        
        # print(data)
        
        # df_temp = pd.DataFrame(np.array(data).reshape(len(list_starts), len(OUT__audio_COL_NAMES)), columns=OUT__audio_COL_NAMES)
        df_temp = pd.DataFrame(np.array(data).transpose(), columns=OUT__audio_COL_NAMES)
        
        # print('df_temp : ')
        # print(df_temp)
        
        
        df_temp_Audio = pd.concat([df_temp_Audio, df_temp], ignore_index=True, sort=False)
    
    # print('df_temp_Audio : ')
    # print(df_temp_Audio)
    
    # sys.stdout.flush()
    # time.sleep(100000000)
    
    
    
    return df_temp_Audio




def check_questions_no(a_txt, text_vals, spliter):
    if text_vals.count(spliter) > 1:
        sys.exit('This question text exists more than one ', spliter, ' in the manual transcription: ', a_txt)






def do_multi_Audio_analysis( ):
    
    
    df_Audio = pd.DataFrame([], columns=OUT__audio_COL_NAMES)
    
    
    df_metadata_temp = df_metadata[['dir_name', 'age', 'diagnosis', 'referral', 'ethnicity', 'gender', 'ENGLISH_FIRST_LANG', 'ENGLISH_ABILITY', 'FIRST_LANG']]
    
    
    #######  muti-processing 
    inputs = zip( list(df_metadata.dir_name) )
    
    n_jobs = min(N_jobs, len(df_metadata))
    print('n_jobs: ', n_jobs)
    sys.stdout.flush()
    
    results = tqdm(Pool(n_jobs).imap_unordered(do_calc_Auduio_analysis, inputs), total=len(df_metadata))
            
    for result in results:
        
        if len(result) > 0:
            
            df_Audio = pd.concat([df_Audio, result], ignore_index=True, sort=False)
    
    
    # # df_Audio_meta = df_metadata_temp.merge(df_Audio, on='dir_name', how='right').sort_values(by=['SNR', 'dir_name'])
    # df_Audio_meta = df_metadata_temp.merge(df_Audio, on='dir_name', how='right').sort_values(by=[ 'dir_name', 'Question'])
    
    # df_Audio_meta.to_csv( Audio_INFO_CSV_out, index=False)
    
    
    
    df_Audio.to_csv( Audio_INFO_CSV_out, index=False)
    
    
    
    
    
    
    
    
    
    
    print('Audio analysis is complete' )







if __name__=='__main__' and '__file__' in globals():
    
    
    # startTime = datetime.now()
    # current_time = startTime.strftime("%Y/%m/%d at %H:%M:%S")
    # print('\n\nThe script starting at: ' + str(current_time), ' \n\n' )
    
    
    N_jobs = int(sys.argv[1])
    
    
    
    '''
    
    My notes on to do: 
        
        1. Generate the VAD, SNR for all audio and save it in a CSV 
        2. Then pick up the audio with Audacity manual transcription and compare VAD and ASR ... 
    '''
    
    
    
    
    
    
    '''
    Testting: WER among the Whisper medium tranbscripts for original (44.1 kHz) and 16 kHz
    '''
    
    ## Read the metadata ... 
    
    # df_metadata = pd.read_csv( '../data/CognoSpeak_metadata__2025_07_24.csv' )
    
    df_metadata = pd.read_csv( ACE_out_all_ACE )
    
    
    
    
    
    # ## The following has been excluded as Q13 was extremely long. 
    # df_metadata = df_metadata[df_metadata.dir_name != 'S_23555_240125_175547']
    
    
    # ## Testing ... 
    # df_metadata = df_metadata[df_metadata.dir_name == 'R_00013_230802_123716']
    # df_metadata = df_metadata[df_metadata.dir_name == 'R_03190_241119_130110']
    # df_metadata = df_metadata[df_metadata.dir_name == 'R_58844_241015_194049']
    # df_metadata = df_metadata[df_metadata.dir_name == 'S_03399_241003_150551']
    # df_metadata = df_metadata[df_metadata.dir_name == 'R_27369_241023_113638']
    
    
    df_metadata = df_metadata.sort_values(by=["dir_name"])
    
    df_metadata = df_metadata.reset_index(drop=True)
    
    
    
    # df_metadata = df_metadata.head()
    
    
    # transforms = jiwer.Compose(
    #     [
    #         jiwer.ExpandCommonEnglishContractions(),
    #         jiwer.RemoveEmptyStrings(),
    #         jiwer.ToLowerCase(),
    #         jiwer.RemoveMultipleSpaces(),
    #         jiwer.Strip(),
    #         jiwer.RemovePunctuation(),
    #         jiwer.ReduceToListOfListOfWords(),
    #     ]
    # )
    
    
    
    VAD_model = load_silero_vad()
    
    
    
    # OUT__audio_COL_NAMES = ['dir_name', 'Question', 'TEXT', 'START', 'END', 'SNR']
    
    OUT__audio_COL_NAMES = ['dir_name', 'Question', 'TEXT', 'START (sec)', 'END (sec)', 'Speech_Audio', 'Pause_Audio', 'Total_Audio', 'SNR']
    
    
    
    
    
    
    
    
    
    
    
    '''
    This is to pin point audio with issues ... 
    Compare WERs between ASRs ... 
    '''
    
    
    
    do_multi_Audio_analysis()
    
    
    
    
    
    #############################
    
    '''
    Next, check the audio quality and add a column to record it 
    '''
    
    
    df_metadata = pd.read_csv( ACE_out_all_ACE )
    df_metadata = df_metadata.reset_index(drop=True)
    
    
    df_Audio = pd.read_csv( Audio_INFO_CSV_out)
    
    
    df_Audio = df_Audio.sort_values(by=['SNR', 'dir_name'], ascending=False)
    
    
    # diff_list( set(df_Audio.dir_name) , set(df_metadata.dir_name))
    
    # diff_list( set(df_metadata.dir_name) , set(df_Audio.dir_name))
    
    
    df_Audio = df_Audio[[ 'dir_name', 'Question', 'TEXT', 'SNR' ]]
    
    df_Audio.drop_duplicates(subset=df_Audio.columns, keep='first', inplace=True)
    
    
    
    # for a_dr in list(set(df_Audio.dir_name)):
        
    #     if len(df_Audio[df_Audio.dir_name == a_dr]) != 14:
    #         print(a_dr, len(df_Audio[df_Audio.dir_name == a_dr]))
    
    
    
    
    df_Audio = df_Audio.merge(df_metadata[['dir_name', 'diagnosis']], on='dir_name', how='inner')
    
    df_Audio.SNR = df_Audio.SNR.astype('float') 
    
    
    
    ## Automatically drop those who has no audio or SNR is 0
    
    df_drop = df_Audio[(df_Audio.TEXT == 'NO_VAD') | (df_Audio.SNR == 0)]
    
    df_drop.insert(len(df_drop.columns), 'AUDIO_SNR', ['ISSUES']*len(df_drop) )
    
    df_drop = df_drop[['dir_name', 'AUDIO_SNR']]
    
    df_drop.drop_duplicates(subset=df_drop.columns, keep='first', inplace=True)
    
    
    
    ## For the rest of the dirs, calculate the mean SNR
    
    df = df_Audio[~df_Audio.dir_name.isin(df_drop.dir_name)][['dir_name', 'Question', 'SNR']]
    
    
    
    
    
    # df_Audio_temp['AUDIO_SNR'] = df_Audio_temp.groupby('dir_name')['SNR'].transform('mean')
    
    # df_Audio_temp = df_Audio_temp[['dir_name', 'AUDIO_SNR']]
    
    # df_Audio_temp.drop_duplicates(subset=df_Audio_temp.columns, keep='first', inplace=True)
    
    
    
    
    stats = df.groupby('dir_name')['SNR'].agg(['mean', 'std'])
    
    df = df.join(stats, on='dir_name')
    
    df['AUDIO_SNR'] = df.apply(
        lambda row: f"{row['mean']:.2f} ± {row['std']:.2f}", axis=1
    )
    
    df = df[['dir_name', 'AUDIO_SNR']]
    df.drop_duplicates(subset=df.columns, keep='first', inplace=True)
    
    
    df_aud_issues = pd.concat([df_drop, df], ignore_index=True, sort=False)
    
    
    df_aud_issues = df_aud_issues.sort_values(by=["dir_name"], ascending=True)
    
    
    df_metadata = df_metadata.merge(df_aud_issues, on='dir_name', how='inner')
    
    
    
    
    
    
    
    
    
    # df_Audio[df_Audio.SNR >=-1].diagnosis.value_counts()
    
    # df_Audio[(df_Audio.SNR >=-0.5) & (df_Audio.diagnosis=='Dementia')].dir_name
    
    # df_Audio[(df_Audio.dir_name == 'R_27369_241023_113638') & (df_Audio.Question == 'Q11')]
    
    
    # df_metadata.assessment_type == 'CognoSpeak Assessment'
    
    # df_metadata.assessment_type == 'CognoMemory Assessment'
    
    # df_metadata.Q10
    
    # df_metadata.Q11
    
    # df_metadata.SNR = df_metadata.Q10.astype('float') 
    
    # df_metadata.SNR = df_metadata.Q11.astype('float') 
    
    
    
    # df_metadata[ ((df_metadata.assessment_type == 'CognoSpeak Assessment') | (df_metadata.assessment_type == 'CognoMemory Assessment')) & ((df_metadata.Q10 < 55) | (df_metadata.Q11 < 55)) ]
    
    
    # df_cogno = df_metadata[ (df_metadata.assessment_type == 'CognoSpeak Assessment') | (df_metadata.assessment_type == 'CognoMemory Assessment')]
    
    # df_cogno.Q10 = df_cogno.Q10.astype('float') 
    
    # df_cogno.Q11 = df_cogno.Q11.astype('float') 
    
    
    # df_cogno[ (df_cogno.Q10 < 60) | (df_cogno.Q11 < 60) ]
    
    
    #############################
    
    
    # detelete late 
    
    # df_metadata = pd.read_csv( Audio_info_metadata_out )
    
    
    
    '''
    Here, I also need to update values which I receive by email .... 
    
    I update the values in this sheet: 
    
    https://docs.google.com/spreadsheets/d/1FjuShwjzl-MbLyzkAFfzrO3U6AnFt2814zGik_7uipU/edit?gid=1651992203#gid=1651992203
    
    '''
    
    df_man_UP = pd.read_csv( '../data/MANUAL_QUESTION_CHECK - update_info.csv' )
    
    df_metadata = df_metadata.reset_index(drop=True)
    for ind in df_man_UP.index:
        
        df_metadata.loc[( df_metadata[df_metadata.dir_name == df_man_UP['dir_name'][ind]].index.item(), df_man_UP['col_2_update'][ind] )] = df_man_UP['VALUE'][ind]
    
    
    # df_metadata[df_metadata.dir_name == 'R_26643_251124_165653'].CONSENT
    
    # df_metadata[df_metadata.dir_name == 'S_81616_241022_150333']['PHQ-9']
    # df_metadata[df_metadata.dir_name == 'S_81616_241022_150333']['GAD-7']
    
    
    # df_metadata[df_metadata.dir_name == 'S_38980_250717_164330']['PHQ-9']
    # df_metadata[df_metadata.dir_name == 'S_38980_250717_164330']['GAD-7']
    
    
    ## Also, check if any of the "to_ignore_assessments" are in the metadata ... 
    
    df_metadata = df_metadata[~df_metadata.dir_name.isin([x.replace('__', '_') for x in to_ignore_assessments])]
    
    
    
    df_metadata.to_csv( Audio_info_metadata_out, index = False )
    
    
    
    
    executionTime = (datetime.now() - startTime)
    current_time = datetime.now().strftime("%Y/%m/%d at %H:%M:%S")
    print('\n\nThe script completed at: ' + str(current_time))
    print('Execution time: ' + str(executionTime), ' \n\n')
    
    
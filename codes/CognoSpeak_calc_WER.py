#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Apr 15 20:58:39 2024

@author: madhupahar
"""


'''
I created this script to check the word error rate (WER) for varoius texts ... 
'''


import warnings
warnings.filterwarnings('ignore')


import os, sys, time

# import whisper
# import torch

# import librosa

# from jiwer import wer


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


def do_calc_SNR(args):
    
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
    
    
    
    df_temp_SNR = pd.DataFrame([], columns=OUT__SNR_COL_NAMES)
    
    for audio_file in audio_files:
        
        
        # print('audio file: ')
        # print(audio_file)
        # sys.stdout.flush()
        # time.sleep(100000000)
        
        y_list, _ = librosa.load(audio_file)
        SNR = signaltonoise_dB(y_list)
        
        
        
        
        df_temp_SNR.loc[len(df_temp_SNR.index)] = [a_dir] + [audio_file.split('.wav')[0].split('_')[-1]] + [SNR]
                
    return df_temp_SNR
    



def do_calc_VAD(args):
    
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
    
    
    
    df_temp_SNR = pd.DataFrame([], columns=OUT__VAD_COL_NAMES)
    
    for audio_file in audio_files:
        
        
        # print('audio file: ')
        # print(audio_file)
        # sys.stdout.flush()
        # time.sleep(100000000)
        
        wav = read_audio(audio_file)
        speech_timestamps = get_speech_timestamps(
          wav,
          VAD_model,
          return_seconds=True,  # Return speech timestamps in seconds (default is samples)
        )
        
        # print(speech_timestamps)
        
        
        
        # df_temp_SNR.loc[len(df_temp_SNR.index)] = [a_dir] + [audio_file.split('.wav')[0].split('_')[-1]] + [SNR]
        df_temp_SNR.loc[len(df_temp_SNR.index)] = [a_dir] + [audio_file.split('.wav')[0].split('_')[-1]] + [len(speech_timestamps)] + [speech_timestamps]
                
    return df_temp_SNR



def do_calc_wer(args):
    
    a_dir = args[0]
    
    ori_txt_files = glob.glob( ori_txt_dir+ a_dir + '/*.txt')
    
    # # print('ori_txt_files: ')
    # # print(ori_txt_files)
    # sys.stdout.flush()
    # time.sleep(100000000)
    
    # I have to use 
    
    # signaltonoise_dB(a, axis=0, ddof=0)
    
    
    
    df_temp_wer = pd.DataFrame([], columns=OUT__WER_COL_NAMES)
    
    for a_txt in ori_txt_files:
        
        tr_a_txt = a_txt.replace(ori_txt_dir, trans_txt_dir)
        
        # print('a_txt: ')
        # print(a_txt)
        # print('tr_a_txt: ')
        # print(tr_a_txt)
        # print('audio file: ')
        # print(audio_file)
        # sys.stdout.flush()
        # time.sleep(100000000)
        
        if os.path.exists( tr_a_txt ):
            
            # reference_text = "The cat is sleeping on the mat."
            # hypothesis_text = "The catx is sleeping on the mat."
            # hypothesis_text = "The cat is playing on mat."
            
            ori_text = further_process_text(read_file(a_txt))
            trans_text = read_file(tr_a_txt)
            
            # print('ori_text: ')
            # print(ori_text)
            # print('trans_text: ')
            # print(trans_text)
            # sys.stdout.flush()
            # time.sleep(100000000)
            
            # wer_score = wer(reference_text, hypothesis_text)
            # print("Word Error Rate (WER):", wer_score)
            
            if ori_text != '' and trans_text != '':
                
                # print(wer(ori_text, trans_text))
                
                # print('a_txt : ', a_txt)
                # print('ori_text: ')
                # print(ori_text)
                # print('trans_text: ')
                # print(trans_text)
                # sys.stdout.flush()
                # time.sleep(100000000)
                try:
                    WeR = jiwer.wer(
                                ori_text,
                                trans_text,
                                truth_transform=transforms,
                                hypothesis_transform=transforms,
                            )
                    
                    # df_temp_wer.loc[len(df_temp_wer.index)] = [a_dir] + [a_txt.split('.txt')[0].split('_')[-1]] + [ round(wer(ori_text, trans_text), 4) ] + [a_txt] + [tr_a_txt] + [ori_text] + [trans_text]
                    df_temp_wer.loc[len(df_temp_wer.index)] = [a_dir] + [a_txt.split('.txt')[0].split('_')[-1]] + [ round(WeR, 4) ] + [a_txt] + [tr_a_txt] + [ori_text] + [trans_text]
                except ValueError:
                    print('\n\n**** There is an issue in : ', a_txt)
                    print('Original text: ', ori_text)
                    print('translated text: ', trans_text)
                    print('*****\n\n')
                    sys.stdout.flush()
                
    return df_temp_wer



def check_questions_no(a_txt, text_vals, spliter):
    if text_vals.count(spliter) > 1:
        sys.exit('This question text exists more than one ', spliter, ' in the manual transcription: ', a_txt)






def do_multi_WER( csv_out_name ):
    
    df_WER = pd.DataFrame([], columns=OUT__WER_COL_NAMES)
    
    df_SNR = pd.DataFrame([], columns=OUT__SNR_COL_NAMES)
    
    #######  muti-processing 
    inputs = zip( list(df_metadata.dir_name) )
    
    n_jobs = min(N_jobs, len(df_metadata))
    print('n_jobs: ', n_jobs)
    sys.stdout.flush()
    
    df_metadata_temp = df_metadata[['dir_name', 'age', 'diagnosis', 'referral', 'ethnicity', 'gender', 'ENGLISH_FIRST_LANG', 'ENGLISH_ABILITY', 'FIRST_LANG']]
    
    ## WER
    results = tqdm(Pool(n_jobs).imap_unordered(do_calc_wer, inputs), total=len(df_metadata))
    
    for result in results:
        
        if len(result) > 0:
            
            df_WER = pd.concat([df_WER, result], ignore_index=True, sort=False)
    
    
    df_WER_wer = df_metadata_temp.merge(df_WER, on='dir_name', how='right').sort_values(by=["WER", "dir_name"], ascending=False)
    df_WER_wer.to_csv('../data/ASR_logs/WER__'+csv_out_name+'.csv', index=False)
    
    df_WER_dir = df_metadata_temp.merge(df_WER, on='dir_name', how='right').sort_values(by=["dir_name"])
    df_WER_dir.to_csv('../data/ASR_logs/WER__'+csv_out_name+'_dir.csv', index=False)
    
    
    
    
    print('WER calc is complete for: ', csv_out_name)







if __name__=='__main__' and '__file__' in globals():
    
    
    # startTime = datetime.now()
    # current_time = startTime.strftime("%Y/%m/%d at %H:%M:%S")
    # print('\n\nThe script starting at: ' + str(current_time), ' \n\n' )
    
    
    N_jobs = int(sys.argv[1])
    
    
    
    
    
    '''
    Testting: WER among the Whisper medium tranbscripts for original (44.1 kHz) and 16 kHz
    '''
    
    ## Read the metadata ... 
    
    # df_metadata = pd.read_csv( final_sorted_CognoSpeak_metadata )
    
    df_metadata = pd.read_csv( '../data/CognoSpeak_metadata__2025_07_28.csv' )
    
    
    # ## The following has been excluded as Q13 was extremely long. 
    # df_metadata = df_metadata[df_metadata.dir_name != 'S_23555_240125_175547']
    
    
    # ## Testing ... 
    # df_metadata = df_metadata[df_metadata.dir_name == 'R_00013_230802_123716']
    # df_metadata = df_metadata[df_metadata.dir_name == 'R_03190_241119_130110']
    # df_metadata = df_metadata[df_metadata.dir_name == 'R_58844_241015_194049']
    # df_metadata = df_metadata[df_metadata.dir_name == 'S_03399_241003_150551']
    
    
    df_metadata = df_metadata.sort_values(by=["dir_name"])
    
    df_metadata = df_metadata.reset_index(drop=True)
    
    
    
    transforms = jiwer.Compose(
        [
            jiwer.ExpandCommonEnglishContractions(),
            jiwer.RemoveEmptyStrings(),
            jiwer.ToLowerCase(),
            jiwer.RemoveMultipleSpaces(),
            jiwer.Strip(),
            jiwer.RemovePunctuation(),
            jiwer.ReduceToListOfListOfWords(),
        ]
    )
    
    
    
    VAD_model = load_silero_vad()
    
    
    
    OUT__WER_COL_NAMES = ['dir_name', 'Question', 'WER', 'ori_text_file', 'trans_text_file', 'ori_txt', 'trans_txt']
    
    OUT__SNR_COL_NAMES = ['dir_name', 'Question', 'SNR']
    
    OUT__VAD_COL_NAMES = ['dir_name', 'Question', 'N_VAD', 'VAD_INFO']
    
    
    
    '''
    Comparing WER among ASRs, not relevant any more ... 
    '''
    
    
    # ## Whisper Medium
    # ori_txt_dir = '../data/FINAL_ASR_Whisper_med_OLD/'
    # trans_txt_dir = '../data/FINAL_ASR_Whisper_med/'
    
    # do_multi_WER( 'Whisper_medium_44100vs16000' )
    
    
    
    
    
    # ## Wav2Vec2
    # ori_txt_dir = '../data/FINAL_ASR_W2V2_OLD/'
    # trans_txt_dir = '../data/FINAL_ASR_W2V2/'
    
    # do_multi_WER( 'W2V2_44100vs16000' )
    
    
    
    
    
    # ## Nvidia Nemo
    # ori_txt_dir = '../data/FINAL_ASR_Nemo_OLD/'
    # trans_txt_dir = '../data/FINAL_ASR_Nemo/'
    
    # do_multi_WER( 'Nemo_44100vs16000' )
    
    
    
    
    
    
    
    # # print(results)
    # sys.stdout.flush()
    # time.sleep(100000000)
    
    
    
    
    
    
    
    
    
    # df_WER = pd.read_csv( '../data/ASR_logs/WER__Whisper_medium_44100vs16000_wer.csv' )
    
    
    # df_WER[df_WER.WER != 0].Question.value_counts()
    
    
    # np.mean(df_WER.WER)
    
    # np.std(df_WER.WER)
    
    
    
    
    # sys.stdout.flush()
    # time.sleep(100000000)
    
    
    
    
    
    
    
    '''
    This is to compare the ASR perforamances ... 
    Calculate the WER among the ASRs based on the manual transcripts done by Sara. 
    This is mentioned in my ethnic minority paper ... 
    '''
    
    
    # df_metadata = pd.read_csv( '../data/CognoSpeak_metadata__2024_12_26.csv' )
    # df_metadata = pd.read_csv( '../data/CognoSpeak_metadata__2025_05_29.csv' )
    df_man_trans = df_metadata[df_metadata.trans_txt!=NO_EXIST_STR]
    df_man_trans = df_man_trans.reset_index(drop=True)
    
    ori_txt_dir = manual_transcript_out
    
    # ori_txt_dir = '../data/CognoSpeak_results/data/'
    trans_txt_dir = ASR_trans_out_whp_med_44kHz
    
    do_multi_WER( 'MAN_WhispMED44kHz' )
    
    
    
    # ori_txt_dir = '../data/CognoSpeak_results/data/'
    trans_txt_dir = ASR_trans_out_wav2vec2_16kHz
    
    do_multi_WER( 'MAN_W2V216kHz' )
    
    
    
    # ori_txt_dir = '../data/CognoSpeak_results/data/'
    trans_txt_dir = ASR_trans_out_nemo_16kHz
    
    do_multi_WER( 'MAN_Nemo16kHz' )
    
    
    
    sys.stdout.flush()
    time.sleep(100000000)
    
    
    
    
    '''
    This is to pin point audio with issues ... 
    Compare WERs between ASRs ... 
    '''
    
    ori_txt_dir = ASR_trans_out_whp_med_44kHz
    trans_txt_dir = ASR_trans_out_wav2vec2_16kHz
    
    do_multi_WER( 'Whis_MedvsW2V2' )
    
    
    
    
    
    ori_txt_dir = ASR_trans_out_whp_med_44kHz
    trans_txt_dir = ASR_trans_out_nemo_16kHz
    
    do_multi_WER( 'Whis_MedvsNemo' )
    
    
    
    
    
    ori_txt_dir = ASR_trans_out_wav2vec2_16kHz
    trans_txt_dir = ASR_trans_out_nemo_16kHz
    
    do_multi_WER( 'W2V2vsNemo' )
    
    
    sys.stdout.flush()
    time.sleep(100000000)
    
    
    
    
    
    
    '''
    I have reliased that my SNR is NOT very accurate to distinguish a noisy or clear speech 
    I need to find out an effective way to measure ... 
    '''
    
    
    
    ## For 16 kHz, use: FINAL_EXT_AUDIO_16kHz

    ## static noise
    a_noisy_audio = '../data/FINAL_EXTRACTED_AUDIO/S_41738_240518_161749/S_41738_240518_161749_Q11.wav'
    
    
    ## quiet but clean 
    a_clean_audio = '../data/FINAL_EXTRACTED_AUDIO/S_41738_240518_161749/S_41738_240518_161749_Q10.wav'
    
    
    ## Backgound noise in all recs ... 
    # a_noisy_audio = '../data/FINAL_EXTRACTED_AUDIO/S_93509_231121_205041/S_93509_231121_205041_Q10.wav'
    
    ## A good clean one ... 
    a_clean_audio = '../data/FINAL_EXTRACTED_AUDIO/S_11134_231206_130621/S_11134_231206_130621_Q10.wav'
    
    
    an_audio = a_noisy_audio
    
    an_audio = a_clean_audio
    
    # y_list, SR = librosa.load(an_audio, sr=None)
    
    # plt.plot(y_list)
    
    print('itlakjsdlakdsj ')
    
    ####### I am trying with a VAD 
    ## https://github.com/snakers4/silero-vad?tab=readme-ov-file
    
    
    
    
    
   
    
    sys.stdout.flush()
    time.sleep(100000000)
    
    
    
    
    
    signaltonoise_dB(y_list)
    
    import math
    
    list_SNR = []
    for i in range(math.floor(len(y_list)/SR)-1): 
        
        audio_chunk = y_list[(i*SR):(i+1)*SR]
        
        list_SNR.append( signaltonoise_dB(audio_chunk) )
        
    print(np.mean(list_SNR))
    print(np.std(list_SNR))
    
    
    # rmse = librosa.feature.rms(y_list, frame_length=1024, hop_length=512, center=True)
    
    # S = librosa.magphase(librosa.stft(y_list, window=np.ones, center=False))[0]
    # plt.plot(librosa.feature.rms(S=S)[0])
    # plt.show()
    
    S, phase = librosa.magphase(librosa.stft(y_list))
    rms = librosa.feature.rms(S=S)
    plt.plot(rms[0])
    
    
    ######## This is PESQ scores .... 
    ## Should work in pyfeat env 
    ## https://pypi.org/project/pesq/
    
    
    from scipy.io import wavfile
    from pesq import pesq
    
    
    rate, ref = wavfile.read(a_clean_audio)
    rate, deg = wavfile.read(a_noisy_audio)
    
    
    print(pesq(rate, ref, deg, 'wb'))
    print(pesq(rate, ref, deg, 'nb'))
    
    
    
    sys.stdout.flush()
    time.sleep(100000000)
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    '''
    Generating some figures to investigate WERs among different metadata 
    '''
    
    csv_out_name = 'Whis_MedvsW2V2'
    
    csv_name = '../data/ASR_logs/WER__'+csv_out_name+'_dir.csv'
    
    df_wer = pd.read_csv( csv_name )
    
    df_wer = df_wer.reset_index(drop=True)
    
    plt.plot( df_wer.WER )
    
    
    
    
    
    csv_name = '../data/ASR_logs/WER__'+csv_out_name+'_wer.csv'
    
    df_wer = pd.read_csv( csv_name )
    
    df_wer = df_wer.sort_values(by=["dir_name", "Question"])
    
    
    df_wer = df_wer.sort_values(by=["dir_name"])
    
    df_wer = df_wer.reset_index(drop=True)
    
    ## This is plotting all the WER for all questions ... 
    
    plt.plot( df_wer.WER )
    
    
    
    ## This is grouping all different demographics and getting their WERs 
    
    
    
    df_wer_grouped = get_grouped_df(df_wer, 'dir_name', 'WER', 'mean_WER')
    
    df_wer_grouped = df_wer_grouped.drop_duplicates(subset="dir_name", keep='first')
    df_wer_grouped = df_wer_grouped.reset_index(drop=True)
    
    plt.plot( df_wer_grouped.mean_WER )
    
    
    
    
    
    
    
    
def make_fig(demo_col):
    df_wer_grouped = get_grouped_df(df_wer, demo_col, 'WER', 'mean_WER')
    
    df_wer_grouped = df_wer_grouped.drop_duplicates(subset=demo_col, keep='first')
    df_wer_grouped = df_wer_grouped.reset_index(drop=True)
    
    # plt.plot( df_wer_grouped.mean_WER )
    
    X_VALs = df_wer_grouped[demo_col]
    Y_VALs = df_wer_grouped.mean_WER
    
    fig_out_file = '../data/CognoSpeak_results/results/figures/'+a_COL+'.png'
    
    fig, ax = plt.subplots(nrows = 1, ncols = 1, figsize=(20, 15))
    
    fig.subplots_adjust(bottom=0.3)
    
    # fruits = ['apple', 'blueberry', 'cherry', 'orange']
    # counts = [40, 100, 30, 55]
    # bar_labels = ['red', 'blue', '_red', 'orange']
    # bar_colors = ['tab:red', 'tab:blue', 'tab:red', 'tab:orange']
    
    # ax.bar(list_VALUES, list_c_n_misspercnt, label=bar_labels, color=bar_colors)
    ax.bar(X_VALs, Y_VALs, color='red')
    
    # addlabels(X_VALs, Y_VALs, list_c_n_actual)
    
    ax.set_title('Mean-WERs for: '+demo_col, fontsize = 25)
    
    ax.set_ylabel('Mean-WER', fontsize = 20)
    # ax.legend(title='Fruit color')
    # ax.set_yticks( list(range(0, 110, 10)), [str(x)+'%' for x in list(range(0, 110, 10))], fontsize = 15)
    ax.set_xticks(X_VALs, X_VALs, rotation = 70, fontsize = 15)
    
    plt.show()
    
    
    plt.savefig( fig_out_file )
    plt.close()
    print('\nThe figure has been successfully generated as: ', fig_out_file, '\n')
    
    
    
    
    
    
    
    
    # make_fig( 'dir_name' )
    
    
    
    df_wer['ethnicity'].value_counts()
    make_fig( 'ethnicity' )
    
    
    
    
    make_fig( 'diagnosis' )
    
    
    make_fig( 'referral' )
    
    
    make_fig( 'gender' )
    
    
    
    
    ## https://matplotlib.org/stable/gallery/lines_bars_and_markers/barchart.html#sphx-glr-gallery-lines-bars-and-markers-barchart-py
    
    species = ("Adelie", "Chinstrap", "Gentoo")
    penguin_means = {
        'Bill Depth': (18.35, 18.43, 14.98),
        'Bill Length': (38.79, 48.83, 47.50),
        'Flipper Length': (189.95, 195.82, 217.19),
    }
    
    x = np.arange(len(species))  # the label locations
    width = 0.25  # the width of the bars
    multiplier = 0
    
    fig, ax = plt.subplots(layout='constrained')
    
    for attribute, measurement in penguin_means.items():
        offset = width * multiplier
        rects = ax.bar(x + offset, measurement, width, label=attribute)
        ax.bar_label(rects, padding=3)
        multiplier += 1
    
    # Add some text for labels, title and custom x-axis tick labels, etc.
    ax.set_ylabel('Length (mm)')
    ax.set_title('Penguin attributes by species')
    ax.set_xticks(x + width, species)
    ax.legend(loc='upper left', ncols=3)
    ax.set_ylim(0, 250)
    
    plt.show()
    
    
    all_ASR_types = ['Whis_MedvsW2V2', 'Whis_MedvsNemo', 'W2V2vsNemo']
    
    
    # for ASR_type in all_ASR_types:
        
    
        
    '''
    This is the test I am doing to cross-check each text 
    '''
    
    
    ## Working with WER: https://medium.com/@johnidouglasmarangon/how-to-calculate-the-word-error-rate-in-python-ce0751a46052
    
    
    df_wer_test = pd.read_csv( '../data/ASR_logs/WER__MAN_WhispMED44kHz_wer.csv' )
    
    
    
    
    
    act_text = df_wer_test[df_wer_test.dir_name == 'R_36338_240716_112815']['ori_txt'][1602]
    
    trans_text = df_wer_test[df_wer_test.dir_name == 'R_36338_240716_112815']['trans_txt'][1602]
    
    df_wer_test[df_wer_test.dir_name == 'R_36338_240716_112815']['WER'][1602]
    
    df_wer_test[df_wer_test.dir_name == 'R_36338_240716_112815']['Question'][1602]
    
    
    
    
    
    
    
    
    
    
    '''
    So, I have developed a way to cross-check each question and then mark them at: 
        https://docs.google.com/spreadsheets/d/1FjuShwjzl-MbLyzkAFfzrO3U6AnFt2814zGik_7uipU/edit?gid=0#gid=0
    
    The Google Sheet needs to be downloaded as a CSV file and replace: 
        MANUAL_QUESTION_CHECK - Sheet1.csv in '../data'
    
    '''
    
    # Prepare the script to exclude those from the CSV file ... 
    
    
    
    
    
    
    
    
    
    
    
    
    
    '''
    This is my investigation into the audio overlap due to TherapyBox issue ... 
    My intentionas are:
        1. Get the list from Bahman and see if the overalpped audio appears in the manual transcriptions 
        2. If they do, then find a way to fix them ...
    '''
    
    ## I manuall downloaded it from: https://docs.google.com/spreadsheets/d/1FD48btVurPNuCKdvVbXug_ZyR-OaUMICXSVJWIm8Fds/edit?gid=0#gid=0
    df_bahman_overlap = pd.read_csv( '../data/ASR_logs/CognoSpeakNew-Mismatches spreadsheet - Sheet1.csv', names=['A', 'file_path' ] )
    
    bahman_dirs = natsorted(list(set([x.split('/')[0] for x in df_bahman_overlap.file_path])))
    
    intersection( bahman_dirs, df_metadata[df_metadata.trans_txt != NO_EXIST_STR].dir_name)
    
    intersection( bahman_dirs, df_txt_mismatch.dir_name)
    
    
    df_metadata[df_metadata.dir_name.isin(bahman_dirs)]
    
    
    df_missmatch_2_fix = df_metadata[df_metadata.dir_name.isin(bahman_dirs)][['dir_name', 'assess_date', 'age', 'diagnosis', 'diagnosis_type', 'referral',
    'ethnicity', 'gender', 'ENGLISH_FIRST_LANG', 'ENGLISH_ABILITY', 'FIRST_LANG', 'EDUCATION_INFO', 'OTHER_CONDITIONS']]
    
    
    # df_missmatch_2_fix = pd.DataFrame({'dirs': bahman_dirs})
    
    df_missmatch_2_fix.to_csv('../data/audio_overlap_2_fix.csv', index=False)
    
    
    
    
    
    
    
    
    
    
    '''
    Checking the audio lengths and text overlap or empty transcripts 
    '''
    
    
    df_metadata
    
    # df_mismatch = pd.DataFrame([], columns=['dir_name']+['Q'+str(i)+'_type' for i in range(1, 15)])
    # df_txt_mismatch = pd.DataFrame([], columns=['dir_name', 'Q_0', 'Q_1', 'Q_0_Len', 'Q_1_Len', 'Q_0_content', 'Q_1_content', 'offset_len'])
    df_txt_mismatch = pd.DataFrame([], columns=['dir_name', 'Q_0', 'Q_1', 'Q_0_Len', 'Q_1_Len', 'Q_0_content', 'Q_1_content'])
    
    for ind in tqdm(df_metadata.index):
        
        # all_Q_typE = ['Q'+str(i) for i in range(1, 15)]
        
        # for i in range(len(all_Q_typE)-1):
            
        #     q_i0_cont = read_file( glob.glob(ASR_trans_out_whp_med_44kHz + df_metadata['dir_name'][ind] + '/*_'+all_Q_typE[i]+'.txt')[0] )
        #     q_i1_cont = read_file( glob.glob(ASR_trans_out_whp_med_44kHz + df_metadata['dir_name'][ind] + '/*_'+all_Q_typE[i+1]+'.txt')[0] )
            
        #     if q_i1_cont.lower().startswith( q_i0_cont[:10].lower() ):
                
        #         # print('')
        #         # print(df_metadata['dir_name'][ind])
        #         # print(all_Q_typE[i], ' len: ', df_metadata[all_Q_typE[i]][ind])
        #         # print(all_Q_typE[i+1], ' len: ', df_metadata[all_Q_typE[i+1]][ind])
        #         # print(all_Q_typE[i], ' : Whisper Medium trans: ')
        #         # print( q_i0_cont )
        #         # print(all_Q_typE[i+1], ' : Whisper Medium trans: ')
        #         # print( q_i1_cont )
        #         # print('')
                
        #         df_txt_mismatch.loc[len(df_txt_mismatch.index)] = [df_metadata['dir_name'][ind]] + [all_Q_typE[i]] + [all_Q_typE[i+1]] + [df_metadata[all_Q_typE[i]][ind]] + [df_metadata[all_Q_typE[i+1]][ind]] + [q_i0_cont] + [q_i1_cont]
            
        
        if df_metadata['Q10'][ind] > 62 or df_metadata['Q11'][ind] > 62:
            
            q10_cont = read_file( glob.glob(ASR_trans_out_whp_med_44kHz + df_metadata['dir_name'][ind] + '/*_Q10.txt')[0] )
            q11_cont = read_file( glob.glob(ASR_trans_out_whp_med_44kHz + df_metadata['dir_name'][ind] + '/*_Q11.txt')[0] )
            
            
            # within_file = glob.glob( final_extract_dir + df_metadata['dir_name'][ind]  +'/'+df_metadata['dir_name'][ind]+'_Q11.wav' )[0]
            # find_file = glob.glob( final_extract_dir + df_metadata['dir_name'][ind]  +'/'+df_metadata['dir_name'][ind]+'_Q10.wav' )[0]
            # offSet_len = find_offset(within_file, find_file, 10)
            
            # print('offSet_len : ', offSet_len)
            
            
            # df_txt_mismatch.loc[len(df_txt_mismatch.index)] = [df_metadata['dir_name'][ind]] + ['Q10'] + ['Q11'] + [df_metadata['Q10'][ind]] + [df_metadata['Q11'][ind]] + [q10_cont] + [q11_cont] + [offSet_len]
            df_txt_mismatch.loc[len(df_txt_mismatch.index)] = [df_metadata['dir_name'][ind]] + ['Q10'] + ['Q11'] + [df_metadata['Q10'][ind]] + [df_metadata['Q11'][ind]] + [q10_cont] + [q11_cont]
            
            
    
    ## FInd out the metadata of those overlapped dirs 
    
    df_txt_mismatch_metadata = df_txt_mismatch.merge(df_metadata, on='dir_name', how='left')
    
    # df_txt_mismatch_metadata.to_csv( '../data/ASR_logs/overlap_info.csv', index=False )
    
    
    '''
    This is by checking the audio overlap ... 
    
    It does not work ... 
    '''
    
    ## https://dev.to/hiisi13/find-an-audio-within-another-audio-in-10-lines-of-python-1866
    
    ## https://github.com/hiisi13/audio-offset-finder
    
    
    for ind in tqdm(df_txt_mismatch.index):
        
        Q10_audio, Sr = librosa.load( glob.glob( final_extract_dir + df_txt_mismatch['dir_name'][ind]  +'/'+df_txt_mismatch['dir_name'][ind]+'_Q10.wav' )[0], sr=None)
        Q11_audio, Sr = librosa.load( glob.glob( final_extract_dir + df_txt_mismatch['dir_name'][ind]  +'/'+df_txt_mismatch['dir_name'][ind]+'_Q11.wav' )[0], sr=None)
        
        if list(Q11_audio) in (list(Q10_audio)):
            print('yes')
        
        print(all(item in Q11_audio for item in Q10_audio))
        
        dir_name = 'S_83098_240726_122105'
    
    
    list_1 = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10"]
    win_1 = ["1", "2", "3", "4"]
    win_2 = ['1', '12']
    
    print(all(item in list_1 for item in win_1))
    print(all(item in list_1 for item in win_2))
    
    
    # The timestamps for haullucinations will be almost the same, may be it is one way to identify these ... 
    
    
    
    ## This is about finding out the Whisper halucinations ... 
    
    for ind in tqdm(df_metadata.index):
        
        all_Q_typE = ['Q'+str(i) for i in range(1, 15)]
        
        for i in range(len(all_Q_typE)):
            
            df_Q = pd.read_csv( glob.glob(ASR_trans_out_whp_med_44kHz + df_metadata['dir_name'][ind] + '/*_'+all_Q_typE[i]+'__WORD.csv')[0] )
            
            list_0_words = []
            
            for iND in df_Q.index:
                
                # if ( df_Q['end'][iND] - df_Q['start'][iND] ) == 0 and list(df_Q['word']).count(df_Q['word'][iND]) > 2:
                if ( df_Q['end'][iND] - df_Q['start'][iND] ) == 0:
                    
                    list_0_words.append( df_Q['word'][iND] )
            
            
            muLt_o = 0
            
            for a in find_values_counts(list_0_words, 1):
                if a[1]>10:
                    muLt_o = 1
            
            # [muLt_o = 1 for a in find_values_counts(list_0_words, 1) if a[1]>5]
            
            # if len(find_values_counts(list_0_words, 1)) > 0:
                    print('')
                    print(df_metadata['dir_name'][ind])
                    print(all_Q_typE[i])
                    # print( df_Q['word'][iND] )
                    print(find_values_counts(list_0_words, 1))
                    print('')
                    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    '''
    This is the work to cross-check the accuracy of the ASR time-stamps 
    AND, combining the old and the new CognoSpeak .... 
    '''
    
    
    cogno_old_dir = '/Volumes/Shared/cchat/Shared/CognoSpeak_OLD/' 
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
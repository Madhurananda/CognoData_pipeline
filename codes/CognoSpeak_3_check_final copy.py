#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Apr 15 20:58:39 2024

@author: madhupahar
"""

from main import *
from config import *
check_env('ACONDA')

import os, sys, time, glob

import pandas as pd

import json
import numpy as np
# import whisper

from tqdm import tqdm
from natsort import natsorted
from datetime import datetime, timedelta




import librosa

import platform
if platform.system() == 'Darwin':
    from multiprocess.pool import ThreadPool, Pool
else:
    from multiprocessing.pool import ThreadPool, Pool
    
from multiprocessing import cpu_count







def get_demographic_info(an_ID, dir_name, json_val, sprdsht_val, str_var, to_add):
    demographic_info = NO_EXIST_STR
    to_add_notes = ''
    if json_val == '' and sprdsht_val == 'Unknown':
        demographic_info = sprdsht_val
    
    elif type(json_val) == float or type(sprdsht_val) == float:
    
        if json_val == '' and np.isnan(sprdsht_val):
            demographic_info = 'Unknown'
        else:
            print('\nINVESTIGATE: ', str_var,' is not float and not nan for ID: ', an_ID)
            print('sprdsht_val: ', sprdsht_val)
            print('json_val : ', json_val)
            print('dir_name : ', dir_name, '\n')
            to_add = False
            # avoided_IDs.append( an_ID )
            # avoided_IDs_NOTEs.append( str_var+' mismatch. sprdsht_val : '+ str(sprdsht_val) + '; json_val : '+str(json_val) + '; dir_name : ' + str(dir_name) )
            to_add_notes = str_var+' mismatch. sprdsht_val : '+ str(sprdsht_val) + '; json_val : '+str(json_val) + '; dir_name : ' + str(dir_name)
            
    
    elif sprdsht_val != json_val:
        print('\n', str_var, ' does not match for ID: ', an_ID)
        print('sprdsht_val: ', sprdsht_val)
        print('json_val : ', json_val)
        print('dir_name : ', dir_name, '\n')
        to_add = False
        # avoided_IDs.append( an_ID )
        # avoided_IDs_NOTEs.append( str_var+' mismatch. sprdsht_val : '+ str(sprdsht_val) + '; json_val : '+str(json_val) + '; dir_name : ' + str(dir_name) )
        to_add_notes = str_var+' mismatch. sprdsht_val : '+ str(sprdsht_val) + '; json_val : '+str(json_val) + '; dir_name : ' + str(dir_name)
    else:
        demographic_info = json_val
    
    # print('to_add_notes: ', to_add_notes )
    # sys.stdout.flush()
    
    
    return demographic_info, to_add, to_add_notes






def do_get_final_speadsheet_values(args):
    
    
    
    
    ##################################################
    
    
    an_ID, dir_name, assess_gap_info = args[0], args[1], args[2]
    
    to_add = True
    
    consent_given = True
    
    # print('ID : ', an_ID)
    # print('dir_name : ', dir_name)
    # sys.stdout.flush()
    # time.sleep(100000000)
    
    ## Get the json file and read it 
    
    dict_json = get_json_content( extracted_data_dir + dir_name )
    
    
    
    ##################################################
    
    assessment_ID = dict_json['assessment']['taskInstanceIdentity']
    
    
    
    ##################################################
    ## Set these IDs such a way that should be easility noticeable ... 
    fName_val = NO_EXIST_STR
    lName_val = NO_EXIST_STR
    bDay_val = NO_EXIST_STR
    nhs_no = NO_EXIST_STR
    prac_email = NO_EXIST_STR
    phone_val = NO_EXIST_STR
    
    AGE = NO_EXIST_STR
    DIAGNOSIS = NO_EXIST_STR
    REFERRAL = NO_EXIST_STR
    ETHNICITY = NO_EXIST_STR
    GENDER = NO_EXIST_STR
    
    
    # ENGLISH_FLUENCY = NO_EXIST_STR
    
    ENGLISH_FIRST_LANG = NO_EXIST_STR
    ENGLISH_ABILITY = NO_EXIST_STR
    FIRST_LANG = NO_EXIST_STR
    EDUCATION_INFO = NO_EXIST_STR
    REGION = NO_EXIST_STR
    OTHER_COND_str = NO_EXIST_STR
    
    VAL_PHQ = NO_EXIST_STR
    VAL_GAD = NO_EXIST_STR
    VAL_EQ5D = NO_EXIST_STR
    repeat_info = NO_EXIST_STR
    # assess_gap_info = NO_EXIST_STR
    consent_info = NO_EXIST_STR
    
    ##################################################
    
    ## Calculate AGE from json files 
    
    fName_val = dict_json['patient']['profile']['firstName']
    lName_val = dict_json['patient']['profile']['lastName']
    
    b_mm = dict_json['patient']['profile']['birthday']['month']
    b_yy = dict_json['patient']['profile']['birthday']['year']
    birth_date = gen_the_date('1', str(b_mm), str(b_yy))
    
    bDay_val = birth_date.strftime("%m-%Y")
    nhs_no = dict_json['patient']['profile']['nhsNumber']
    prac_email = dict_json['patient']['profile']['email']
    phone_val = dict_json['patient']['profile']['telephone']
    
    # assessment_date = datetime.strptime( dict_json['patient']['updatedAt'].split('T')[0], '%Y-%m-%d')
    assessment_date = datetime.strptime( dict_json['assessment']['taskCompletedAt'].split('T')[0], '%Y-%m-%d')
    AGE = (assessment_date - birth_date) // timedelta(days=365.2425)
    
    
    ##################################################
    
    ## Get diagnosis, referral, ethnicity and gender information from both json and speadsheet and then compare and check .... 
    
    ## Check that if json values match with the spreadsheet ... 
    final_to_add_notes = []
    
    
    
    ## DIAGNOSIS
    if an_ID in list(df_fixed_demographics['Research_IDs']) and 'DIAGNOSIS' == df_fixed_demographics[df_fixed_demographics['Research_IDs']==an_ID]['Notes'].values[0].split(' ')[0]:
        DIAGNOSIS = df_fixed_demographics[df_fixed_demographics['Research_IDs']==an_ID]['Final_decision'].values[0]
        to_add = True
        to_add_notes = ''
    else:
        
        '''
        
        Calculating diagnosis was a bit difficult. 
        
        
        set(df_xls_demographics['Diagnosis'])
        Out[192]: {'Dementia', 'FMD', 'HC', 'MCI', 'Unknown', nan}
        
        dementia
        functionalMovementDisorder
        functionalNeurologicalDisorder
        mildCognitiveImpairment
        undisclosed
        
        '''
        
        json_diagnosis = ''
        
        for a_key in dict_json['patient']['profile']['diagnosis']:
            
            if a_key == 'reason':
                if dict_json['patient']['profile']['diagnosis'][a_key] == 'healthy volunteer':
                    json_diagnosis = 'HC'
            
            elif dict_json['patient']['profile']['diagnosis'][a_key] == True:
                # print(dict_json['patient']['profile']['diagnosis'][a_key])
                # print(a_key)
                        
                if a_key == 'dementia':
                    json_diagnosis = 'Dementia'
                elif a_key == 'functionalMovementDisorder':
                    json_diagnosis = 'FMD'
                elif a_key == 'mildCognitiveImpairment':
                    json_diagnosis = 'MCI'
                # else:
                #     json_diagnosis = a_key
        
        df_xls_demographics[df_xls_demographics['Research ID']==30301]['Assessment ID']
        df_xls_demographics[df_xls_demographics['Research ID']==22637]['Assessment ID']
        
        if len(df_xls_demographics[ (df_xls_demographics['Research ID']==an_ID) & ((df_xls_demographics['Assessment ID']==assessment_ID)) ]['Diagnosis'].values) == 0:
            print('\n\n **** an_ID : ', an_ID)
            print('**** assessment_ID : ', assessment_ID)
            print('The assessment ID', assessment_ID, ' can not be found among the speadhseet for research ID: ', an_ID)
            print('Research ID and Assessment ID do not match. Please check if the spreadsheet has been updated ..... ')
            
            # to_add = False
            
            sys.stdout.flush()
            time.sleep(100000000)
        
        
        
        sprdsht_diagnosis = df_xls_demographics[ (df_xls_demographics['Research ID']==an_ID) & ((df_xls_demographics['Assessment ID']==assessment_ID)) ]['Diagnosis'].values[0]
        
        DIAGNOSIS, to_add, to_add_notes = get_demographic_info(an_ID, dir_name, json_diagnosis, sprdsht_diagnosis, 'DIAGNOSIS', to_add)
        
    final_to_add_notes.append ( to_add_notes )
    
    
    
    ## REFERRAL
    if an_ID in list(df_fixed_demographics['Research_IDs']) and 'REFERRAL' == df_fixed_demographics[df_fixed_demographics['Research_IDs']==an_ID]['Notes'].values[0].split(' ')[0]:
        REFERRAL = df_fixed_demographics[df_fixed_demographics['Research_IDs']==an_ID]['Final_decision'].values[0]
        to_add = True
        to_add_notes = ''
    else:
        json_referral = dict_json['patient']['profile']['referralSource']
        sprdsht_referral = df_xls_demographics[ (df_xls_demographics['Research ID']==an_ID) & ((df_xls_demographics['Assessment ID']==assessment_ID)) ]['Referral Source'].values[0]
        REFERRAL, to_add, to_add_notes = get_demographic_info(an_ID, dir_name, json_referral, sprdsht_referral, 'REFERRAL', to_add)
    
    final_to_add_notes.append ( to_add_notes )
    
    
    
    ## ETHNICITY
    json_ethnicity = dict_json['patient']['profile']['ethnicity']
    sprdsht_ethnicity = df_xls_demographics[ (df_xls_demographics['Research ID']==an_ID) & ((df_xls_demographics['Assessment ID']==assessment_ID)) ]['Ethnicity'].values[0]
    ETHNICITY, to_add, to_add_notes = get_demographic_info(an_ID, dir_name, json_ethnicity, sprdsht_ethnicity, 'ETHNICITY', to_add)
    final_to_add_notes.append ( to_add_notes )
    
    
    
    ## GENDER
    json_gender = dict_json['patient']['profile']['gender']
    sprdsht_gender = df_xls_demographics[ (df_xls_demographics['Research ID']==an_ID) & ((df_xls_demographics['Assessment ID']==assessment_ID)) ]['Gender'].values[0]
    GENDER, to_add, to_add_notes = get_demographic_info(an_ID, dir_name, json_gender, sprdsht_gender, 'GENDER', to_add)
    final_to_add_notes.append ( to_add_notes )
    
    
    
    
    ##################################################
    
    ## Get english langauge information from both json and speadsheet and then compare and check .... 
    
    # for key in dict_json['patient']['profile']:
        
    #     if key == 'englishFluency':
    #         # print('key: ', key)
    #         if dict_json['patient']['profile']['englishFluency'] == True:
    #             ENGLISH_FLUENCY = 1
    #         else:
    #             ENGLISH_FLUENCY = 0 
    #     else:
    #         ENGLISH_FLUENCY = 0 
            
    ## I am adding the new information, which is added to the CognoSpeak later, instead of the column "English"
    
    
    if 'englishFluency' in dict_json['patient']['profile']:
        # This means that the person has English as the first language 
        if dict_json['patient']['profile']['englishFluency'] == True:
            ENGLISH_FIRST_LANG = 'YES'
            ENGLISH_ABILITY = 'NATIVE'
            FIRST_LANG = 'ENGLISH'
        else:
            ENGLISH_FIRST_LANG = 'NO'
            ENGLISH_ABILITY = dict_json['patient']['profile']['englishFluency']
            # FIRST_LANG = dict_json['patient']['profile']['firstLanguage']
            
            if 'firstLanguage' in dict_json['patient']['profile']:
                FIRST_LANG = dict_json['patient']['profile']['firstLanguage']
            # else:
            #     print('This ID does not have English as firstLanguage, the other language information is not provided: ', an_ID)
    # else:
    #     print('This ID does not have language information: ', an_ID)
        
    
    ##################################################
    
    if 'educationLevel' in dict_json['patient']['profile']:
        EDUCATION_INFO = dict_json['patient']['profile']['educationLevel']
    # else:
    #     print('This ID does not have EDUCATION information: ', an_ID)
    
    ##################################################
    
    if 'region' in dict_json['patient']['profile']:
        REGION = dict_json['patient']['profile']['region']
    # else:
    #     print('This ID does not have REGION information: ', an_ID)
    
    ##################################################
    
    if 'otherConditions' in dict_json['patient']['profile']:
        OTHER_COND_str = ''
        for ky in dict_json['patient']['profile']['otherConditions']:
            OTHER_COND_str += ky + ', '
        OTHER_COND_str = OTHER_COND_str[0:len(OTHER_COND_str)-2]
        
    # else:
    #     print('This ID does not have REGION information: ', an_ID)
    
    ##################################################
    
    audio_files = natsorted(glob.glob(final_extract_dir + dir_name + '/*.wav'))
    
    if len(audio_files) != 14:
        print('******** The length of all the audio files are not 14. CHECK :', dir_name)
        sys.stdout.flush()
        time.sleep(100000000)
    
    audio_lens = []
    
    for i in range(1,15):
        audio_found = 0
        for an_audio in audio_files:
            
            if '_Q'+str(i)+'.wav' in an_audio:
                y, _ = librosa.load(an_audio, sr=SR)
                audio_lens.append(len(y)/SR)
                audio_found = 1
        if audio_found != 1:
            audio_lens.append(0)
        
    
    
    
    ##################################################
    
    ## Get the PHQ total value from spreadsheet 
    
    VAL_PHQ = df_PHQ[ (df_PHQ['Assessment ID']==assessment_ID) & (df_PHQ['Research ID']==an_ID) ]['Total'].values[0]
    
    
    ## The following can be used to get values for PHQ and GAD from json files 
    
    # for i in dict_json['assessment']['artifact']['results']:
    #     for key in dict_json['assessment']['artifact']['results'][i]['itemResult']:
    #         print(key)
    #         if 'mcqItems' in key:
    #             for j in dict_json['assessment']['artifact']['results'][i]['itemResult']['mcqItems']:
    #                 dict_json['assessment']['artifact']['results'][i]['itemResult']['mcqItems'][j]
    
    ##################################################
    
    ## Get the GAD total value from spreadsheet 
    
    VAL_GAD = df_GAD[ (df_GAD['Assessment ID']==assessment_ID) & (df_GAD['Research ID']==an_ID) ]['Total'].values[0]
    
    ##################################################
    
    ## Gather the EQ-5D values from the json files ... 
    
    # if_EQ5D = 0
    for i in range(len(dict_json['assessment']['artifact']['results'])):
        for key in dict_json['assessment']['artifact']['results'][i]['itemResult']:
            # print(key)
            if 'checklistItems' in key:
                VAL_EQ5D = dict_json['assessment']['artifact']['results'][-1]['itemResult']['checklistItems'][0]['selectedCheckboxAnswer']
                # if_EQ5D = 1
    
    # if if_EQ5D != 1:
    #     # print('')
    #     # print('ID: ', an_ID, ' does not EQ5D value.')
    #     # print('dir_name : ', dir_name)
    #     # print('The len of the results section of the json file is: ', len(dict_json['assessment']['artifact']['results']))
    #     # print('')
    #     no_EQ5D_IDs.append( an_ID )
    #     no_EQ5D_dates.append( assessment_date.strftime("%d-%m-%Y") )
    
    
    
    ##################################################
    
    ## Check if this ID appears multiple times ... 
    
    repeat_info = 'NO'
    for i in range(len(ZIP__r_IDs_mult_appearance)):
        if ZIP__r_IDs_mult_appearance[i] == an_ID:
            repeat_info = str(ZIP__file_IDs_mult_appearance[i])
    
    
    
    ##################################################
    
    '''
    I have to check CONSENT forms for multiple occerences to check for any changes in the later answers for a participant
    '''
            
    
    
    ## This is a test I am doing to see the list of the consents inside json files 
    
    # print('an_ID : ', an_ID)
    # print('Length of consent forms : ', len( dict_json['assessment']['artifact']['consentData'] ))
    
    not_appearing = True
    
    for c in range(len(dict_json['assessment']['artifact']['consentData'])):
        if 'I agree that the researchers can use extracts of the written, video and sound material collected in this study, without any additional information that could identify me, in scientific publications, for teaching and for future ethically approved studies. This may include short quotes from the audio and/or video recorded data.' in dict_json['assessment']['artifact']['consentData'][c]['text']:
            if_consent = dict_json['assessment']['artifact']['consentData'][c]['consented']
            not_appearing = False
            if not if_consent:
                consent_info = 'NO'
                # print('an_ID : ', an_ID)
                # print('Length of consent forms : ', len( dict_json['assessment']['artifact']['consentData'] ))
                # print(if_consent)
                # n_NO_consent += 1
                consent_given = False
                
            else:
                consent_info = 'YES'
                
                
    if not_appearing:
        print('\n\n******* This ID does not have the consent form. CHECK : ', an_ID)
        sys.stdout.flush()
        time.sleep(100000000)
    
    
    ##################################################
    
    # to_return_vals = [ make_N_chars_a_val(an_ID, 5), fName_val, lName_val, bDay_val, nhs_no, prac_email, phone_val, assessment_ID, dir_name, assessment_date.strftime("%d-%m-%Y"), AGE, DIAGNOSIS, REFERRAL, ETHNICITY, GENDER, ENGLISH_FLUENCY]
    
    # to_return_vals = [ make_N_chars_a_val(an_ID, 5), fName_val, lName_val, bDay_val, nhs_no, prac_email, phone_val, assessment_ID, dir_name, assessment_date.strftime("%Y-%m-%d"), AGE, DIAGNOSIS, REFERRAL, ETHNICITY, GENDER, ENGLISH_FLUENCY]
    
    to_return_vals = [ make_N_chars_a_val(an_ID, 5), fName_val, lName_val, bDay_val, nhs_no, prac_email, phone_val, assessment_ID, dir_name, assessment_date.strftime("%Y-%m-%d"), AGE, DIAGNOSIS, REFERRAL, ETHNICITY, GENDER, ENGLISH_FIRST_LANG, ENGLISH_ABILITY, FIRST_LANG, EDUCATION_INFO, REGION, OTHER_COND_str]
    
    
    for i in range(1,15): 
        # exec( "LIST_Q" + str(i) + ".append({})".format(audio_lens[i-1]) )
        exec( "to_return_vals.append({})".format(audio_lens[i-1]) )
    audio_lens = []
    
    to_return_vals.extend([VAL_PHQ, VAL_GAD, VAL_EQ5D, repeat_info, assess_gap_info, consent_info])
    
    
    return to_add, an_ID, to_return_vals, consent_given, final_to_add_notes

















if __name__=='__main__' and '__file__' in globals():
    
    
    
    if len(sys.argv) < 2:
        print('\n\n Please use : python CognoSpeak_3_check_final.py 15 [where 15 is the number of CPU]\n\n')
        sys.exit()
    
    # startTime = datetime.now()
    # current_time = startTime.strftime("%Y/%m/%d at %H:%M:%S")
    # print('\n\nThe script starting at: ' + str(current_time), ' \n\n' )
    
    N_jobs = int(sys.argv[1])
    
    if N_jobs >= cpu_count():
        print('The max no of CPU available : ', cpu_count())
        sys.exit("Lower the number of CPU\n\n")
    
    
    
    '''
    Step 1: Read the speadsheet. Only consider the IDs which appear only on the speadsheet. 
    I will look into the other IDs later after I hear back from TherapyBox
    '''
    
    
    ## Take only those subjects who appear in the Excel file .... 
    
    
    sprdsht_research_IDs = list(df_xls_summary['Research ID'])
    
    sprdsht_unique_research_IDs = list(set(sprdsht_research_IDs))
    
    
    df_test = pd.read_csv(test_ID_out_csv)
    test_r_IDs = list(df_test['research_IDs'])
    
    
    intersection(list(df_test['research_IDs']) , sprdsht_unique_research_IDs)
    
    sprdsht_unique_research_IDs = diff_list(sprdsht_unique_research_IDs, test_r_IDs)
    
    
    
    
    
    print('The number of IDs on the spreadsheet : ', len(sprdsht_research_IDs))
    print('The number of UNIQUE IDs excluding the test ones on the spreadsheet : ', len(sprdsht_unique_research_IDs))
    
    
    
    converted_zip_file_ID_list = [ i.split('/')[-1] for i in glob.glob(final_extract_dir+'/*') ]
    # converted_zip_r_ID_list = [ int(i.split('_')[1]) for i in converted_zip_file_ID_list]
    converted_zip_r_ID_list = [int(x.split('_')[2]) if x.startswith('STROKE') or x.startswith('MND') else int(x.split('_')[1]) for x in converted_zip_file_ID_list]
    
    transcribed_zip_file_ID_list = [ i.split('/')[-1] for i in glob.glob(final_transcript_dir+'/*') ]
    # transcribed_zip_r_ID_list = [ int(i.split('_')[1]) for i in transcribed_zip_file_ID_list]
    transcribed_zip_r_ID_list = [int(x.split('_')[2]) if x.startswith('STROKE') or x.startswith('MND') else int(x.split('_')[1]) for x in transcribed_zip_file_ID_list]
    
    
    # *********************************************
    # df_test = pd.read_csv(test_ID_out_csv)
    # test_r_IDs = list(df_test['research_IDs'])
    
    
    # intersection(list(df_test['research_IDs']) , sprdsht_unique_research_IDs)
    
    # sprdsht_unique_research_IDs = diff_list(sprdsht_unique_research_IDs, test_r_IDs)
    
    # intersection(list(df_test['research_IDs']) , transcribed_zip_r_ID_list)
    
    # *********************************************
    
    
    
    
    converted_ID_freq_dist = find_values_counts(converted_zip_r_ID_list, 0)
    transcribed_ID_freq_dist = find_values_counts(transcribed_zip_r_ID_list, 0)
    
    
    
    
    ###########################################################################
    ###########################################################################
    '''
    Find out the IDs with multiple diagnosis from spreadsheet only 
    '''
    
    sprdsht_ID_freq_dist = find_values_counts(sprdsht_research_IDs, 1)
    
    
    
    IDs_with_mult_diag_refs = []
    IDs_with_mult_diag_refs_notes= []
    
    for id in sprdsht_ID_freq_dist:
        
        # print(df_xls_demographics[df_xls_demographics['Research ID']==id[0]]['Diagnosis'])
        # print('Multiple Diagnosis')
        
        if len(set(list(df_xls_demographics[df_xls_demographics['Research ID']==id[0]]['Diagnosis'].values))) > 1:
            print('ID: ', id[0])
            print('Diagnosis : ', list(df_xls_demographics[df_xls_demographics['Research ID']==id[0]]['Diagnosis'].values))
            print('Referral Source: ', list(df_xls_demographics[df_xls_demographics['Research ID']==id[0]]['Referral Source'].values))
            print('Assessment ID: ', list(df_xls_demographics[df_xls_demographics['Research ID']==id[0]]['Assessment ID'].values))
            print()
            IDs_with_mult_diag_refs.append( id[0] )
            IDs_with_mult_diag_refs_notes.append( 'Diagnosis : ' + str(list(df_xls_demographics[df_xls_demographics['Research ID']==id[0]]['Diagnosis'].values)) + ' ;;; Referral Source: ' + str(list(df_xls_demographics[df_xls_demographics['Research ID']==id[0]]['Referral Source'].values)) + ' ;;; Assessment ID: ' + str(list(df_xls_demographics[df_xls_demographics['Research ID']==id[0]]['Assessment ID'].values))  )
        
        # print('Multiple referral sources')
        
        if len(set(list(df_xls_demographics[df_xls_demographics['Research ID']==id[0]]['Referral Source'].values))) > 1:
            print('ID: ', id[0])
            print('Diagnosis : ', list(df_xls_demographics[df_xls_demographics['Research ID']==id[0]]['Diagnosis'].values))
            print('Referral Source: ', list(df_xls_demographics[df_xls_demographics['Research ID']==id[0]]['Referral Source'].values))
            print('Assessment ID: ', list(df_xls_demographics[df_xls_demographics['Research ID']==id[0]]['Assessment ID'].values))
            print()
            IDs_with_mult_diag_refs.append( id[0] )
            IDs_with_mult_diag_refs_notes.append( 'Diagnosis : ' + str(list(df_xls_demographics[df_xls_demographics['Research ID']==id[0]]['Diagnosis'].values)) + ' ;;; Referral Source: ' + str(list(df_xls_demographics[df_xls_demographics['Research ID']==id[0]]['Referral Source'].values)) + ' ;;; Assessment ID: ' + str(list(df_xls_demographics[df_xls_demographics['Research ID']==id[0]]['Assessment ID'].values))  )
    
    
    
    
    # df_IDs_with_mult_diag_refs = pd.DataFrame(np.transpose( np.array(( IDs_with_mult_diag_refs, IDs_with_mult_diag_refs_notes )) ), columns=['research_ID', 'notes'])
    # df_IDs_with_mult_diag_refs.to_csv(IDs_with_mult_diag_refs_path, index=False)
    # print('IDs with multiple diagnosis and referral sources are saved at: ', IDs_with_mult_diag_refs_path)
    
    
    
    ## Only update the CSV file if there are some new IDs with multiple diagnosis and referral sources in spreadsheet 
    
    df_IDs_with_mult_diag_refs_new = pd.DataFrame(np.transpose( np.array(( make_5_chars(IDs_with_mult_diag_refs), IDs_with_mult_diag_refs_notes )) ), columns=['research_ID', 'notes'])
    if os.path.exists( IDs_with_mult_diag_refs_path ):
        df_IDs_with_mult_diag_refs = pd.read_csv(IDs_with_mult_diag_refs_path)
        df_IDs_with_mult_diag_refs.research_ID = df_IDs_with_mult_diag_refs.research_ID.astype('str') 
        
        # diff = df_IDs_with_mult_diag_refs.compare(df_IDs_with_mult_diag_refs_new)
        if not df_IDs_with_mult_diag_refs.equals(df_IDs_with_mult_diag_refs_new):
            df_IDs_with_mult_diag_refs_new.to_csv(IDs_with_mult_diag_refs_path, index=False)
            print('IDs with multiple diagnosis and referral sources in spreadsheet are saved at: ', IDs_with_mult_diag_refs_path)
        else:
            print('No new IDs with multiple diagnosis and referral sources in spreadsheet are found. ')
            
    else:
        df_IDs_with_mult_diag_refs_new.to_csv(IDs_with_mult_diag_refs_path, index=False)
        print('IDs with multiple diagnosis and referral sources in spreadsheet are saved at: ', IDs_with_mult_diag_refs_path)
    
    
    sys.stdout.flush()
    
    
    
    # sys.stdout.flush()
    # time.sleep(100000000)
    
    
    
    '''
    Investigate according to the referral sources 
    '''
    
    for a_ref in list(set(list(df_xls_demographics['Referral Source'].values))):
        
    
        rID_ref = list(df_xls_demographics[df_xls_demographics['Referral Source'] == a_ref ]['Research ID'].values)
        
        ## this is what I got from the other script: converted_zip_r_ID_list, transcribed_zip_r_ID_list
        
        print('\n\n*** Referral Source: ', a_ref)
        print('Total number of IDs : ', len(rID_ref))
        print('Total number of unique IDs : ', len(set(rID_ref)))
        
        print('IDs for which we do not have any audio file: ', diff_list(rID_ref, converted_zip_r_ID_list) )
        
        print('IDs for which we do not have all audio files: ', diff_list(rID_ref, transcribed_zip_r_ID_list) )
        
    ###########################################################################
    ###########################################################################
    
    
    
    
    
    unique_converted_IDs = [i[0] for i in converted_ID_freq_dist]
    
    unique_transcribed_IDs = [i[0] for i in transcribed_ID_freq_dist]
    
    
    
    
    
    
    
    ## I am only taking the single first assessment for now 
    
    # ### These IDs are for testing 
    # unique_transcribed_IDs = [43214]
    # unique_converted_IDs = [20139]
    
    ## These IDs have multiple folders containing different json files. I needed to consider the mosrt updated one. 
    # unique_transcribed_IDs = [1474]
    # unique_transcribed_IDs = [58556]
    # unique_transcribed_IDs = [80270]
    # unique_transcribed_IDs = [1474, 58556, 80270]
    
    # ## These are the IDs I am testing for follow-up study 29/07/2024
    # # This one has multiple occurence 
    # unique_transcribed_IDs = [3479]
    # # This one has single occurence 30/07/2024
    # unique_transcribed_IDs = [13]
    # # Here, the first two have repeated occurences and the final two don't 
    # unique_transcribed_IDs = [3479, 47039, 13, 37408]
    # unique_transcribed_IDs = [43214]
    # unique_transcribed_IDs = [43214, 90271]
    
    ## Another ID which had multiple tests .... 
    # unique_transcribed_IDs = [90271]
    # unique_transcribed_IDs = [99214]
    
    
    
    ## These ones were the same ID for two different person, serious issue 
    # unique_transcribed_IDs = [11475]
    
    
    
    ZIP__r_IDs_4_final_dataset = []
    ZIP__file_IDs_4_final_dataset = []
    
    ZIP__r_IDs_mult_appearance = []
    ZIP__file_IDs_mult_appearance = []
    
    ZIP__gaps_mult_appearance = []
    
    
    '''
    This one is about taking all the IDs, but I found out many bugs ... 
    ID 20139 did not finish on first time but came back to complte 41 days later 
    '''
    
    # for i in natsorted( unique_converted_IDs ):
    #     occurnces = []
        
    #     for j in natsorted(converted_zip_file_ID_list): 
        
    #         if make_N_chars_a_val(i, 5)+'__' in j:
    #             occurnces.append( j )
        
    #     if len(occurnces) == 1:
    #         ZIP__r_IDs_4_final_dataset.append( i )
    #         ZIP__file_IDs_4_final_dataset.append( occurnces[0] )
        
    #     else: 
    #         day_diff = abs((get_date_4M_file( occurnces[-1] ) - get_date_4M_file( occurnces[0] )).days)
            
    #         if day_diff <= 1:
                
    #             if len(glob.glob(final_extract_dir+'/' + occurnces[-1]+'/*.wav')) == 0:
    #                 print('There are no wav files, INVESTIGATE.', i)
    #                 sys.stdout.flush()
    #                 time.sleep(100000000)
                
    #             else:
    #                 ZIP__r_IDs_4_final_dataset.append( i )
    #                 # ZIP__file_IDs_4_final_dataset.append( occurnces[0] )
    #                 ZIP__file_IDs_4_final_dataset.append( occurnces[-1] )
    #         else:
    #             print('The day difference is : ', day_diff , ' days.')
    #             print('ID: ', i)
    #             print('Occurences : ', occurnces )
    #             print()
                
    #             ZIP__r_IDs_4_final_dataset.append( i )
    #             ZIP__file_IDs_4_final_dataset.append( occurnces[0] )
                
                
                
    #             ZIP__r_IDs_mult_appearance.append( i )
    #             ZIP__file_IDs_mult_appearance.append( occurnces )
    
    
    
    '''
    This one is about using only those which answered all questions. 
    It works all the time ... 
    '''
    
    I need to make changes here and remove the special ID etc. 
    
    # I was working with only those which were transcribed .... 
    for i in natsorted( unique_transcribed_IDs ):
        
        occurnces = []
        
        for j in natsorted(transcribed_zip_file_ID_list): 
            
            if '_'+make_N_chars_a_val(i, 5)+'_' in j:
                occurnces.append( j )
        
        
        special_ID_found = 0
        
        ## First check if they appear in special IDs ... 
        for j in range(len(SPECIAL_IDs)):
            if i == int(SPECIAL_IDs[j][0]):
                ZIP__r_IDs_4_final_dataset.append( i )
                
                special_ID_found = 1
                
                o_found = 0
                
                for o in occurnces:
                    
                    if SPECIAL_IDs[j][1] in o:
                        ZIP__file_IDs_4_final_dataset.append( o )
                        # print('***special ID', i, ' is found in any occurences i.e. transcribed files', o )
                        o_found = 1 
                    
                if o_found != 1:
                    print('***special ID is not found in any occurences i.e. transcribed files', i, ' CHECK .... ' )
                    sys.stdout.flush()
                    time.sleep(100000000)
        
        
        
        if special_ID_found != 1:
           
            if len(occurnces) == 1:
                ZIP__r_IDs_4_final_dataset.append( i )
                ZIP__file_IDs_4_final_dataset.append( occurnces[0] )
            
            else: 
                day_diff = abs((get_date_4M_file( occurnces[-1] ) - get_date_4M_file( occurnces[0] )).days)
                
                if day_diff <= 1:
                    
                    if len(glob.glob(final_transcript_dir+'/' + occurnces[0]+'/*.wav')) > 2:
                        print('There are more than 2 wav files, INVESTIGATE.')
                        sys.stdout.flush()
                        time.sleep(100000000)
                    
                    if len(glob.glob(final_transcript_dir+'/' + occurnces[0]+'/*.mp3')) > 1:
                        print('There are more than 2 mp3 files, INVESTIGATE.')
                        sys.stdout.flush()
                        time.sleep(100000000)
                    
                    if os.path.getsize( glob.glob(final_transcript_dir+'/' + occurnces[0]+'/*.mp3')[0]) != os.path.getsize( glob.glob(final_transcript_dir+'/' + occurnces[0]+'/*.mp3')[0]) and os.path.getsize( glob.glob(final_transcript_dir+'/' + occurnces[0]+'/*.wav')[0]) != os.path.getsize( glob.glob(final_transcript_dir+'/' + occurnces[0]+'/*.wav')[0]) :
                        print('****** there is something wrong as two mp3 or wav files are not equal in size ********')
                        print('ID: ', i)
                        print('Occurences : ', occurnces )
                        sys.stdout.flush()
                        time.sleep(100000000)
                    else:
                        
                        
                        ## I am considering the json file which is the earliest and got maximum number of results 
                        if_max_len = 0
                        
                        len_json_results = 0
                        
                        len_diff = []
                        
                        for k in range(len(occurnces)-1):
                            len_diff.append( (len(get_json_content(extracted_data_dir + occurnces[k+1])['assessment']['artifact']['results']) - len(get_json_content(extracted_data_dir + occurnces[k])['assessment']['artifact']['results'])) )
                        
                        
                        if 0 in len_diff:
                            
                            indx_found = False
                            for x in range(len(len_diff)):
                                if len_diff[x] == 0:
                                    indx_found = x
                        else:
                            indx_found = len(occurnces) - 1
                        
                        ZIP__r_IDs_4_final_dataset.append( i )
                        ZIP__file_IDs_4_final_dataset.append( occurnces[indx_found] )
                        
                        
                else:
                    print('The day difference between the first and the final is : ', day_diff , ' days.')
                    print('ID: ', i)
                    print('Occurences : ', occurnces )
                    print()
                    
                    
                    ZIP__r_IDs_4_final_dataset.append( i )
                    ZIP__file_IDs_4_final_dataset.append( occurnces[0] )
                    
                    ZIP__r_IDs_mult_appearance.append( i )
                    # ZIP__file_IDs_mult_appearance.append( occurnces )
                    
                    
                    
                    ## Here, I am trying to calculate the gaps in days between occurences 
                    
                    # gap_lists = []
                    
                    # gap_lists.append(0)
                    # for o in range(len(occurnces)-1):
                    #     day_diff = abs((get_date_4M_file( occurnces[o+1] ) - get_date_4M_file( occurnces[o] )).days)
                    #     gap_lists.append( day_diff )
                    
                    # ZIP__gaps_mult_appearance.append( gap_lists )
                    
                    
                    
                    ## There are IDs: 43214 and 90271 who have many assessements. I need to fix those ... 
                    
                    l_days = [o.split('_')[2] for o in occurnces]
                    df_temp = pd.DataFrame( {'dates':l_days, 'occrs':occurnces} )
                    
                    # temp_ZIP__r_IDs_mult_appearance = []
                    temp_ZIP__file_IDs_mult_appearance = []
                    for a_date in natsorted(set(l_days)):
                        print(a_date)
                        temp_occrs = list(df_temp[df_temp.dates == a_date].occrs)
                        
                        
                        
                        if len(glob.glob(final_transcript_dir+'/' + temp_occrs[0]+'/*.wav')) > 2:
                            print('There are more than 2 wav files, INVESTIGATE.')
                            sys.stdout.flush()
                            time.sleep(100000000)
                        
                        if len(glob.glob(final_transcript_dir+'/' + temp_occrs[0]+'/*.mp3')) > 1:
                            print('There are more than 2 mp3 files, INVESTIGATE.')
                            sys.stdout.flush()
                            time.sleep(100000000)
                        
                        if os.path.getsize( glob.glob(final_transcript_dir+'/' + temp_occrs[0]+'/*.mp3')[0]) != os.path.getsize( glob.glob(final_transcript_dir+'/' + temp_occrs[0]+'/*.mp3')[0]) and os.path.getsize( glob.glob(final_transcript_dir+'/' + temp_occrs[0]+'/*.wav')[0]) != os.path.getsize( glob.glob(final_transcript_dir+'/' + temp_occrs[0]+'/*.wav')[0]) :
                            print('****** there is something wrong as two mp3 or wav files are not equal in size ********')
                            print('ID: ', i)
                            print('Occurences : ', temp_occrs )
                            sys.stdout.flush()
                            time.sleep(100000000)
                        else:
                            
                            
                            ## I am considering the json file which is the earliest and got maximum number of results 
                            if_max_len = 0
                            
                            len_json_results = 0
                            
                            len_diff = []
                            
                            for k in range(len(temp_occrs)-1):
                                len_diff.append( (len(get_json_content(extracted_data_dir + temp_occrs[k+1])['assessment']['artifact']['results']) - len(get_json_content(extracted_data_dir + temp_occrs[k])['assessment']['artifact']['results'])) )
                            
                            
                            if 0 in len_diff:
                                
                                indx_found = False
                                for x in range(len(len_diff)):
                                    if len_diff[x] == 0:
                                        indx_found = x
                            else:
                                indx_found = len(temp_occrs) - 1
                            
                            # ZIP__r_IDs_4_final_dataset.append( i )
                            # ZIP__file_IDs_4_final_dataset.append( temp_occrs[indx_found] )
                            
                            # temp_ZIP__r_IDs_mult_appearance.append( i )
                            temp_ZIP__file_IDs_mult_appearance.append( temp_occrs[indx_found] )
                    
                    
                    gap_lists = []
                    
                    gap_lists.append(0)
                    for o in range(len(temp_ZIP__file_IDs_mult_appearance)-1):
                        day_diff = abs((get_date_4M_file( temp_ZIP__file_IDs_mult_appearance[o+1] ) - get_date_4M_file( temp_ZIP__file_IDs_mult_appearance[o] )).days)
                        gap_lists.append( day_diff )
                    
                    
                    # ZIP__r_IDs_mult_appearance.append( temp_ZIP__r_IDs_mult_appearance )
                    ZIP__file_IDs_mult_appearance.append( temp_ZIP__file_IDs_mult_appearance )
                    ZIP__gaps_mult_appearance.append( gap_lists )
                    
    
    
    check_list_len(ZIP__r_IDs_mult_appearance, ZIP__file_IDs_mult_appearance)
    check_list_len(ZIP__r_IDs_mult_appearance, ZIP__gaps_mult_appearance)
    check_list_len(ZIP__gaps_mult_appearance, ZIP__file_IDs_mult_appearance)
    
    
    
    
    ## Find out the IDs which appears on both ZIPs and spreadsheet 
    
    FINAL_ZIP_SPRDSHT_IDs = natsorted(intersection(sprdsht_unique_research_IDs, ZIP__r_IDs_4_final_dataset))
    
    
    
    
    
    print('The total unique IDs in spreadsheet : ', len(sprdsht_unique_research_IDs))
    print('The total unique IDs in ZIPs : ', len(ZIP__r_IDs_4_final_dataset))
    
    print('The number of IDs appear in both speadsheet and ZIPs: ', len(FINAL_ZIP_SPRDSHT_IDs))
    
    
    IDs_sprsht_NTNzip = diff_list(sprdsht_unique_research_IDs, ZIP__r_IDs_4_final_dataset)
    print('The length of IDs appear in speadsheet but not in ZIPs: ', len( IDs_sprsht_NTNzip ))
    
    
    IDs_zip_NTNsprsht = diff_list(ZIP__r_IDs_4_final_dataset, sprdsht_unique_research_IDs)
    print('The length of IDs appear in ZIPs but not in speadsheet: ', len( IDs_zip_NTNsprsht ))
    
    # # This ID didn't have English language information 
    # FINAL_ZIP_SPRDSHT_IDs = [71681]
    # # This ID have English language information 
    # FINAL_ZIP_SPRDSHT_IDs = [8038]
    
    # # This ID has one appearance in the ZIP files, but multiple appearance in the spreadsheet 
    # FINAL_ZIP_SPRDSHT_IDs = [96543]
    
    ## This one was to investigate the PHQ, GAD, ED5D values ... 
    # FINAL_ZIP_SPRDSHT_IDs = [1474]
    # FINAL_ZIP_SPRDSHT_IDs = [22909]
    
    ## This one to investigate the IDs with missing answers 
    # FINAL_ZIP_SPRDSHT_IDs = [27899, 05921, 41762]
    
    
    ## Final test .... 
    # FINAL_ZIP_SPRDSHT_IDs = [71681, 8038, 96543, 1474, 655, 7115, 15637, 22909, 23794, 90271, 27899, 5921, 41762]
    
    # FINAL_ZIP_SPRDSHT_IDs = [90271]
    
    # FINAL_ZIP_SPRDSHT_IDs = [71681, 8038, 96543, 1474]
    
    # FINAL_ZIP_SPRDSHT_IDs = [95436,
    #  95500,
    #  95522,
    #  95543,
    #  95574,
    #  95673,
    #  95715,
    #  95941,
    #  96135,
    #  96316,
    #  96324,
    #  96342,
    #  96374,
    #  96543,
    #  96728,
    #  96927,
    #  97000,
    #  97240,
    #  97270,
    #  97391]
    
    ## These are the IDs I am testing for the new inforamtion added later ... 
    # FINAL_ZIP_SPRDSHT_IDs = [61708, 89591, 9207]
    
    
    # ## These are the IDs who have missing assess-ID in speadsheet 
    # FINAL_ZIP_SPRDSHT_IDs = [70344, 71134]
    
    
    ## These are the IDs I am excluding as I need to look into them later ... 
    
    # to_exclude_IDs = [20139] ## had issues with multiple appearnace. Came back to do the test after 41 days 
    to_exclude_IDs = [32882] ## had issues with multiple appearnace. Came back to do the test after 41 days 
    
    new_FINAL_ZIP_SPRDSHT_IDs = natsorted( diff_list(FINAL_ZIP_SPRDSHT_IDs, to_exclude_IDs) )
    
    
    
    
    '''
    There are some IDs which I needed to confirm their diagnosis status from Caitlin. 
    https://docs.google.com/spreadsheets/d/1NaYKrUmppTRx9DEOWR-25k-5DubyjnrTmqi6cUM-UHU/edit#gid=0
    
    Download a copy of the updated sheet 
    
    '''
    
    fixed_demographics_csv_file = '../data/Checking diagnosis and referral source - Sheet1.csv'
    
    df_fixed_demographics = pd.read_csv( fixed_demographics_csv_file )
    
    
    
    
    
    '''
    To add: SNR, MoCA, CogniTron etc. 
    '''
    
    both_json_sprdsht = ['diagnosis', 'referral', 'ethnicity', 'gender']
    # col_names = ['research_ID', 'assessment_ID', 'dir_name', 'assess_date', 'age'] + both_json_sprdsht + ['english'] + ['Q'+str(i) for i in list(range(1, 15))] + ['PHQ-9', 'GAD-7', 'EQ-5D', 'REPEAT', 'CONSENT']
    
    # col_names = ['research_ID', 'FirstName', 'LastName', 'BirthDay', 'NHS_No', 'Prac_email', 'telephone', 'assessment_ID', 'dir_name', 'assess_date', 'age'] + both_json_sprdsht + ['english'] + ['Q'+str(i) for i in list(range(1, 15))] + ['PHQ-9', 'GAD-7', 'EQ-5D', 'REPEAT', 'ASSESS_GAPS_days', 'CONSENT']
    
    col_names = ['research_ID', 'FirstName', 'LastName', 'BirthDay', 'NHS_No', 'Prac_email', 'telephone', 'assessment_ID', 'dir_name', 'assess_date', 'age'] + both_json_sprdsht + ['ENGLISH_FIRST_LANG', 'ENGLISH_ABILITY', 'FIRST_LANG', 'EDUCATION_INFO', 'REGION', 'OTHER_CONDITIONS'] + ['Q'+str(i) for i in list(range(1, 15))] + ['PHQ-9', 'GAD-7', 'EQ-5D', 'REPEAT', 'ASSESS_GAPS_days', 'CONSENT']
    
    
    LIST_r_IDs = []
    LIST_assessment_ID = []
    
    LIST_fName = []
    LIST_lName = []
    LIST_BDay = []
    LIST_NHSNo = []
    LIST_prac_email = []
    LIST_phone = []
    
    LIST_dir_names = []
    LIST_dates = []
    LIST_ages = []
    LIST_diagnosis = []
    LIST_referral = []
    LIST_ethnicity = []
    LIST_gender = []
    
    # LIST_english = []
    
    LIST_ENGLISH_FIRST_LANG = []
    LIST_ENGLISH_ABILITY = []
    LIST_FIRST_LANG = []
    LIST_EDUCATION_INFO = []
    LIST_REGION = []
    LIST_OTHER_COND_str = []
    
    
    
    for i in range(1,15): 
        exec("LIST_Q" + str(i) + " = []")
    
    
    LIST_PHQ_9 = []
    LIST_GAD_7 = []
    LIST_EQ5D = []
    LIST_repeat_info = []
    LIST_assess_gap_info = []
    LIST_consents = []
    
    
    
    avoided_IDs = []
    avoided_IDs_NOTEs = []
    
    # no_EQ5D_IDs = []
    # no_EQ5D_dates = []
    
    # n_NO_consent = 0
    n_NO_consent = []
    
    
    
    
    
    ## Multiple CPU 
    ##################################################
    
    # inputs = zip(new_FINAL_ZIP_SPRDSHT_IDs)
    
    
    final_ID_lists = []
    final_dir_names = []
    
    final_assess_gaps = []
    
    
    for an_ID in new_FINAL_ZIP_SPRDSHT_IDs:
        dir_name_lists = []
        assess_gap_lists = []
        
        if an_ID in ZIP__r_IDs_mult_appearance: 
        
            for i in range(len(ZIP__r_IDs_mult_appearance)):
                
                if an_ID == ZIP__r_IDs_mult_appearance[i]:
                    dir_name_lists.extend( ZIP__file_IDs_mult_appearance[i] ) 
                    assess_gap_lists.extend( ZIP__gaps_mult_appearance[i] )
        
        elif an_ID in ZIP__r_IDs_4_final_dataset: 
            for a_file in ZIP__file_IDs_4_final_dataset: 
                if '_'+make_N_chars_a_val(an_ID, 5)+'_' in a_file:
                    dir_name_lists.append(a_file)
                    assess_gap_lists.append( NO_EXIST_STR )
        
        
        final_dir_names.extend( dir_name_lists )
        final_ID_lists.extend( [an_ID]*len(dir_name_lists) )
        final_assess_gaps.extend( assess_gap_lists )
        
    check_list_len(final_ID_lists, final_dir_names)
    check_list_len(final_ID_lists, final_assess_gaps)
    check_list_len(final_assess_gaps, final_dir_names)
    
    
    
    inputs = zip(final_ID_lists, final_dir_names, final_assess_gaps)
    
    # n_jobs = min(N_jobs, len(new_FINAL_ZIP_SPRDSHT_IDs))
    n_jobs = min(N_jobs, len(final_ID_lists))
    print('n_jobs: ', n_jobs)
    sys.stdout.flush()
    
    
    
    # results = tqdm(Pool(n_jobs).imap_unordered(do_get_final_speadsheet_values, inputs), total=len(new_FINAL_ZIP_SPRDSHT_IDs))
    results = tqdm(Pool(n_jobs).imap_unordered(do_get_final_speadsheet_values, inputs), total=len(final_ID_lists))
    for result in results:
        
        if result[0] == True:
            LIST_r_IDs.append( result[2][0] )
            
            LIST_fName.append( result[2][1] )
            LIST_lName.append( result[2][2] )
            LIST_BDay.append( result[2][3] )
            LIST_NHSNo.append( result[2][4] )
            LIST_prac_email.append( result[2][5] )
            LIST_phone.append( result[2][6] )
            
            LIST_assessment_ID.append( result[2][7] )
            LIST_dir_names.append( result[2][8] )
            LIST_dates.append( result[2][9] )
            LIST_ages.append( result[2][10] ) 
            LIST_diagnosis.append( result[2][11] )
            LIST_referral.append( result[2][12] )
            LIST_ethnicity.append( result[2][13] )
            LIST_gender.append( result[2][14] )
            
            # LIST_english.append( result[2][15] )
            
            LIST_ENGLISH_FIRST_LANG.append( result[2][15] )
            LIST_ENGLISH_ABILITY.append( result[2][16] )
            LIST_FIRST_LANG.append( result[2][17] )
            LIST_EDUCATION_INFO.append( result[2][18] )
            LIST_REGION.append( result[2][19] )
            LIST_OTHER_COND_str.append( result[2][20] )
            
            
            
            for i in range(1,15): 
                exec( "LIST_Q" + str(i) + ".append({})".format( result[2][20+i] ) )
            audio_lens = []
            
            LIST_PHQ_9.append( result[2][35] )
            LIST_GAD_7.append( result[2][36] )
            LIST_EQ5D.append( result[2][37] )
            
            LIST_repeat_info.append( result[2][38] )
            LIST_assess_gap_info.append( result[2][39] )
            LIST_consents.append( result[2][40] )
        else:
            print('ID ', result[1], ' has NOT been added to the spreadsheet.')
            # avoided_IDs.append( result[1] )
            # avoided_IDs_NOTEs.append( result[4] )
            # print('result[4]: ', result[4] )
            # sys.stdout.flush()
            
            for i in result[4]:
                if i != '':
                    avoided_IDs.append( result[2][0] )
                    avoided_IDs_NOTEs.append( i )
            
        
        if result[3] == False:
            n_NO_consent.append( result[1] )
        
    ##################################################
    
    
    
    
    
    # print('avoided_IDs : ', avoided_IDs)
    # print('LIST_r_IDs : ', LIST_r_IDs)
    
    print('There are ', len(avoided_IDs), ' IDs were not added to the speadsheet.')
    
    # print('\n\n***** There are ', n_NO_consent, ' participants who did not provide consent to use their data. ******* \n\n')
    
    print('\n\n***** There are ', len(n_NO_consent), ' participants who did not provide consent to use their data. ******* \n\n')
    
    
    
    df_ID_issues = pd.DataFrame(np.transpose( np.array(( avoided_IDs, avoided_IDs_NOTEs )) ), columns=['research_ID', 'notes'])
    df_ID_issues = df_ID_issues.sort_values('research_ID')
    df_ID_issues.to_csv(ID_issues_path, index=False)
    print('The spreadsheet with IDs mismatching spreadsheet and json is saved at: ', ID_issues_path)
    sys.stdout.flush()
    
    exec_str = ''
    for i in range(1,15): 
        if i == 1:
            exec_str += "LIST_Q" + str(i)
        else:
            exec_str += ", LIST_Q" + str(i)
    
    if len(LIST_r_IDs) >=1:
        # exec("df_FINAL = pd.DataFrame(np.transpose( np.array((LIST_r_IDs, LIST_fName, LIST_lName, LIST_BDay, LIST_NHSNo, LIST_prac_email, LIST_phone, LIST_assessment_ID, LIST_dir_names, LIST_dates, LIST_ages, LIST_diagnosis, LIST_referral, LIST_ethnicity, LIST_gender, LIST_english, "+exec_str+", LIST_PHQ_9, LIST_GAD_7, LIST_EQ5D, LIST_repeat_info, LIST_assess_gap_info, LIST_consents )) ), columns=col_names)")
        exec("df_FINAL = pd.DataFrame(np.transpose( np.array((LIST_r_IDs, LIST_fName, LIST_lName, LIST_BDay, LIST_NHSNo, LIST_prac_email, LIST_phone, LIST_assessment_ID, LIST_dir_names, LIST_dates, LIST_ages, LIST_diagnosis, LIST_referral, LIST_ethnicity, LIST_gender, LIST_ENGLISH_FIRST_LANG, LIST_ENGLISH_ABILITY, LIST_FIRST_LANG, LIST_EDUCATION_INFO, LIST_REGION, LIST_OTHER_COND_str, "+exec_str+", LIST_PHQ_9, LIST_GAD_7, LIST_EQ5D, LIST_repeat_info, LIST_assess_gap_info, LIST_consents )) ), columns=col_names)")
        # df_FINAL = df_FINAL.sort_values('research_ID')
        # df_FINAL = df_FINAL.sort_values(['research_ID', 'ASSESS_GAPS_days'])
        df_FINAL = df_FINAL.sort_values(['research_ID', 'dir_name'])
        # df_FINAL.to_csv(final_metadata_path, index=False)
        # print('The final metadata spreadsheet is saved at: ', final_metadata_path)
        
        
    else:
        print('The list of values to populate the sheet is empty.')
    
    
    
    
    
    
    
    
    
    
    ### READ the troubled IDs which are saved in the previous step 2 
    
    df_fianl_list_incomplete_r_IDs = pd.read_csv( out_troubled_not_all_answers_IDs )
    df_IDs_sprsht_NTNzip = pd.read_csv( out_troubled_IDs_sprsht_NTNzip )
    df_IDs_zip_NTNsprsht = pd.read_csv( out_troubled_IDs_zip_NTNsprsht )
    
    
    
    fianl_list_incomplete_r_IDs = np.array(make_5_chars(list(df_fianl_list_incomplete_r_IDs['Not_all_answers'])))
    
    IDs_sprsht_NTNzip = np.array(make_5_chars(list(df_IDs_sprsht_NTNzip['IDs_sprsht_notTranscribed'])))
    
    IDs_zip_NTNsprsht = np.array(make_5_chars(list(df_IDs_zip_NTNsprsht['IDs_Transcribed_notsprsht'])))
    
    test_r_IDs = np.array(test_r_IDs)
    
    
    
    intersection(fianl_list_incomplete_r_IDs, IDs_sprsht_NTNzip)
    
    diff_list(fianl_list_incomplete_r_IDs, IDs_sprsht_NTNzip)
    
    diff_list( IDs_sprsht_NTNzip, fianl_list_incomplete_r_IDs )
    
    
    actual_incomplete_r_IDs = np.array(diff_list(fianl_list_incomplete_r_IDs, IDs_sprsht_NTNzip))
    
    
    
    data_N_all_ANSs = np.array(['N_all_ANSs']*(40*len(actual_incomplete_r_IDs))).reshape(len(actual_incomplete_r_IDs), (df_FINAL.shape[1]-1))
    
    data_SPRDSHT__NOT_TRANS = np.array(['SPRDSHT__NOT_TRANS']*(40*len(IDs_sprsht_NTNzip))).reshape(len(IDs_sprsht_NTNzip), (df_FINAL.shape[1]-1))
    
    data_TRANS__NOT_SPRDSHT = np.array(['TRANS__NOT_SPRDSHT']*(40*len(IDs_zip_NTNsprsht))).reshape(len(IDs_zip_NTNsprsht), (df_FINAL.shape[1]-1))
    
    data_TEST = np.array(['TEST_IDs']*(40*len(test_r_IDs))).reshape(len(test_r_IDs), (df_FINAL.shape[1]-1))
    
    
    
    
    
    
    
    
    
    # df_FINAL_FINAL = pd.concat([ df_FINAL, 
    #                             pd.DataFrame( np.concatenate([actual_incomplete_r_IDs.reshape(len(actual_incomplete_r_IDs), 1), data_N_all_ANSs], axis=1), columns=col_names), 
    #                             pd.DataFrame( np.concatenate([IDs_sprsht_NTNzip.reshape(len(IDs_sprsht_NTNzip), 1), data_SPRDSHT__NOT_TRANS], axis=1), columns=col_names), 
    #                             pd.DataFrame( np.concatenate([IDs_zip_NTNsprsht.reshape(len(IDs_zip_NTNsprsht), 1), data_TRANS__NOT_SPRDSHT], axis=1), columns=col_names), 
    #                             pd.DataFrame( np.concatenate([test_r_IDs.reshape(len(test_r_IDs), 1), data_TEST], axis=1), columns=col_names) ], axis=0)
    
    
    ## This step to generate pseudo IDs which are unique ... 
    df_FINAL_FINAL = pd.concat([ get_pseudo_IDs(df_FINAL, 1), 
                                get_pseudo_IDs(pd.DataFrame( np.concatenate([actual_incomplete_r_IDs.reshape(len(actual_incomplete_r_IDs), 1), data_N_all_ANSs], axis=1), columns=col_names), 1), 
                                get_pseudo_IDs(pd.DataFrame( np.concatenate([IDs_sprsht_NTNzip.reshape(len(IDs_sprsht_NTNzip), 1), data_SPRDSHT__NOT_TRANS], axis=1), columns=col_names), 1), 
                                get_pseudo_IDs(pd.DataFrame( np.concatenate([IDs_zip_NTNsprsht.reshape(len(IDs_zip_NTNsprsht), 1), data_TRANS__NOT_SPRDSHT], axis=1), columns=col_names), 1), 
                                get_pseudo_IDs(pd.DataFrame( np.concatenate([test_r_IDs.reshape(len(test_r_IDs), 1), data_TEST], axis=1), columns=col_names), 1) ], axis=0)
    
    
    
    
    
    # df_FINAL_FINAL_FINAL= get_pseudo_IDs(df_FINAL_FINAL, 1)
    # df_FINAL_FINAL_FINAL.to_csv(final_metadata_path, index=False)
    
    
    df_FINAL_FINAL = df_FINAL_FINAL.reset_index(drop=True)
    
    
    # ## This was to test that all the IDs appear only once in this spreadsheet ... 
    # len(set(df_FINAL['research_ID']))
    
    # len(df_FINAL['research_ID'])
    
    # ## This list should be empty 
    # find_values_counts(df_FINAL['research_ID'], 1)
    
    
    for an_id_row in SPECIAL_IDs_DIAGNOSIS: 
        
        print('Diagnosis before change : ')
        print(df_FINAL_FINAL[df_FINAL_FINAL.pseudo_unq_id == an_id_row[0]].diagnosis)
        
        df_FINAL_FINAL.loc[( df_FINAL_FINAL[df_FINAL_FINAL.pseudo_unq_id == an_id_row[0]].index.item(), 'diagnosis' )] = an_id_row[1]
        
        ## check that it has ben changed ...     
        print('Diagnosis AFTER change : ')
        print(df_FINAL_FINAL[df_FINAL_FINAL.pseudo_unq_id == an_id_row[0]].diagnosis)
    
    
    
    
    df_FINAL_FINAL.to_csv(final_metadata_path, index=False)
    
    print('The final metadata spreadsheet is saved at: ', final_metadata_path)
    
    
    
    
    
    
    
    
    
    
    ## This is checking the Dupliacted_ID_subject issue  
    
    col_2_check = ['FirstName', 'LastName', 'BirthDay', 'NHS_No']
    id_mismatch = []
    for col_n in col_2_check:
        # print('col_n : ', col_n)
        for an_id in natsorted(set(df_FINAL_FINAL.research_ID)):
            
            if len(set(df_FINAL_FINAL[df_FINAL_FINAL.research_ID == an_id][col_n]))>1:
                # print('ID: ', an_id)
                # print(list(df_FINAL_FINAL[df_FINAL_FINAL.research_ID == an_id][col_n]))
                id_mismatch.append( an_id )
        # print('***************')
    
    sorted_id_mismatches = natsorted(set(id_mismatch))
    
    # df_possible_mismatch = df_FINAL_FINAL[df_FINAL_FINAL.research_ID.isin(sorted_id_mismatches)][['research_ID'] + col_2_check + ['assessment_ID']]
    # df_possible_mismatch.to_csv(duplicated_ids_out, index=False)
    
    if_print = 0
    assess_to_show = []
    df_possible_mismatch_new = df_FINAL_FINAL[df_FINAL_FINAL.research_ID.isin(sorted_id_mismatches)][['research_ID'] + col_2_check + ['assessment_ID']]
    if os.path.exists( duplicated_ids_out ):
        df_possible_mismatch = pd.read_csv(duplicated_ids_out)
        
        if len(df_possible_mismatch.assessment_ID) < len(df_possible_mismatch_new.assessment_ID):
            assess_to_show = diff_list(df_possible_mismatch_new.assessment_ID, df_possible_mismatch.assessment_ID)
            df_possible_mismatch_new.to_csv(IDs_with_mult_diag_refs_path, index=False)
            print('Possible Dupliacted_ID_subject are saved at: ', duplicated_ids_out)
            if_print = 1
        else:
            # print('No new IDs with multiple diagnosis and referral sources in spreadsheet are found. ')
            print('No new IDs with possible duplicates are found.')
            
    else:
        df_possible_mismatch_new.to_csv(duplicated_ids_out, index=False)
        print('Possible Dupliacted_ID_subject are saved at: ', duplicated_ids_out)
        if_print = 1
        assess_to_show = natsorted(df_possible_mismatch_new.assessment_ID)
    
    
    if if_print == 1:
        print('The NEW dataframe which may contain dupliacted IDs are: (Ignore IDs: 19528) ')
        
        print(df_possible_mismatch_new[df_possible_mismatch_new.assessment_ID.isin(assess_to_show)])
        
    
    
    
    
    
    
    executionTime = (datetime.now() - startTime)
    current_time = datetime.now().strftime("%Y/%m/%d at %H:%M:%S")
    print('\n\nThe script completed at: ' + str(current_time))
    print('Execution time: ' + str(executionTime), ' \n\n')
    
    
    
    
    
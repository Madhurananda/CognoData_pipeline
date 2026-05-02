#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jun 23 16:51:31 2024

@author: madhupahar
"""

from main import *
from config import *
check_env('ACONDA')

from datetime import datetime, timedelta




if __name__=='__main__' and '__file__' in globals():

    
    # if len(sys.argv) < 2:
    #     print('\n\nPlease use : python CognoSpeak_2_data_process.py 15 [where 15 is the number of CPU]\n\n')
    #     sys.exit()
    
    # N_jobs = int(sys.argv[1])
    
    # if N_jobs >= cpu_count():
    #     print('The max no of CPU available : ', cpu_count())
    #     sys.exit("Lower the number of CPU\n\n")
    
    
    
    
    ct = datetime.now()
    
    df_metadata = get_metadata()
    
    df_metadata = df_metadata[(df_metadata.assessment_type == 'CognoSpeak Assessment') | (df_metadata.assessment_type == 'CognoMemory Assessment')]
    
    
    
    ## Delete the IDs which are to be removed in previous step 4 
    
    df_to_remove = pd.read_csv(ids_to_remove_out) 
    
    df_metadata = df_metadata[~df_metadata['research_ID'].isin(df_to_remove['ID_to_remove'])]
    df_metadata = df_metadata.reset_index(drop=True)
    
    df_duplicated_info = pd.read_csv(duplicates_FINAL_confirmed_out_FINAL)
    
    
    
    
    
    
    CHANGE_ID_from_to = []
    
    
    for i in range(len(df_duplicated_info)):
        
        
        CHANGE_ID_from_to.append( ( [int(i) for i in remove_item_list(df_duplicated_info.loc[i, "All_other_IDs"].replace('[', '').replace(']', '').replace('\'', '').replace(' ', '').split(','), str(df_duplicated_info.loc[i, "research_ID"]))], int(df_duplicated_info.loc[i, "research_ID"])   ) )
    
    ## Check that the lengths are same for both lists .... 
    
    # check_list_len(CHANGE_ID_from, CHANGE_ID_to)
    
    ## Change these IDs in the spreadsheets now ... 
    
    CHANGE_ID_to = []
    CHANGE_ID_from = []
    
    for i in CHANGE_ID_from_to:
        
        if len(i[0]) != 0:
            CHANGE_ID_to.append(i[1])
            CHANGE_ID_from.append( i[0] )
    
    
    check_list_len(CHANGE_ID_from, CHANGE_ID_to)
    
    print('There are originally ', len(df_duplicated_info), ' number of IDs in the duplicated summary sheet.')
    print('There will be only ', len(CHANGE_ID_to), ' no of IDs whose IDs will be changed. ')
    
    # df_metadata[df_metadata['research_ID'].isin(CHANGE_ID_from)]
    
    
    # df_duplicated_info[df_duplicated_info['research_ID'].isin(CHANGE_ID_to)]
    
    
    
    
    
    df_METADATA_FINAL = pd.DataFrame([], columns=df_metadata.columns.insert(1, 'Corrected_r_ID'))
    
    
    
    for ind in df_metadata.index:
        a_row = list(df_metadata.iloc[ind].values)
        
        to_insert_new = 0
        f_ind = 0
        for i in range(len(CHANGE_ID_from)): 
        
            for ID in CHANGE_ID_from[i]: 
                if df_metadata.iloc[ind]['research_ID'] == ID:
                    # print(ind)
                    to_insert_new = 1
                    f_ind = i
                # else:
                #     to_insert_new = 0
                    
        if to_insert_new == 1:
            a_row.insert(1, CHANGE_ID_to[f_ind])
        else:
            a_row.insert(1, df_metadata.iloc[ind]['research_ID'])
            
        df_METADATA_FINAL.loc[len(df_METADATA_FINAL.index)] = a_row
    
    
    ## This is the dataset which have new IDs as the corrected ones. 
    df_METADATA_FINAL_changed_IDs = df_METADATA_FINAL[df_METADATA_FINAL['research_ID'] != df_METADATA_FINAL['Corrected_r_ID']]
    
    
    
    # if len(df_METADATA_FINAL_changed_IDs[df_METADATA_FINAL_changed_IDs['REPEAT']!='NO']) > 0:
    #     print('This is a situation where dupliacted IDs appear multiple times. Needs checking .... ')
    #     print('The following IDs have follow-ups in the dupliacted df: ')
    #     print(df_METADATA_FINAL_changed_IDs[df_METADATA_FINAL_changed_IDs['REPEAT']!='NO'])
    #     # sys.stdout.flush()
    #     # time.sleep(100000000)
    
    
    
    
    # df_METADATA_FINAL = df_METADATA_FINAL.sort_values(['Corrected_r_ID', 'dir_name'])
    
    df_METADATA_FINAL = df_METADATA_FINAL.sort_values(['Corrected_r_ID', 'assess_date'])
    
    
    
    # df_METADATA_FINAL_changed_IDs[df_METADATA_FINAL_changed_IDs['REPEAT']=='NO']['dir_name']
    
    
    
    
    ## I need to split the dataframe into two sections: no_repeated and repeated ... 
    
    ID_repeats = [i[0] for i in find_values_counts(df_METADATA_FINAL['Corrected_r_ID'], 1)]
    
    
    df__FINAL_no_reap = df_METADATA_FINAL[~df_METADATA_FINAL['Corrected_r_ID'].isin(ID_repeats)]
    
    df__FINAL_reap = df_METADATA_FINAL[df_METADATA_FINAL['Corrected_r_ID'].isin(ID_repeats)]
    
    
    
    
    # ID_repeats = [3479]
    # ID_repeats = [3760]
    # ID_repeats = [5638]
    # ID_repeats = [90271]
    
    
    # df_NEW_FINAL_reap = pd.DataFrame([], columns=df__FINAL_reap.columns)
    df_NEW_FINAL_reap = pd.DataFrame([], columns=df__FINAL_reap.columns.insert(3, 'correct_pseudo_unq_id'))
    
    
    for an_id_reap in ID_repeats: 
        
        df_temp = df__FINAL_reap[df__FINAL_reap['Corrected_r_ID']==an_id_reap]
        
        
        
        df_temp = df_temp.sort_values('assess_date')
        df_temp = df_temp.reset_index(drop=True)
        
        
        
        # df_temp = df_temp.reset_index(drop=True)
        
        # if an_id_reap in CHANGE_ID_to:
        #     reap_info = str(list(df_temp['dir_name'])).replace('[', '').replace(']', '').replace('\'', '')
        # else:
        #     reap_info = list(df_temp['REPEAT'])[0].replace('[', '').replace(']', '').replace('\'', '')
        
        
        
        # reap_dates_vals = []
        
        # for a_date_ext in reap_info.split(','):
            
        #     reap_dates_vals.append( get_date_4M_file(a_date_ext) )
        
        
        # df_temp['temp_dates'] = reap_dates_vals
        # # df_temp.loc[:, 'temp_dates'] = reap_dates_vals
        
        # df_temp = df_temp.sort_values('temp_dates')
        
        # df_temp = df_temp.drop('temp_dates', axis=1)
        
        # df_temp = df_temp.reset_index(drop=True)
        
        
        
        gap_lists = []
        reap_dates_str = []
        
        gap_lists.append(0)
        reap_dates_str.append( df_temp['assess_date'][0] )
        for i in range(len(df_temp)-1):
            # day_diff = abs((get_date_4M_file( df_temp['dir_name'][i+1] ) - get_date_4M_file( df_temp['dir_name'][i] )).days)
            
            day_diff = abs((gen_the_date(df_temp['assess_date'][i+1].split('-')[2], df_temp['assess_date'][i+1].split('-')[1], df_temp['assess_date'][i+1].split('-')[0]) - gen_the_date(df_temp['assess_date'][i].split('-')[2], df_temp['assess_date'][i].split('-')[1], df_temp['assess_date'][i].split('-')[0])).days)
            
            gap_lists.append( day_diff )
            reap_dates_str.append( df_temp['assess_date'][i+1] )
        
        df_temp_new = df_temp.copy()
        
        
        df_temp_new['REPEAT'] = [reap_dates_str]*len(gap_lists)
        # df_temp_new['REPEAT'] = reap_dates_str
        df_temp_new['ASSESS_GAPS_days'] = gap_lists
        
        corr_IDs = list(set(df_temp_new['Corrected_r_ID']))
        
        if len(corr_IDs) > 1:
            print('This looks like a majot problem.')
            sys.stdout.flush()
            time.sleep(100000000)
        
        
        
        df_temp_new['correct_pseudo_unq_id'] = [make_N_chars_a_val(corr_IDs[0], 5)+'_'+str(x+1) for x in range(len(gap_lists)) ]
        
        df_NEW_FINAL_reap = pd.concat( [df_NEW_FINAL_reap, df_temp_new], axis=0 )
        
    
    
    # df_NEW_FINAL_reap.sort_values(['Corrected_r_ID', 'correct_pseudo_unq_id']).to_csv(sorted_follow_up_out, index=False)
    
    df_NEW_FINAL_reap.to_csv(sorted_follow_up_out, index=False)
    
    
    # df__FINAL_no_reap['correct_pseudo_unq_id'] = df__FINAL_no_reap['pseudo_unq_id']
    
    
    df__FINAL_no_reap.insert(3, 'correct_pseudo_unq_id', df__FINAL_no_reap['pseudo_unq_id'])
    
    # df_FINAL = pd.concat( [df__FINAL_no_reap, df_NEW_FINAL_reap], axis=0 ).sort_values(['Corrected_r_ID', 'dir_name'])
    
    df_FINAL = pd.concat( [df__FINAL_no_reap, df_NEW_FINAL_reap], axis=0 ).sort_values(['Corrected_r_ID', 'correct_pseudo_unq_id'])
    df_FINAL = df_FINAL.reset_index(drop=True)
    
    df_FINAL.to_csv(sorted_followUP_all_out, index=False)
    
    
    
    # I need to check the output with:
    #     IDs_with_mult_diag_refs_path = '../data/CognoSpeak_3__SPREADSHEET_diag_ref_mismatch.csv'
    
    
    
    # To do next: 
        
    #     1. Fix the pseudo IDs for duplicated IDs 
    #     2. Check those who has different diagnosis in the follow-up 
    
    
    
    '''
    Get information about the follow-ups 
    '''
    
    
    df_follow_up = pd.read_csv( sorted_follow_up_out )
    
    unique_IDs_follow_up = natsorted(set(df_follow_up.Corrected_r_ID))
    
    
    print('There are ', len(unique_IDs_follow_up), ' number of unique subjects who did a follow up study.')
    
    
    cols_2_consider = ['research_ID', 'Corrected_r_ID', 'correct_pseudo_unq_id', 'diagnosis', 'referral', 'ASSESS_GAPS_days']
    
    df_2_check_manually = pd.DataFrame([], columns=cols_2_consider+['CHECKED_Diagnosis', 'CHECKED_Referral', 'Comments'])
    
    
    
    ## diganosis mis-match
    
    for an_id in unique_IDs_follow_up:
        if len(set(df_follow_up[df_follow_up.Corrected_r_ID == an_id].diagnosis))>1 or len(set(df_follow_up[df_follow_up.Corrected_r_ID == an_id].referral))>1:
            print('ID : ', an_id)
            # print(set(df_follow_up[df_follow_up.Corrected_r_ID == an_id].diagnosis))
            print(df_follow_up[df_follow_up.Corrected_r_ID == an_id][cols_2_consider])
            print()
            df_temp = df_follow_up[df_follow_up.Corrected_r_ID == an_id][cols_2_consider]
            
            df_2_check_manually = pd.concat( [df_2_check_manually, df_temp], axis=0 )
            
    df_2_check_manually = df_2_check_manually.rename(columns={'research_ID': 'OLD_ID', 'Corrected_r_ID': 'checked_research_ID', 'correct_pseudo_unq_id':'checked_pseudo_unq_id'})
    
    
    
    ## I need to double check this list with Caitlin's MCI sheet ... The answers may be there already. I will not do this automatically, will do it manually  
    
    
    
    # df_2_check_manually.to_csv( to_check_follow_ups_out, index=False )
    
    
    
    
    # Next. I need to implement the structure where I read the entire csv and only save the new one if there are some changes. CognoSpeak_3 script might help me. 
    
    
    
    
    
    
    '''
    Then, manually check which IDs might have duplicated values .... 
    Open the file: '../data/CognoSpeak_5__follow_up_CHECK.csv' and add the NEW values into: 
        https://docs.google.com/spreadsheets/d/1i3YjXwwO5fyoWUHQNf3VSUZGy3ZzwYEuIIYKVT5Da5g/edit?pli=1&gid=1661823654#gid=1661823654
    
    Download it as a CSV file: 'follow_up_diagnosis_referral_CHECK - CognoSpeak_5__follow_up_CHECK.csv'
    
    '''
    
    df_manual_confirmed = pd.read_csv( '../data/follow_up_diagnosis_referral_CHECK - CognoSpeak_5__follow_up_CHECK.csv' )
    
    
    
    
    df_2_check_manually
    
    df_manual_confirmed
    
    
    len(set(df_2_check_manually.checked_pseudo_unq_id))
    
    len(set(df_manual_confirmed.checked_pseudo_unq_id))
    
    
    diff_list( list(df_2_check_manually['checked_pseudo_unq_id']), list(df_manual_confirmed['checked_pseudo_unq_id']))
    
    
    
    
    
    
    
    ## Check if the most recent pandas dataframe has some more IDs which are not already got sorted ... 
    
    to_save_manual_df = 0 
    if len(df_2_check_manually)> len(df_manual_confirmed):
        
        r_IDs_2_add = diff_list( list(df_2_check_manually['checked_pseudo_unq_id']), list(df_manual_confirmed['checked_pseudo_unq_id']))
        to_save_manual_df = 1
        
    
    ## Only save the manually confirmed one if it got extra IDs which are not already sorted out 
    if to_save_manual_df == 1:
        df_2_add = df_2_check_manually[df_2_check_manually['checked_pseudo_unq_id'].isin(r_IDs_2_add)]
        df_save_4_manual_check = pd.concat([df_manual_confirmed, df_2_add],ignore_index=True).sort_values(['checked_pseudo_unq_id'])
        df_save_4_manual_check.to_csv(to_check_follow_ups_out, index=False)
        df_manual_confirmed_FINAL = df_save_4_manual_check.copy()
    else:
        df_manual_confirmed_FINAL = df_manual_confirmed.copy()
    
    
    
    
    
    # ## Checking the intersection between Cailtin's MCI sheet and the mis-matched ones here ... 
    
    # df_caitlin_MCI = pd.read_csv( '../data/Israac Data Spreadsheets (Clean) - All Results.csv' )[:52]
    
    # intersection( list(df_caitlin_MCI['Research number']), list(df_save_4_manual_check.OLD_ID) )
    
    # intersection( list(df_caitlin_MCI['Research number']), list(df_save_4_manual_check.checked_research_ID) )
    
    
    
    
    
    ## Next, update the metadata with the manually checked information 
    
    change_consider_cols = [['diagnosis', 'CHECKED_Diagnosis'], ['referral', 'CHECKED_Referral']]
    
    
    
    for an_id in df_manual_confirmed_FINAL.checked_pseudo_unq_id:
        
        df_temp = df_manual_confirmed_FINAL[df_manual_confirmed_FINAL.checked_pseudo_unq_id == an_id]
        df_temp = df_temp[df_temp['CHECKED_Diagnosis'].notna()]
        
        # if an_id == '47039_1':
        #     print(df_temp.CHECKED_Diagnosis)
        #     print(df_temp.CHECKED_Referral)
        
        for a_col_vals in change_consider_cols:
            
            
            # print(a_col_vals[0], ' before change : ')
            # print(df_FINAL[df_FINAL.correct_pseudo_unq_id == an_id][a_col_vals[0]].values[0])
            
            
            
            
            
            if len(df_temp) > 0:
                
                if len(df_temp[a_col_vals[1]]) > 1:
                    print('There should be only one value for this ID for the CHECKED', a_col_vals[0], ' : ', an_id)
                    sys.stdout.flush()
                    time.sleep(100000000)
                
                df_FINAL.loc[( df_FINAL[df_FINAL.correct_pseudo_unq_id == an_id].index.item(), a_col_vals[0] )] = list(df_temp[a_col_vals[1]])[0]
                
                # if an_id == '47039_1':
                    
                #     print('the value is : ', list(df_temp[a_col_vals[1]])[0])
                
                
            
            # ## check that it has ben changed ...     
            # print(a_col_vals[0], ' AFTER change : ')
            # print(df_FINAL[df_FINAL.correct_pseudo_unq_id == an_id][a_col_vals[0]])
    
    
    
    # df_FINAL[df_FINAL.Corrected_r_ID == 23893].diagnosis
    
    
    # df_FINAL[df_FINAL.correct_pseudo_unq_id == '47039_1'].diagnosis
    
    
    
    df_FINAL = df_FINAL.rename(columns={'research_ID': 'OLD_r_ID', 'pseudo_unq_id': 'OLD_pseudo_unq_id'})
    df_FINAL = df_FINAL.rename(columns={'Corrected_r_ID': 'research_ID', 'correct_pseudo_unq_id': 'pseudo_unq_id'})
    
    
    
    ## Now, Read the Stroke and MND metadata, add two missing columns and merge with CognoSpeak data 
    
    df_meta_Stroke_MND = pd.read_csv(temp_ST_MND_save_out)
    
    df_meta_Stroke_MND.insert(0, 'OLD_r_ID', df_meta_Stroke_MND.research_ID)
    df_meta_Stroke_MND.insert(2, 'OLD_pseudo_unq_id', df_meta_Stroke_MND.pseudo_unq_id)
    
    
    df_FINAL = pd.concat([df_FINAL, df_meta_Stroke_MND], ignore_index=True, sort=False)
    
    
    df_FINAL.to_csv(final_sorted_CognoSpeak_metadata, index=False)
    
    
    
    
    
    # ## Prepare the version which can be shared with others without personal information 
    # df_FINAL_2_SHARE = df_FINAL.drop(['OLD_r_ID', 'OLD_pseudo_unq_id', 'BirthDay', 'NHS_No', 'Prac_email', 'telephone', 'assessment_ID'], axis=1)
    # df_FINAL_2_SHARE.to_csv( final_metadata_2_share, index=False )
    
    
    
    
    executionTime = (datetime.now() - startTime)
    current_time = datetime.now().strftime("%Y/%m/%d at %H:%M:%S")
    print('\n\nThe script completed at: ' + str(current_time))
    print('Execution time: ' + str(executionTime), ' \n\n')
    
    
    
    
    
    
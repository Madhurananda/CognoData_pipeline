#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jun 12 11:20:20 2024

@author: madhupahar
"""



from main import *
from config import *
check_env('ACONDA')




'''
Here, I am considering two IDs as automatic duplictes only if NHS No, practioaner email telephone and birthday are the same ... 
'''
def find_values_4_duplicates(unique_NHS_no, col_name, df_duplicated_info, df_not_matched):
    
    print('\n\n****** Start For Column : ', col_name)
    for a_nhs in unique_NHS_no: 
        a_nhs_df = df_metadata[ df_metadata[col_name]==a_nhs[0] ]
        
        if len(set(a_nhs_df.NHS_No)) > 1 or len(set(a_nhs_df.Prac_email)) > 1 or len(set(a_nhs_df.telephone)) > 1 or len(set(a_nhs_df.BirthDay)) > 1 or len(set(a_nhs_df.FirstName)) > 1 or len(set(a_nhs_df.LastName)) > 1:
            # print('-----------')
            # print(a_nhs_df)
            # print('-----------')
            df_not_matched = pd.concat([df_not_matched, a_nhs_df])
        else:
            # df_duplicated_info = pd.concat([df_duplicated_info, pd.DataFrame(data=[ (list(a_nhs_df.research_ID)[0], list(a_nhs_df.research_ID))], columns=['final_ID', 'All_IDs']) ])
            
            
            to_NOT_add = 0
            for i in range(len(df_duplicated_info)):
                # print(df_duplicated_info.loc[i, "All_IDs"])
                if list(a_nhs_df.research_ID)[0] in df_duplicated_info.loc[i, "All_other_IDs"]:
                    print('The final ID : ', list(a_nhs_df.research_ID)[0], ' with all IDs : ' , list(a_nhs_df.research_ID), ' already exists in ', df_duplicated_info.loc[i, "All_other_IDs"])
                    to_NOT_add = 1
                    
            if to_NOT_add != 1:
                df_duplicated_info = pd.concat([df_duplicated_info, pd.DataFrame(data=[ (list(a_nhs_df.research_ID)[0], list(a_nhs_df.research_ID), list(a_nhs_df.assess_date), 'checked by script')], columns=['research_ID', 'All_other_IDs', 'All_assess_dates', 'Comments']) ])
                
                
        df_not_matched.reset_index(drop=True, inplace=True)
        df_duplicated_info.reset_index(drop=True, inplace=True)
    
    print('End For Column : ', col_name, ' \n\n****** ')
    
    return df_duplicated_info, df_not_matched


def get_a_val(a_col):
    # vals = [int(i) for i in set(df_manual_confirmed[df_manual_confirmed['Final_r_ID'] == an_uqn_ID][a_col])]
    
    if len(set(df_manual_confirmed[df_manual_confirmed['Final_r_ID'] == an_uqn_ID][a_col])) == 1:
    
        vals = list(set(df_manual_confirmed[df_manual_confirmed['Final_r_ID'] == an_uqn_ID][a_col]))
    else:
        vals = list(df_manual_confirmed[df_manual_confirmed['Final_r_ID'] == an_uqn_ID][a_col])
        
    
    vals = remove_item_list(vals, '')
    
    # print('vals : ', vals)
    
    if len(vals) == 0:
        set_val = ''
    else:
        if a_col == 'NHS_No':
            vals = [int(i) for i in vals ]
        
        if len(vals) == 1:
            set_val = vals[0]
        else:
            set_val = vals
    
    return set_val



def get_list_4RM_values(vals):
    all_ids_list = []
    all_ids_list_appended = []
    
    for i in vals:
        if type(i) is list:
            all_ids_list.extend( i )
            all_ids_list_appended.append( i )
        elif type(i) is int:
            all_ids_list.extend( [i] )
            all_ids_list_appended.append( [i] )
        elif type(i) is str:
            all_ids_list.extend( [i] )
            all_ids_list_appended.append( [i] )
    return all_ids_list, all_ids_list_appended


def prune_sort(vals):
    f_val = ''
    if len(vals) == 1:
        f_val = vals[0]
    else:
        f_val = vals
    return f_val


def find_mult_OccRnce(df):
    
    all_ids_list, all_ids_list_appended = get_list_4RM_values(list( df['All_other_IDs'] ))
    
    multi_IDs = find_values_counts(all_ids_list, 1)
    
    final_inds = []
    
    for a_id in multi_IDs: 
        
        final_inds_temp = []
        
        for i in range(len(all_ids_list_appended)):
            
            if type(all_ids_list_appended[i]) is list:
            
                if a_id[0] in all_ids_list_appended[i]:
                    final_inds_temp.append( i )
            elif type(all_ids_list_appended[i]) is int:
            
                if a_id[0] == all_ids_list_appended[i]:
                    final_inds_temp.append( i )
        
        if not final_inds_temp in final_inds:
        
            final_inds.append( final_inds_temp )
            
    return final_inds


if __name__=='__main__' and '__file__' in globals():

    
    # if len(sys.argv) < 2:
    #     print('\n\nPlease use : python CognoSpeak_2_data_process.py 15 [where 15 is the number of CPU]\n\n')
    #     sys.exit()
    
    # N_jobs = int(sys.argv[1])
    
    # if N_jobs >= cpu_count():
    #     print('The max no of CPU available : ', cpu_count())
    #     sys.exit("Lower the number of CPU\n\n")
    
    
    '''
    There are two types of duplications: 
        
        1. Duplicated_subject_ID: this is when the subject is assigned to multiple IDs. (the following should work.)
        
        
        2. Dupliacted_ID_subject: this is when the same ID is assigned to multiple subjects. Same IDs are assigned to multiple subjects. I need to find them while I am doing Follow-up Study (It should be in CognoSpeak_3.py under "IDs_with_mult_diag_refs_path", but more thorough search sould be done later using the JSON files.)
        
        
    '''
    
    
    
    
    ct = datetime.now()
    
    df_metadata = get_metadata()
    
    
    time.sleep(2)
    
    
    
    ## This is the metadata which I will merge later ... 
    df_meta_Stroke_MND = df_metadata[~((df_metadata.assessment_type == 'CognoSpeak Assessment') | (df_metadata.assessment_type == 'CognoMemory Assessment'))]
    df_meta_Stroke_MND.to_csv(temp_ST_MND_save_out, index=False)
    
    
    ## This is the metadata which will be used for checking follow ups and duplicates ... 
    df_metadata = df_metadata[(df_metadata.assessment_type == 'CognoSpeak Assessment') | (df_metadata.assessment_type == 'CognoMemory Assessment')]
    
    
    
    df_metadata = df_metadata.drop_duplicates(subset=['research_ID'])
    df_metadata = df_metadata.reset_index(drop=True)
    
    
    
    # df_metadata = df_metadata[ ['research_ID', 'NHS_No', 'Prac_email', 'telephone', 'BirthDay', 'FirstName', 'LastName', 'assess_date'] ]
    df_metadata = df_metadata[ ['research_ID', 'NHS_No', 'Prac_email', 'telephone', 'BirthDay', 'FirstName', 'LastName', 'assess_date', 'age', 'diagnosis', 'assessment_type'] ]
    df_metadata['FirstName'] = df_metadata['FirstName'].str.upper()
    df_metadata['LastName'] = df_metadata['LastName'].str.upper()
    
    
    '''
    The order of checking duplicates .... 
    1. NHS_No 
    2. Prac_email
    3. telephone
    4. BirthDay
    5. FirstName
    6. LastName
    '''
    
    unique_NHS_no = find_values_counts( df_metadata[df_metadata['NHS_No'].notna()]['NHS_No'] , 1)
    
    unique_email_no = find_values_counts(df_metadata['Prac_email'], 1)
    
    unique_phone_no = find_values_counts( df_metadata[df_metadata['telephone'].notna()]['telephone'] , 1)
    
    unique_bDay = find_values_counts(df_metadata['BirthDay'], 1)
    
    unique_fNames = find_values_counts(df_metadata['FirstName'], 1)
    
    unique_lNames = find_values_counts(df_metadata['LastName'], 1)
    
    
    
    
    
    df_duplicated_info = pd.DataFrame(data=[], columns=['research_ID', 'All_other_IDs', 'All_assess_dates', 'Comments'])
    
    df_not_matched = pd.DataFrame(data=[], columns=list(df_metadata.columns) + ['Comments'])
    
    
    
    df_duplicated_info, df_not_matched = find_values_4_duplicates( unique_NHS_no, 'NHS_No', df_duplicated_info, df_not_matched)
    
    df_duplicated_info, df_not_matched = find_values_4_duplicates( unique_email_no, 'Prac_email', df_duplicated_info, df_not_matched)
    
    df_duplicated_info, df_not_matched = find_values_4_duplicates( unique_phone_no, 'telephone', df_duplicated_info, df_not_matched)
    
    
    
    
    
    df_auto_checked_duplicated = df_metadata.merge(df_duplicated_info, on='research_ID', how='inner')
    
    df_auto_checked_duplicated = df_auto_checked_duplicated.drop(['assess_date'], axis=1)
    df_auto_checked_duplicated = df_auto_checked_duplicated.fillna('')
    
    df_2_check_manually = df_not_matched.drop_duplicates(keep='first')
    df_2_check_manually = df_2_check_manually.fillna('')
    
    
    # ## Now, save these to CSV files ... 
    
    # Save the auto confirmed CSV anyway  .... 
    df_auto_checked_duplicated.to_csv(duplicates_confirmed_out, index=False)
    
    ## Only save the manually confirmed one if it got extra IDs which are not already sorted out 
    # df_2_check_manually.to_csv(duplicates_TO_confirm_out, index=False)
    
    
    
    
    
    '''
    Then, manually check which IDs might have duplicated values .... 
    Open the file: '../data/CognoSpeak_4__duplicates_TO_BE_confirmed.csv' and add the NEW values into: 
        https://docs.google.com/spreadsheets/d/1CY3CQhsybI2jwR2fhGyXsEyjcU1ScoiSB2x0CHzau7o/edit?gid=1962030411#gid=1962030411
    
    Download it as 'CognoSpeak_4__duplicates_TO_BE_confirmed - duplicates_TO_BE_confirmed.csv'
    
    '''
    
    df_manual_confirmed = pd.read_csv( '../data/CognoSpeak_4__duplicates_TO_BE_confirmed - duplicates_TO_BE_confirmed.csv' )
    
    
    ## Find out those who needs to be removed ... 
    to_remove_IDs = natsorted(df_manual_confirmed[df_manual_confirmed['Final_r_ID'] == 'remove']['research_ID'])
    
    data = {'ID_to_remove':to_remove_IDs}
    
    df_to_remove = pd.DataFrame(data)
    
    df_to_remove.to_csv( ids_to_remove_out , index=False)
    
    
    
    ## Check if the most recent pandas dataframe has some more IDs which are not already got sorted ... 
    
    
    to_save_manual_df = 0 
    if len(df_2_check_manually)> len(df_manual_confirmed):
        
        # r_IDs_2_add = diff_list( diff_list( list(df_2_check_manually['research_ID']), list(df_manual_confirmed['research_ID'])), to_remove_IDs)
        r_IDs_2_add = diff_list( list(df_2_check_manually['research_ID']), diff_list( list(df_manual_confirmed['research_ID']), to_remove_IDs))
        to_save_manual_df = 1
    
    ## Only save the manually confirmed one if it got extra IDs which are not already sorted out 
    if to_save_manual_df == 1:
        df_2_add = df_2_check_manually[df_2_check_manually['research_ID'].isin(r_IDs_2_add)]
        df_save_4_manual_check = pd.concat([df_manual_confirmed, df_2_add],ignore_index=True)
        df_save_4_manual_check.to_csv(duplicates_TO_confirm_out, index=False)
    
    
    
    
    
    # if len(intersection( list(df_manual_confirmed[df_manual_confirmed['Final_r_ID'] == 'remove']['research_ID']), list(df_metadata['research_ID']) )) > 0:
    #     print('These IDs are to be removed. Add them as the test IDs in CognoSpeak_2_data_process.py and then run Step 2, 3 and 4 (this one) again ... ', natsorted(df_manual_confirmed[df_manual_confirmed['Final_r_ID'] == 'remove']['research_ID']))
        
    #     sys.stdout.flush()
    #     time.sleep(100000000)
    
    
    
    df_manual_confirmed = df_manual_confirmed[df_manual_confirmed['Final_r_ID'] != 'remove']
    
    df_manual_confirmed = df_manual_confirmed.fillna('')
    
    
    
    df_cross_checked = pd.DataFrame(data=[], columns=df_auto_checked_duplicated.columns)
    
    for an_uqn_ID in natsorted(set(df_manual_confirmed['Final_r_ID'])):
        
        # a_row = [an_uqn_ID, get_a_val('NHS_No'), get_a_val('Prac_email'), get_a_val('telephone'), get_a_val('BirthDay'), get_a_val('FirstName'), get_a_val('LastName'), get_a_val('research_ID'), get_a_val('assess_date'), 'cross-checked manually']
        
        a_row = [an_uqn_ID, get_a_val('NHS_No'), get_a_val('Prac_email'), get_a_val('telephone'), get_a_val('BirthDay'), get_a_val('FirstName'), get_a_val('LastName'), get_a_val('age'), get_a_val('diagnosis'), get_a_val('assessment_type'), get_a_val('research_ID'), get_a_val('assess_date'), 'cross-checked manually']
        
        df_cross_checked.loc[len(df_cross_checked.index)] = a_row
        
        
    
    df_cross_checked.research_ID = df_cross_checked.research_ID.astype(int)
    
    df_FINAL_duplicated = pd.concat([df_auto_checked_duplicated, df_cross_checked],ignore_index=True)
    
    df_FINAL_duplicated = df_FINAL_duplicated.sort_values('research_ID')
    
    df_FINAL_duplicated = df_FINAL_duplicated.reset_index(drop=True)
    
    ## Finally, save the combined CSV with both automatically and manually checked IDs ... 
    df_FINAL_duplicated.to_csv(duplicates_FINAL_confirmed_out, index=False)
    
    
    
    
    
    

    
    
    '''
    There is an issue of the same ID is appearing multiple times connected to different IDs. It needing sorted ... 
    '''
    
    
    
    
    ## First, remover the same ID appearing on a single row ...
    
    df_FINAL_duplicated['All_other_IDs'] = [list(set(x)) if type(x) is list else x for x in list(df_FINAL_duplicated['All_other_IDs']) ]
    
    
    ## Then, get the indexes where an ID appears multiple times ... 
    final_inds = find_mult_OccRnce( df_FINAL_duplicated )
    
    
    
    df_FINAL_duplicated_FINAL = df_FINAL_duplicated.copy()
    
    ## Remove those idices from the df
    x, _ = get_list_4RM_values(final_inds)
    df_FINAL_duplicated_FINAL = df_FINAL_duplicated_FINAL.drop(index=x)
    df_FINAL_duplicated_FINAL = df_FINAL_duplicated_FINAL.reset_index(drop=True)
    
    
    
    
    ## Then, calculate the combined row and append it to the df ... 
    for a_dupl_set in final_inds:
        
        df_duplt = [] 
        for i in a_dupl_set:
            df_temp = df_FINAL_duplicated.iloc[[i]]
            
            if len(df_duplt) == 0:
                df_duplt = df_temp
            else:
                df_duplt = pd.concat([df_duplt, df_temp],ignore_index=True)
            
        
        
        final_row = []
        
        for a_col in df_duplt.columns:
            if a_col == 'research_ID':
                final_row.append( min(df_duplt[a_col]) )
            else:
                
                values = list(df_duplt[a_col])
                
                if type(values) is list:
                    
                    final_row.append( prune_sort(natsorted(set(get_list_4RM_values(values)[0]))) )
                elif type(values) is int:
                    final_row.append( prune_sort(natsorted(set(values))) )
                
                
                
        df_FINAL_duplicated_FINAL.loc[len(df_FINAL_duplicated_FINAL.index)] = final_row
    
    
    df_FINAL_duplicated_FINAL = df_FINAL_duplicated_FINAL.sort_values('research_ID')
    
    df_FINAL_duplicated_FINAL = df_FINAL_duplicated_FINAL.reset_index(drop=True)
    
    df_FINAL_duplicated_FINAL.to_csv(duplicates_FINAL_confirmed_out_FINAL, index=False)
    
    
    ####### Do the check again to make sure that all the duplicate issues are fixed .... 
    
    
    final_inds = find_mult_OccRnce( df_FINAL_duplicated_FINAL )
    
    
    
    
    if len(final_inds) > 0:
        print('****** There are still some duplacted issues. Needing fix .... ')
        print('The indexes are: ', final_inds)
        print('Find them in: ', duplicates_FINAL_confirmed_out_FINAL)
        sys.stdout.flush()
        time.sleep(100000000)
    
    
    
    
    
    
    
    
    
    executionTime = (datetime.now() - startTime)
    current_time = datetime.now().strftime("%Y/%m/%d at %H:%M:%S")
    print('\n\nThe script completed at: ' + str(current_time))
    print('Execution time: ' + str(executionTime), ' \n\n')
    
    
    
    
    
    
    
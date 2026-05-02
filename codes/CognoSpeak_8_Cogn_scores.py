#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jun  4 14:59:52 2024

@author: madhupahar
"""




from config import *



def get_Nmatched_MoCA_dfs(df):
    
    df = df.reset_index(drop=True)
    
    col_4_sum = df_MoCA_ISRAAC.columns
    col_4_sum = remove_item_list(col_4_sum, 'research_ID')
    col_4_sum = remove_item_list(col_4_sum, 'pseudo_unq_id')
    col_4_sum = remove_item_list(col_4_sum, 'Timestamp')
    col_4_sum = remove_item_list(col_4_sum, 'MoCA Total score')
    
    # col_4_sum = ['Visuospatial / Executive',
    #  'Naming',
    #  'Attention',
    #  'Language',
    #  'Abstraction',
    #  'Delayed Recall',
    #  'Orientation',
    #  'Total score']
    
    
    
    # cmd = 'df_MoCA_test = df['
    
    tot = 0
    
    for i in col_4_sum: 
        # cmd += 'df[\'' + i + '\'] + '
        
        tot += df[i]
        
        
    # cmd = cmd[0:len(cmd)-2] + ' != df[\'MoCA Total score\']] '
    
    # exec(cmd)
    
    df_new = df.copy()
    
    df_new['Sum_Total'] = tot
    
    ## Those whose running totals are more than provided total or provided totals are more than 1 than the running totals ... 
    
    df_Nmatched = df_new[ (abs(df['MoCA Total score'] - df_new['Sum_Total']) > 1) | (df_new['Sum_Total'] > df['MoCA Total score']) ]
    
    
    return df_Nmatched


def check_dupliacted_timestamos(df):
    if len(df[df['Research ID'].isin([x[0] for x in find_values_counts( df['Research ID'], 1 )])]) != len(df[df['Research ID'].isin([x[0] for x in find_values_counts( df['Research ID'], 1 )])].drop_duplicates(subset="Timestamp", keep='first')):
        
        print('It seems that there is same "Timestamp" for an reseach ID. Investigate ...  ')
        sys.stdout.flush()
        time.sleep(100000000)




def get_Nmatched_COGN_dfs(df, cog_type):
    
    df = df.reset_index(drop=True)
    
    col_4_sum = df.columns
    col_4_sum = remove_item_list(col_4_sum, 'research_ID')
    col_4_sum = remove_item_list(col_4_sum, 'pseudo_unq_id')
    col_4_sum = remove_item_list(col_4_sum, 'Timestamp')
    
    if cog_type == 'RUDAS':
        col_4_sum = remove_item_list(col_4_sum, 'RUDAS Total score')
        col_4_sum = remove_item_list(col_4_sum, 'RUDAS reason_4_missing_question')
        col_4_sum = remove_item_list(col_4_sum, 'RUDAS list of animals')
    elif cog_type == 'MCE':
        col_4_sum = remove_item_list(col_4_sum, 'MCE Total Score')
        col_4_sum = remove_item_list(col_4_sum, 'MCE reason_4_missing_question')
        col_4_sum = remove_item_list(col_4_sum, 'MCE supermarket items')
    elif cog_type == 'ACE':
        col_4_sum = remove_item_list(col_4_sum, 'ACE Total')
        col_4_sum = remove_item_list(col_4_sum, 'ACE P fluency')
        col_4_sum = remove_item_list(col_4_sum, 'ACE animal fluency')
        col_4_sum = remove_item_list(col_4_sum, 'ACE reason_4_missing_question')
    else:
        print('There is something very wrong ... ')
        sys.stdout.flush()
        time.sleep(100000000)
        
    
    
    tot = 0
    for i in col_4_sum: 
        tot += df[i]
    
    df_new = df.copy()
    df_new['Sum_Total'] = tot
    
    
    if cog_type == 'RUDAS':
        df_Nmatched = df_new[ (df_new['Sum_Total'] != df['RUDAS Total score']) ]
    elif cog_type == 'MCE':
        df_Nmatched = df_new[ (df_new['Sum_Total'] != df['MCE Total Score']) ]
    elif cog_type == 'ACE':
        df_Nmatched = df_new[ (df_new['Sum_Total'] != df['ACE Total']) ]
    else:
        print('There is something very wrong ... ')
        sys.stdout.flush()
        time.sleep(100000000)
    
    
    
    return df_Nmatched





if __name__=='__main__' and '__file__' in globals():
    
    
    
    # if len(sys.argv) < 2:
    #     print('\n\n Please use : python CognoSpeak_3_check_final.py 15 [where 15 is the number of CPU]\n\n')
    #     sys.exit()
    
    # # startTime = datetime.now()
    # # current_time = startTime.strftime("%Y/%m/%d at %H:%M:%S")
    # # print('\n\nThe script starting at: ' + str(current_time), ' \n\n' )
    
    # N_jobs = int(sys.argv[1])
    
    # if N_jobs >= cpu_count():
    #     print('The max no of CPU available : ', cpu_count())
    #     sys.exit("Lower the number of CPU\n\n")
    
    
    
    '''
    I need to do this sanity checking, as actaul cogntive score is uploaded to the CcHAT spreadsheet in bulk, 
    and I am matching the assessments for each ID by the order, not the time 
    '''
    
    check_dupliacted_timestamos( df_MoCA )
    check_dupliacted_timestamos( df_RUDAS )
    check_dupliacted_timestamos( df_MCE )
    check_dupliacted_timestamos( df_ACE_III )
    
    
    
    
    
    '''
    Reading the spreadsheet which was generated at the previous step ... 
    '''
    
    df_metadata = pd.read_csv( transcript_metadata_out )
    
    
    
    '''
    ###########################################################################
    ###########################################################################
    I am just checking the MoCA scores here .... 
    ###########################################################################
    ###########################################################################
    '''
    
    '''
    THERE ARE SOME ISSEUS WHILE ADDING UP THE MOCA SCORES THE TOTAL SCORES DO NOT match
    
    I NEED TO FIND A FIX FOR THAT. 
    
    THE SPEADSHEET IS BEING UPDATED BY CAITLIN 
    
    https://docs.google.com/spreadsheets/d/1arydmDqrcGNSdMosRokMzbV0bZAcOKc7PeKKc3JeKWw/edit?gid=1716922336#gid=1716922336
    
    
    This file has to be replaced as "no_match_MoCA_scores_spreadshet - no_match_MoCA_scores_spreadshet.csv"
    '''
    
    '''
    I have to disregard the IDs which have nan 
    This is because the total scores are calcualted regardless of any missing values; as Caitlin is looking into the MoCA thresholds only to find out if someone belongs to case or control (with MoCA cut off 26) 
    '''
    
    
    '''
    STEP 1: First, take the scores from our big spreadsheet .... 
    '''
    
    
    ## Fix the mis-typed research-IDs
    df_MoCA = df_MoCA.reset_index(drop=True)
    df_MoCA.loc[( df_MoCA[df_MoCA['Research ID'] == 726760].index.item(), 'Research ID' )] = 72760
    
    
    
    col_2_consider = ['Visuospatial / Executive', 'Naming', 'Attention', 'Language', 'Abstraction', 'Delayed Recall', 'Orientation', 'Total score', 'For the verbal fluency test, please list all the words that the patient stated during the task. ', 'Memory Index Score', 'How many years did the participant spend in full-time education? ']
    
    # df_MoCA_dataOverview = pd.read_excel(xls_file, sheet_name='MoCa')
    # df_MoCA_dataOverview = df_MoCA_dataOverview[df_MoCA_dataOverview.columns.intersection(['Research ID', 'Timestamp']+col_2_consider)]
    
    df_MoCA_dataOverview = df_MoCA[df_MoCA.columns.intersection(['Research ID', 'Timestamp']+col_2_consider)]
    
    # df_MoCA_dataOverview = df_MoCA_dataOverview.dropna()
    df_MoCA_dataOverview = df_MoCA_dataOverview.dropna(subset=['Research ID'])
    
    
    
    ## Change the columns so that two spreadsheet match each other .... 
    # cmd = "df_MoCA_dataOverview.rename(columns={'oldName1': 'newName1', 'oldName2': 'newName2'}, inplace=True)"
    
    df_MoCA_dataOverview.rename(columns={'For the verbal fluency test, please list all the words that the patient stated during the task. ': 'words list', 'How many years did the participant spend in full-time education? ': 'years of education'}, inplace=True)
    
    cmd = 'df_MoCA_dataOverview.rename(columns={'
    
    for i in diff_list(list(df_MoCA_dataOverview.columns), ['Research ID', 'Timestamp']):
    # for i in col_2_consider:
        
        cmd += '\'' + i + '\': \'MoCA '+ i + '\', '
    
    cmd = cmd[0:len(cmd)-2] + '}, inplace=True)'
    
    exec(cmd)
    
    
    df_MoCA_dataOverview.rename(columns={'Research ID': 'research_ID'}, inplace=True)
    df_MoCA_dataOverview.research_ID = df_MoCA_dataOverview.research_ID.astype(int)
    
    
    
    ##### I need to check the changed research ID in the follow ups in here ...
    
    df_metadata[df_metadata.OLD_r_ID != df_metadata.research_ID][['OLD_r_ID', 'research_ID']]
    
    df1 = df_MoCA_dataOverview.copy().reset_index(drop=True)
    df2 = df_metadata[df_metadata.OLD_r_ID != df_metadata.research_ID][['OLD_r_ID', 'research_ID']].reset_index(drop=True)
    
    
    list_new_rID = []
    
    for ind in df1.index:
        
        t_r_id = df1['research_ID'][ind]
        
        if t_r_id in list(df2.OLD_r_ID):
            # print(t_r_id)
            # print(set(df2[df2.OLD_r_ID == t_r_id].research_ID))
            
            t_llsT  = list(set(df2[df2.OLD_r_ID == t_r_id].research_ID))
            
            if len(t_llsT) != 1:
                
                print('The length is not 1 , check ... ')
                print(t_r_id)
                print(set(df2[df2.OLD_r_ID == t_r_id].research_ID))
                
                sys.stdout.flush()
                time.sleep(100000000)
            
            new_r_id = int(t_llsT[0])
            
        else:
            new_r_id = t_r_id
        
        list_new_rID.append( new_r_id )
    
    
    df1.insert(2, 'new_r_ID', list_new_rID)
    
    df_MoCA_dataOverview = df1.rename(columns={'research_ID': 'OLD_ID', 'new_r_ID': 'research_ID'})
    
    
    
    
    
    # find_values_counts(df_MoCA_dataOverview['research_ID'], 1)
    
    
    mult_r_IDS_spreadsheet = [i[0] for i in find_values_counts(df_MoCA_dataOverview['research_ID'], 1)]
    
    
    
    
    r_IDS_spreadsheet = natsorted(set(df_MoCA_dataOverview['research_ID']))
    
    
    ## I need to sort the MoCA socres dataframe so that I can match them with my metadata 
    
    df_MoCA_dataOverview = df_MoCA_dataOverview.sort_values(by=["research_ID", "Timestamp"])
    
    '''
    I can assign some pseudo_unq_id as the order of the MoCA tests will correspond to the CognoSpeak tests as well ... 
    '''
    
    df_MoCA_dataOverview = get_pseudo_IDs(df_MoCA_dataOverview, 1, 'Timestamp').sort_values(by=["research_ID", "pseudo_unq_id"])
    
    
    
    
    
    '''
    STEP 2: Then, consider the MoCA scores from Caitlin's ISRAAC sheet .... 
    '''
    
    
    ## Download the Excel file: https://docs.google.com/spreadsheets/d/1zVZfQaRoqI0d8vZW3qVFZTxwOcGKaLm3iqn76IUAeio/edit?gid=2078686059#gid=2078686059
    
    ## This is the newer version of the previous sheet: https://docs.google.com/spreadsheets/d/1gep8mauzIvz9jiLgj7Auzd5JFkMaCAQaLDx0jwIkL7Y/edit?gid=2078686059#gid=2078686059
    ## This one includes all the ethnic monority data, not just the ISRACC ones 
    
    
    
    df_MoCA_ISRAAC = pd.read_excel('../data/Israac Data Spreadsheets (Clean).xlsx', sheet_name='All Results')
    
    
    
    df_MoCA_ISRAAC = df_MoCA_ISRAAC[df_MoCA_ISRAAC.columns.intersection(['Research number']+['MoCA '+i for i in col_2_consider])]
    
    df_MoCA_ISRAAC = df_MoCA_ISRAAC[df_MoCA_ISRAAC['Research number'].notna()]
    
    df_MoCA_ISRAAC = df_MoCA_ISRAAC.dropna()
    
    df_MoCA_ISRAAC.rename(columns={'Research number': 'research_ID'}, inplace=True)
    
    df_MoCA_ISRAAC.research_ID = df_MoCA_ISRAAC.research_ID.astype(int)
    
    
    
    if len(find_values_counts(df_MoCA_ISRAAC['research_ID'], 1)) > 0:
        print('caitlin ISRAAC should not have any follow-ups.')
        print('check what went wrong ... ')
        sys.stdout.flush()
        time.sleep(100000000)
    
    
    
    df_MoCA_ISRAAC = get_pseudo_IDs(df_MoCA_ISRAAC, 0, '')
    
    
    
    r_IDS_ISRAAC = natsorted(set(df_MoCA_ISRAAC['research_ID']))
    
    
    
    ## There are no follow-ups so nothing has been done for ISRAAC 
    
    
    
    
    if len( intersection( mult_r_IDS_spreadsheet, r_IDS_ISRAAC ) ) > 0:
        print('IDs which appear in Caitlin-ISRAAC file only once, appear multiple times on the spreadsheet. As there are no date in Caitlin-ISRAAC, this will be an issue.')
        sys.stdout.flush()
        time.sleep(100000000)
    
    
    
    ## ISRAAC dataframe organised by Caitlin does not have any timestamps as there are only one appearnace of each subject 
    
    '''
    df_MoCA_dataOverview.columns
    Out[1158]: 
    Index(['Timestamp', 'research_ID', 'MoCA Visuospatial / Executive',
           'MoCA Naming', 'MoCA Attention', 'MoCA Language', 'MoCA Abstraction',
           'MoCA Delayed Recall', 'MoCA Orientation', 'MoCA Total score'],
          dtype='object')
    
    
    df_MoCA_ISRAAC.columns
    Out[1159]: 
    Index(['research_ID', 'MoCA Visuospatial / Executive', 'MoCA Naming',
           'MoCA Attention', 'MoCA Language', 'MoCA Abstraction',
           'MoCA Delayed Recall', 'MoCA Orientation', 'MoCA Total score'],
          dtype='object')
    
    '''
    
    
    
    '''
    Next, check the IDs for which the MoCA scores do not match ... 
    These are shared with Caitlin and saved in 
    https://drive.google.com/drive/folders/1GShbN90CDspUqcxO45oShOYzyo6MkDnP
    '''
    
    
    # df_Nmatched_MoCA = get_Nmatched_MoCA_dfs(df_MoCA_ISRAAC)
    
    df_Nmatched_SPRDSHT = get_Nmatched_MoCA_dfs(df_MoCA_dataOverview)
    df_Nmatched_SPRDSHT = df_Nmatched_SPRDSHT.merge(df_metadata[['pseudo_unq_id', 'assessment_type']], on='pseudo_unq_id', how='inner')
    
    
    
    
    
    ## Read the CSV file which is updated by Caitlin here (https://docs.google.com/spreadsheets/d/1arydmDqrcGNSdMosRokMzbV0bZAcOKc7PeKKc3JeKWw/edit?gid=1716922336#gid=1716922336)
    
    df_manually_updated = pd.read_csv( '../data/no_match_MoCA_scores_spreadshet - no_match_MoCA_scores_spreadshet.csv' )
    df_manually_updated = df_manually_updated[~df_manually_updated.Timestamp.isna()]
    df_manually_updated.research_ID = df_manually_updated.research_ID.astype(int)
    
    # df_manually_updated = df_manually_updated.merge(df_metadata[['pseudo_unq_id', 'assessment_type']], on='pseudo_unq_id', how='inner')
    
    
    df_misT_manual_updated = df_Nmatched_SPRDSHT[df_Nmatched_SPRDSHT.OLD_ID.isin( diff_list(df_manually_updated.research_ID, df_Nmatched_SPRDSHT.research_ID) )][['pseudo_unq_id', 'OLD_ID', 'research_ID']]
    
    
    if len(df_misT_manual_updated) > 0:
        
        print('The following IDs from the Google sheet (manual update MoCA) have changed.')
        print('Please change the OLD_ID to research_ID and correspoinding pseudo_unq_id on the sheet and redownload it as a CSV file and run this script again ... ')
        print(df_misT_manual_updated)
        sys.stdout.flush()
        time.sleep(100000000)
    
    
    
    
    if len(df_manually_updated) > df_manually_updated.To_ADD.isnull().sum():
        df_manually_updated.To_ADD = df_manually_updated.To_ADD.str.upper()
    
    
    ## If there are any other input than 'yes' and 'no', raise an issue ... 
    
    if len(df_manually_updated.To_ADD.value_counts()) > 2:
        print('There are other inputs than YES or NO. Check the online speadsheet ... ')
        sys.stdout.flush()
        time.sleep(100000000)
        
        
    # ## I need to do this one only once after adding new columns ... 
    # df_temp = df_manually_updated[['research_ID']].merge(df_Nmatched_SPRDSHT, on=['research_ID'], how='inner')[['research_ID', 'pseudo_unq_id', 'MoCA words list', 'MoCA Memory Index Score', 'MoCA years of education']]
    
    # df_temp.to_csv( '../data/temp.csv', index=False )
    
    
    
    ## Check if the most recent pandas dataframe has some more IDs which are not already got sorted ... 
    
    
    
    
    
    to_save_manual_df = 0 
    r_IDs_2_add = diff_list( list(df_Nmatched_SPRDSHT['pseudo_unq_id']), list(df_manually_updated['pseudo_unq_id']))
    if len(r_IDs_2_add)> 0:
        to_save_manual_df = 1
    
    ## Only save the manually confirmed one if it got extra IDs which are not already sorted out 
    if to_save_manual_df == 1:
        # df_2_add = df_Nmatched_SPRDSHT[df_Nmatched_SPRDSHT['research_ID'].isin(r_IDs_2_add)].drop(ext_MoCA_cols, axis=1)
        df_2_add = df_Nmatched_SPRDSHT[df_Nmatched_SPRDSHT['pseudo_unq_id'].isin(r_IDs_2_add)]
        df_save_4_manual_check = pd.concat([df_manually_updated, df_2_add],ignore_index=True)
        df_save_4_manual_check.to_csv(MoCA_out_n_matched_spreadshet, index=False)
    
    
    
    
    ## As I will not be using the old_r_ID, it's better to drop it now ... 
    
    df_MoCA_dataOverview = df_MoCA_dataOverview.drop(['OLD_ID'], axis=1)
    
    
    
    
    
    '''
    After having a discussion with Caitlin, I realised that I will take the ISRAAC values first as a preference as she cross-checked those. 
    Then, the remaining ones I will take from the spreadsheet. 
    
    I initially thought about merging the df, but not applicable here .... 
    
    '''
    
    
    
    print('No. of intesection between spreadsheet and ISRAAC: ', len(intersection( r_IDS_spreadsheet, r_IDS_ISRAAC )))
    
    
    print('IDs which appear in spreadsheet but not in ISRAAC: ')
    len(diff_list(r_IDS_spreadsheet, r_IDS_ISRAAC))
    
    print('IDs which appear in ISRAAC but not in spreadsheet: ')
    diff_list( r_IDS_ISRAAC, r_IDS_spreadsheet )
    
    
    
    
    
    
    ## This is the IDs for all MoCA
    
    r_ID_MoCA = natsorted(set( r_IDS_ISRAAC + r_IDS_spreadsheet ))
    
    print('There are altogether ', len( r_ID_MoCA ), ' unique IDs who have MoCA scores.')
    
    
    
    ## I need to delete those IDs which needs to be manually confirmed 
    r_ID_MoCA = natsorted(set(diff_list(r_ID_MoCA, df_Nmatched_SPRDSHT.research_ID)))
    
    print('After ignoring to-be-manually-confirmed IDs, there are altogether ', len( r_ID_MoCA ), ' unique IDs who have MoCA scores.')
    
    
    
    '''
    I have two dataframes: ISRAAC and the speadhsheet:
        df_MoCA_ISRAAC (Constant)
        df_MoCA_dataOverview (Keeps changing from time to time)
    I need to consider the ISRAAC ones first and then the remaining ones from the spreadsheet 
    '''
    
    
    ## Add some columns to ISTRAAC dataframe 
    ext_MoCA_cols = ['MoCA words list', 'MoCA Memory Index Score', 'MoCA years of education']
    for a_col in ext_MoCA_cols:
        df_MoCA_ISRAAC.insert(len(df_MoCA_ISRAAC.columns), a_col, ['']*len(df_MoCA_ISRAAC))
    
    ## Drop a col in spreadsheet dataframe 
    df_MoCA_dataOverview = df_MoCA_dataOverview.drop('Timestamp', axis=1)
    
    ## Drop the "still to be confirmed dataframe"
    df_MoCA_ISRAAC = df_MoCA_ISRAAC[~df_MoCA_ISRAAC.pseudo_unq_id.isin(df_Nmatched_SPRDSHT.pseudo_unq_id)]
    df_MoCA_dataOverview = df_MoCA_dataOverview[~df_MoCA_dataOverview.pseudo_unq_id.isin(df_Nmatched_SPRDSHT.pseudo_unq_id)]
    
    
    df_MoCA_final = pd.concat([df_MoCA_ISRAAC, df_MoCA_dataOverview[~df_MoCA_dataOverview.pseudo_unq_id.isin(df_MoCA_ISRAAC.pseudo_unq_id)]], ignore_index=True, sort=False)
    
    
    
    df_manually_updated_sel = df_manually_updated[df_manually_updated['To_ADD']=='YES']
    
    
    print('MoCA: These research IDs are not added as still waiting for manual check: ', list(df_manually_updated[df_manually_updated['To_ADD']!='YES']['research_ID']))
    
    df_MoCA_final = pd.concat([df_MoCA_final, df_manually_updated_sel[df_MoCA_final.columns ]], ignore_index=True, sort=False)
    
    
    df_MoCA_final.research_ID = df_MoCA_final.research_ID.astype(int)
    
    
    df_MoCA_final = df_MoCA_final.sort_values(['research_ID', 'pseudo_unq_id'])
    
    
    
    
    
    
    
    
    
    
    print('There are', len(intersection(df_metadata.research_ID, df_MoCA_final.research_ID)), ' IDs between the metadata and MoCA.')
    
    
    # find_values_counts( intersection(df_metadata.research_ID, df_MoCA_final.research_ID), 1 )
    
    
    
    
    print('The number of IDs which are among the metadata but do not appear among the MoCA scores : ')
    print(len((diff_list( df_metadata.research_ID, df_MoCA_final.research_ID ))))
    
    
    
    print('The number of IDs which are among the MoCA scores but do not appear among the metadata: ')
    print(len((diff_list(df_MoCA_final.research_ID, df_metadata.research_ID))))
    print(natsorted(set(diff_list(df_MoCA_final.research_ID, df_metadata.research_ID))))
    
    
    
    ## Prepare and save the MoCA scores along with the metadata 
    
    df_all_metadata_MoCA = df_metadata.merge(df_MoCA_final, on=['pseudo_unq_id', 'research_ID'], how='left')
    
    df_all_MoCA_metadata = df_metadata.merge(df_MoCA_final, on=['pseudo_unq_id', 'research_ID'], how='right')
    
    df_metadata_MoCA = df_metadata.merge(df_MoCA_final, on=['pseudo_unq_id', 'research_ID'], how='inner')
    
    
    
    # df_all_metadata_MoCA.to_csv( MoCA_out_all_moca, index=False )
    
    df_all_MoCA_metadata.to_csv( MoCA_out_all_metadta, index=False )
    
    df_metadata_MoCA.to_csv( MoCA_out_moca_metadata, index=False )
    
    
    
    
    
    
    
    
    
    
    
    '''
    ## Use this CSV file to convert MoCA to MMSE: 
        ## https://docs.google.com/spreadsheets/d/1L4aJIDRGtFe-ZD3KWojgFcqYwCo6V-StR_N7DzWMcm8/edit?gid=105218023#gid=105218023
    ## '../data/Challenge ideas - MoCA2MMSE.csv'
    '''
    
    
    
    
    
    '''
    ###########################################################################
    ###########################################################################
    Now I am working with RUDAS .... 
    ###########################################################################
    ###########################################################################
    '''
    
    ## Fix the mis-typed research-IDs
    df_RUDAS = df_RUDAS.reset_index(drop=True)
    df_RUDAS.loc[( df_RUDAS[df_RUDAS['Research ID'] == 586965].index.item(), 'Research ID' )] = 58696
    
    
    
    df_RUDAS_dataOverview = df_RUDAS.dropna(subset=['Research ID'])
    
    
    
    ## Change the columns so that two spreadsheet match each other ....
    df_RUDAS_dataOverview.rename(columns={'If any questions were missed, please provide a reason. ': 'reason_4_missing_question', 'Please write a list of all the animals that the participant named during the animal naming task. ': 'list of animals'}, inplace=True)
    
    
    col_2_consider = df_RUDAS_dataOverview.columns
    
    
    cmd = 'df_RUDAS_dataOverview.rename(columns={'
    
    for i in diff_list(list(df_RUDAS_dataOverview.columns), ['Research ID', 'Timestamp']):
        
        cmd += '\'' + i + '\': \'RUDAS '+ i + '\', '
    
    cmd = cmd[0:len(cmd)-2] + '}, inplace=True)'
    
    exec(cmd)
    
    
    
    df_RUDAS_dataOverview.rename(columns={'Research ID': 'research_ID'}, inplace=True)
    df_RUDAS_dataOverview.research_ID = df_RUDAS_dataOverview.research_ID.astype(int)
    
    
    
    
    ## I need to sort the RUDAS socres dataframe so that I can match them with my metadata 
    
    df_RUDAS_dataOverview = df_RUDAS_dataOverview.sort_values(by=["research_ID", "Timestamp"])
    
    '''
    I can assign some pseudo_unq_id as the order of the MoCA tests will correspond to the CognoSpeak tests as well ... 
    '''
    
    df_RUDAS_dataOverview = get_pseudo_IDs(df_RUDAS_dataOverview, 1, 'Timestamp').sort_values(by=["research_ID", "pseudo_unq_id"])
    
    
    
    ### Next, I need to check if there are any mismatches in the RUDAS scores ... 
    
    df_Nmatched_RUDAS = get_Nmatched_COGN_dfs(df_RUDAS_dataOverview, 'RUDAS')
    
    # ## Only needing done at the beginnin ... 
    # df_Nmatched_RUDAS.to_csv( '../data/no_match_RUDAS_scores.csv', index=False )
    
    
    
    ## Read the CSV file which is updated by Caitlin/Dora here (https://docs.google.com/spreadsheets/d/1tbqVyKX28WJwLHh9bbfppLj3db7vcb3uxgOTMpXsWGM/edit?gid=88759952#gid=88759952)
    
    df_manually_updated = pd.read_csv( '../data/no_match_RUDAS_scores - no_match_RUDAS_scores.csv' )
    df_manually_updated = df_manually_updated[~df_manually_updated.Timestamp.isna()]
    
    df_manually_updated.research_ID = df_manually_updated.research_ID.astype(int)
    if len(df_manually_updated) > df_manually_updated.To_ADD.isnull().sum():
        df_manually_updated.To_ADD = df_manually_updated.To_ADD.str.upper()
    
    
    ## If there are any other input than 'yes' and 'no', raise an issue ... 
    
    if len(df_manually_updated.To_ADD.value_counts()) > 2:
        print('There are other inputs than YES or NO. Check the online speadsheet ... ')
        sys.stdout.flush()
        time.sleep(100000000)
        
    
    
    ## Check if the most recent pandas dataframe has some more IDs which are not already got sorted ... 
    
    to_save_manual_df = 0 
    if len(df_Nmatched_RUDAS)> len(df_manually_updated):
        
        r_IDs_2_add = diff_list( list(df_Nmatched_RUDAS['pseudo_unq_id']), list(df_manually_updated['pseudo_unq_id']))
        to_save_manual_df = 1
    
    ## Only save the manually confirmed one if it got extra IDs which are not already sorted out 
    if to_save_manual_df == 1:
        df_2_add = df_Nmatched_SPRDSHT[df_Nmatched_SPRDSHT['pseudo_unq_id'].isin(r_IDs_2_add)]
        df_save_4_manual_check = pd.concat([df_manually_updated, df_2_add],ignore_index=True)
        df_save_4_manual_check.to_csv(RUDAS_out_n_matched_spreadshet, index=False)
    
    
    
    
    ## Drop a col in spreadsheet dataframe 
    df_RUDAS_dataOverview = df_RUDAS_dataOverview.drop('Timestamp', axis=1)
    
    
    ## Drop the "still to be confirmed dataframe"
    df_RUDAS_dataOverview = df_RUDAS_dataOverview[~df_RUDAS_dataOverview.pseudo_unq_id.isin(df_Nmatched_RUDAS.pseudo_unq_id)]
    
    
    
    df_manually_updated_sel = df_manually_updated[df_manually_updated['To_ADD']=='YES']
    
    print('RUDAS: These research IDs are not added as still waiting for manual check: ', list(df_manually_updated[df_manually_updated['To_ADD']!='YES']['research_ID']))
    
    df_RUDAS_final = pd.concat([df_RUDAS_dataOverview, df_manually_updated_sel[df_RUDAS_dataOverview.columns ]], ignore_index=True, sort=False)
    
    df_RUDAS_final.research_ID = df_RUDAS_final.research_ID.astype(int)
    df_RUDAS_final = df_RUDAS_final.sort_values(['research_ID', 'pseudo_unq_id'])
    
    
    
    ## Prepare and save the RUDAS scores along with the metadata 
    
    df_all_metadata_RUDAS = df_all_metadata_MoCA.merge(df_RUDAS_final, on=['pseudo_unq_id', 'research_ID'], how='left')
    df_all_RUDAS_metadata = df_metadata.merge(df_RUDAS_final, on=['pseudo_unq_id', 'research_ID'], how='right')
    df_metadata_RUDAS = df_metadata.merge(df_RUDAS_final, on=['pseudo_unq_id', 'research_ID'], how='inner')
    
    
    # df_all_metadata_RUDAS.to_csv( RUDAS_out_all_RUDAS, index=False )
    df_all_RUDAS_metadata.to_csv( RUDAS_out_all_metadta, index=False )
    df_metadata_RUDAS.to_csv( RUDAS_out_RUDAS_metadata, index=False )
    
    
    
    
    
    
    
    
    
    '''
    ###########################################################################
    ###########################################################################
    Now I am working with  MCE 
    ###########################################################################
    ###########################################################################
    '''
    
    
    
    # ## Fix the mis-typed research-IDs
    # df_MCE = df_MCE.reset_index(drop=True)
    # df_MCE.loc[( df_MCE[df_MCE['Research ID'] == 586965].index.item(), 'Research ID' )] = 58696
    
    ## I will be getting the RFUDAS scores seperately, not from this MCE sheet ... 
    df_MCE_dataOverview = df_MCE.drop(['RUDAS'], axis=1)
    
    df_MCE_dataOverview = df_MCE.dropna(subset=['Research ID'])
    
    ## Change the columns so that two spreadsheet match each other ....
    df_MCE_dataOverview.rename(columns={'If any questions were missed, please provide a reason. ': 'reason_4_missing_question', 'What supermarket "things" did the participant list during the supermarket fluency task? ': 'supermarket items'}, inplace=True)
    
    col_2_consider = df_MCE_dataOverview.columns
    
    cmd = 'df_MCE_dataOverview.rename(columns={'
    
    for i in diff_list(list(df_MCE_dataOverview.columns), ['Research ID', 'Timestamp']):
        
        cmd += '\'' + i + '\': \'MCE '+ i + '\', '
    
    cmd = cmd[0:len(cmd)-2] + '}, inplace=True)'
    
    exec(cmd)
    
    
    
    df_MCE_dataOverview.rename(columns={'Research ID': 'research_ID'}, inplace=True)
    df_MCE_dataOverview.research_ID = df_MCE_dataOverview.research_ID.astype(int)
    
    
    
    
    ## I need to sort the MCE socres dataframe so that I can match them with my metadata 
    
    df_MCE_dataOverview = df_MCE_dataOverview.sort_values(by=["research_ID", "Timestamp"])
    
    '''
    I can assign some pseudo_unq_id as the order of the MoCA tests will correspond to the CognoSpeak tests as well ... 
    '''
    
    df_MCE_dataOverview = get_pseudo_IDs(df_MCE_dataOverview, 1, 'Timestamp').sort_values(by=["research_ID", "pseudo_unq_id"])
    
    
    ## I need to exclude IDs whose RUDAS scores are still to be confirmed ... 
    
    # diff_list( df_manually_updated[df_manually_updated['To_ADD']!='YES'].pseudo_unq_id, df_MCE_dataOverview.pseudo_unq_id)
    df_MCE_dataOverview = df_MCE_dataOverview[~df_MCE_dataOverview.pseudo_unq_id.isin(df_manually_updated[df_manually_updated['To_ADD']!='YES'].pseudo_unq_id)]
    
    
    
    
    
    ### Next, I need to check if there are any mismatches in the MCE scores ... 
    df_Nmatched_MCE = get_Nmatched_COGN_dfs(df_MCE_dataOverview, 'MCE')
    
    # ## Only needing done at the beginnin ... 
    # df_Nmatched_MCE.to_csv( '../data/no_match_MCE_scores.csv', index=False )
    
    
    
    ## Read the CSV file which is updated by Caitlin/Dora here (https://docs.google.com/spreadsheets/d/1FU3zw-0pypCorCiILoRNegBd5d08PHPiQxdUe3IXK5s/edit?gid=1487915522#gid=1487915522)
    
    df_manually_updated = pd.read_csv( '../data/no_match_MCE_scores - no_match_MCE_scores.csv' )
    df_manually_updated = df_manually_updated[~df_manually_updated.Timestamp.isna()]
    
    df_manually_updated.research_ID = df_manually_updated.research_ID.astype(int)
    
    if len(df_manually_updated) > df_manually_updated.To_ADD.isnull().sum():
        df_manually_updated.To_ADD = df_manually_updated.To_ADD.str.upper()
    
    
    ## If there are any other input than 'yes' and 'no', raise an issue ... 
    
    if len(df_manually_updated.To_ADD.value_counts()) > 2:
        print('There are other inputs than YES or NO. Check the online speadsheet ... ')
        sys.stdout.flush()
        time.sleep(100000000)
        
    
    
    ## Check if the most recent pandas dataframe has some more IDs which are not already got sorted ... 
    
    to_save_manual_df = 0 
    if len(df_Nmatched_MCE)> len(df_manually_updated):
        
        r_IDs_2_add = diff_list( list(df_Nmatched_MCE['pseudo_unq_id']), list(df_manually_updated['pseudo_unq_id']))
        to_save_manual_df = 1
    
    ## Only save the manually confirmed one if it got extra IDs which are not already sorted out 
    if to_save_manual_df == 1:
        df_2_add = df_Nmatched_SPRDSHT[df_Nmatched_SPRDSHT['pseudo_unq_id'].isin(r_IDs_2_add)]
        df_save_4_manual_check = pd.concat([df_manually_updated, df_2_add],ignore_index=True)
        df_save_4_manual_check.to_csv(MCE_out_n_matched_spreadshet, index=False)
    
    
    
    
    ## Drop a col in spreadsheet dataframe 
    df_MCE_dataOverview = df_MCE_dataOverview.drop('Timestamp', axis=1)
    
    
    ## Drop the "still to be confirmed dataframe"
    df_MCE_dataOverview = df_MCE_dataOverview[~df_MCE_dataOverview.pseudo_unq_id.isin(df_Nmatched_MCE.pseudo_unq_id)]
    
    
    
    df_manually_updated_sel = df_manually_updated[df_manually_updated['To_ADD']=='YES']
    
    print('MCE: These research IDs are not added as still waiting for manual check: ', list(df_manually_updated[df_manually_updated['To_ADD']!='YES']['research_ID']))
    
    df_MCE_final = pd.concat([df_MCE_dataOverview, df_manually_updated_sel[df_MCE_dataOverview.columns ]], ignore_index=True, sort=False)
    
    df_MCE_final.research_ID = df_MCE_final.research_ID.astype(int)
    df_MCE_final = df_MCE_final.sort_values(['research_ID', 'pseudo_unq_id'])
    
    
    
    ## Prepare and save the MCE scores along with the metadata 
    
    df_all_metadata_MCE = df_all_metadata_RUDAS.merge(df_MCE_final, on=['pseudo_unq_id', 'research_ID'], how='left')
    df_all_MCE_metadata = df_metadata.merge(df_MCE_final, on=['pseudo_unq_id', 'research_ID'], how='right')
    df_metadata_MCE = df_metadata.merge(df_MCE_final, on=['pseudo_unq_id', 'research_ID'], how='inner')
    
    
    # df_all_metadata_MCE.to_csv( MCE_out_all_MCE, index=False )
    df_all_MCE_metadata.to_csv( MCE_out_all_metadta, index=False )
    df_metadata_MCE.to_csv( MCE_out_MCE_metadata, index=False )
    
    
    
    
    
    
    
    
    
    
    
    
    '''
    ###########################################################################
    ###########################################################################
    Now I am working with  ACE-III 
    ###########################################################################
    ###########################################################################
    '''
    
    
    # df_ACE_III 
    
    
    # ## Fix the mis-typed research-IDs
    # df_ACE_III = df_ACE_III.reset_index(drop=True)
    # df_ACE_III.loc[( df_ACE_III[df_ACE_III['Research ID'] == 586965].index.item(), 'Research ID' )] = 58696
    
    ## I will be getting the MMSE scores seperately, not from this ACE sheet ... 
    ## And, I will not need Email Adrress and Date as well (at least for now ...)
    df_ACE_dataOverview = df_ACE_III.drop(['MMSE', 'Email address', 'Date'], axis=1)
    
    df_ACE_dataOverview = df_ACE_dataOverview.dropna(subset=['Research ID'])
    
    ## Change the columns so that two spreadsheet match each other ....
    df_ACE_dataOverview.rename(columns={'If any questions were missed, please provide a reason. ': 'reason_4_missing_question', 'Please list all the words that the participant generated during the "letter P" verbal fluency test. ': 'P fluency', 'Please list all the words that the participant generated during the "animals" verbal fluency test. ':'animal fluency'}, inplace=True)
    
    col_2_consider = df_ACE_dataOverview.columns
    
    cmd = 'df_ACE_dataOverview.rename(columns={'
    
    for i in diff_list(list(df_ACE_dataOverview.columns), ['Research ID', 'Timestamp']):
        
        cmd += '\'' + i + '\': \'ACE '+ i + '\', '
    
    cmd = cmd[0:len(cmd)-2] + '}, inplace=True)'
    
    exec(cmd)
    
    
    
    df_ACE_dataOverview.rename(columns={'Research ID': 'research_ID'}, inplace=True)
    df_ACE_dataOverview.research_ID = df_ACE_dataOverview.research_ID.astype(int)
    
    
    
    ## I need to sort the ACE socres dataframe so that I can match them with my metadata 
    
    df_ACE_dataOverview = df_ACE_dataOverview.sort_values(by=["research_ID", "Timestamp"])
    
    '''
    I can assign some pseudo_unq_id as the order of the MoCA tests will correspond to the CognoSpeak tests as well ... 
    '''
    
    df_ACE_dataOverview = get_pseudo_IDs(df_ACE_dataOverview, 1, 'Timestamp').sort_values(by=["research_ID", "pseudo_unq_id"])
    
    
    
    
    ### Next, I need to check if there are any mismatches in the ACE scores ... 
    
    # df_Nmatched_ACE = get_Nmatched_ACE_dfs(df_ACE_dataOverview)
    df_Nmatched_ACE = get_Nmatched_COGN_dfs(df_ACE_dataOverview, 'ACE')
    
    # ## Only needing done at the beginnin ... 
    # df_Nmatched_ACE.to_csv( '../data/no_match_ACE_scores.csv', index=False )
    
    
    
    ## Read the CSV file which is updated by Caitlin/Dora here (https://docs.google.com/spreadsheets/d/1HYz4YyGXQkD0IGVPu0YWmwHQCn22ySigM0L0CymFjg0/edit?gid=1035080297#gid=1035080297)
    
    df_manually_updated = pd.read_csv( '../data/no_match_ACE_scores - no_match_ACE_scores.csv' )
    df_manually_updated = df_manually_updated[~df_manually_updated.Timestamp.isna()]
    
    df_manually_updated.research_ID = df_manually_updated.research_ID.astype(int)
    if len(df_manually_updated) > df_manually_updated.To_ADD.isnull().sum():
        df_manually_updated.To_ADD = df_manually_updated.To_ADD.str.upper()
    
    
    ## If there are any other input than 'yes' and 'no', raise an issue ... 
    
    if len(df_manually_updated.To_ADD.value_counts()) > 2:
        print('There are other inputs than YES or NO. Check the online speadsheet ... ')
        sys.stdout.flush()
        time.sleep(100000000)
        
    
    
    ## Check if the most recent pandas dataframe has some more IDs which are not already got sorted ... 
    
    to_save_manual_df = 0 
    if len(df_Nmatched_ACE)> len(df_manually_updated):
        
        r_IDs_2_add = diff_list( list(df_Nmatched_ACE['pseudo_unq_id']), list(df_manually_updated['pseudo_unq_id']))
        to_save_manual_df = 1
    
    ## Only save the manually confirmed one if it got extra IDs which are not already sorted out 
    if to_save_manual_df == 1:
        df_2_add = df_Nmatched_SPRDSHT[df_Nmatched_SPRDSHT['pseudo_unq_id'].isin(r_IDs_2_add)]
        df_save_4_manual_check = pd.concat([df_manually_updated, df_2_add],ignore_index=True)
        df_save_4_manual_check.to_csv(ACE_out_n_matched_spreadshet, index=False)
    
    
    
    
    ## Drop a col in spreadsheet dataframe 
    df_ACE_dataOverview = df_ACE_dataOverview.drop('Timestamp', axis=1)
    
    
    ## Drop the "still to be confirmed dataframe"
    df_ACE_dataOverview = df_ACE_dataOverview[~df_ACE_dataOverview.pseudo_unq_id.isin(df_Nmatched_ACE.pseudo_unq_id)]
    
    
    
    df_manually_updated_sel = df_manually_updated[df_manually_updated['To_ADD']=='YES']
    
    print('ACE: These research IDs are not added as still waiting for manual check: ', list(df_manually_updated[df_manually_updated['To_ADD']!='YES']['research_ID']))
    
    df_ACE_final = pd.concat([df_ACE_dataOverview, df_manually_updated_sel[df_ACE_dataOverview.columns ]], ignore_index=True, sort=False)
    
    df_ACE_final.research_ID = df_ACE_final.research_ID.astype(int)
    df_ACE_final = df_ACE_final.sort_values(['research_ID', 'pseudo_unq_id'])
    
    
    
    ## Prepare and save the ACE scores along with the metadata 
    
    df_all_metadata_ACE = df_all_metadata_MCE.merge(df_ACE_final, on=['pseudo_unq_id', 'research_ID'], how='left')
    df_all_ACE_metadata = df_metadata.merge(df_ACE_final, on=['pseudo_unq_id', 'research_ID'], how='right')
    df_metadata_ACE = df_metadata.merge(df_ACE_final, on=['pseudo_unq_id', 'research_ID'], how='inner')
    
    
    ## A final check: there should not be any duplacted 'pseudo_unq_id' in df_all_metadata_ACE:
    
    if len(find_values_counts( df_all_metadata_ACE.pseudo_unq_id, 1 )) != 0:
        
        print('\n\n********* STOP: there are duplicated "pseudo_unq_id" in df_all_metadata_ACE')
    
    
    
    df_all_ACE_metadata.to_csv( ACE_out_all_metadta, index=False )
    df_metadata_ACE.to_csv( ACE_out_ACE_metadata, index=False )
    
    
    ## ADD MMSE scores as well ... 
    df_MMSE = pd.read_csv( '../data/Challenge ideas - MoCA2MMSE.csv' )
    df_MMSE.rename(columns={'MoCA':'MoCA Total score'}, inplace=True)
    
    df_all_metadata_ACE = df_all_metadata_ACE.merge(df_MMSE[['MoCA Total score', 'MMSE']], on=['MoCA Total score'], how='left')
    
    
    
    
    df_all_metadata_ACE.to_csv( ACE_out_all_ACE, index=False )
    
    
    
    
    
    
    executionTime = (datetime.now() - startTime)
    current_time = datetime.now().strftime("%Y/%m/%d at %H:%M:%S")
    print('\n\nThe script completed at: ' + str(current_time))
    print('Execution time: ' + str(executionTime), ' \n\n')
    
    
    
    
    
    
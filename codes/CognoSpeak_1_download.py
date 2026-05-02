#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Apr  8 14:53:54 2024

@author: madhupahar
"""


# import os, sys, time, glob

from main import *
from config import *
check_env('ACONDA')

from datetime import datetime

from tqdm import tqdm
from natsort import natsorted

# from multiprocessing.pool import ThreadPool, Pool
# from multiprocessing import cpu_count



def generate_log():
    log_cmd = 'gcloud storage ls {}/*/*.zip > {}'.format(cloud_base, log_file)
    print('The command to get the list of files from cloud: ', log_cmd)
    sys.stdout.flush()
    os.system(log_cmd)
    print('Generating the log file is complete.\n\n')
    sys.stdout.flush()


def get_ZIP_downloaded():
    zip_files_downloaded_list = glob.glob(raw_data_dir+"*.zip")
    
    D_file_ID_list = []
    
    for a_file in zip_files_downloaded_list:
        D_file_ID_list.append(a_file.split('/')[-1].split('.zip')[0])
    
    return D_file_ID_list



# def do_get_ZIP_4M_logs_OLD(a_list):
#     file_ID_list = []
#     r_ID_list = []
#     for a_file in a_list:
#         if a_file.endswith('.zip'):
#             file_ID = a_file.split('/')[-1].split('.zip')[0]
#             file_ID_list.append(file_ID)
#             if len(file_ID.split('_')) == 5:
#                 r_ID = file_ID.split('_')[1]
#                 r_ID_list.append(int(r_ID))
#     return file_ID_list, r_ID_list



# def do_get_ZIP_4M_logs(a_list):
#     file_ID_list = []
#     r_ID_list = []
#     for a_file in a_list:
#         if a_file.endswith('.zip'):
#             file_ID = a_file.split('/')[-1].split('.zip')[0]
            
#             if file_ID.startswith('STROKE_') or file_ID.startswith('MND_'):
#                 # print(file_ID)
#                 if len(file_ID.split('_')) == 6 and file_ID.split('_')[2] != '':
#                     # r_ID = file_ID.split('_')[1]
#                     r_ID_list.append(int(file_ID.split('_')[2]))
#                     file_ID_list.append(file_ID)
                    
#             else:
#                 if len(file_ID.split('_')) == 5 and file_ID.split('_')[1] != '':
#                     # r_ID = file_ID.split('_')[1]
#                     r_ID_list.append(int(file_ID.split('_')[1]))
#                     file_ID_list.append(file_ID)
#     return file_ID_list, r_ID_list



def get_ZIP_4M_logs(log_file):
    log_content = read_file(log_file)
    
    file_ID_list, r_ID_list = do_get_ZIP_4M_logs(log_content.split('\n'))
    
    check_list_len(r_ID_list, file_ID_list)
    
    
    return file_ID_list, r_ID_list



def do_gsutil(args):
    cloud_base, a_file, raw_data_dir = args[0], args[1], args[2]
    download_cmd = 'gcloud storage cp {}/*/{}.zip {}'.format(cloud_base, a_file, raw_data_dir)
    print('command to download : ', download_cmd)
    sys.stdout.flush()
    
    os.system(download_cmd)


def delete_folder(root_dir, a_zip):
    dir_to_del = root_dir+ a_zip.replace('.zip', '').replace('__', '_')
    
    if os.path.isdir( dir_to_del ):
        del_cmd = 'rm -rf {}'.format( dir_to_del )
        
        if os.system(del_cmd) != 0:
            print('This command did not execute successfully: ', del_cmd)
        else:
            print('This dir has been successfully deleted : ', dir_to_del)
        sys.stdout.flush()
    else:
        print('This dir has already been deleted: ', dir_to_del)

## This is to find out the list of ZIPs whose names are changed and they exist ... 
def get_list_exist_name_ZIP_2_update():
    
    list_exit_2_update_ZIPs = []
    
    for a_zip in list_of_2_update_ZIPs:
        # chng_cmd = 'mv {} {}'.format(raw_data_dir+'S_11475__240318_192653.zip', raw_data_dir+'S_991147599__240318_192653.zip')
        
        a_zip += '.zip'
        
        
        
        # print('raw_data_dir+a_zip : ', raw_data_dir+a_zip)
        
        if os.path.exists( raw_data_dir+ a_zip.replace('_'+a_zip.split('__')[0].split('_')[-1]+'__', '_99'+a_zip.split('__')[0].split('_')[-1]+'99__') ):
            
            list_exit_2_update_ZIPs.append( a_zip.replace('.zip', '') )
        
    return list_exit_2_update_ZIPs






if __name__=='__main__' and '__file__' in globals():
    
    
    # if len(sys.argv) < 2:
    #     print('Please use : python CognoSpeak_1_download.py 15 [where 15 is the number of CPU]')
    #     sys.exit()
    
    
    # startTime = datetime.now()
    # current_time = startTime.strftime("%Y/%m/%d at %H:%M:%S")
    # print('\n\nThe script starting at: ' + str(current_time), ' \n\n' )
    
    # N_jobs = int(sys.argv[1])
    
    
    # if N_jobs >= cpu_count():
    #     print('The max no of CPU available : ', cpu_count())
    #     sys.exit("Lower the number of CPU\n\n")
    
    
    
    '''
    Step 1: Check and download the ZIp files from the server .... 
    
    I made a seperate python script as there were some bugs in the downloading, but they are fixed. 
    '''
    
    ct = datetime.now()
    
    # cloud_base = 'gs://cognospeak-production.appspot.com/production'
    # raw_data_dir = '../data/raw_data/'
    # extracted_data_dir = '../data/EXTRACTED_RAW_DATA/'
    # final_extract_dir = '../data/FINAL_EXTRACTED_AUDIO/'
    
    '''
    The ZIP files which have duplicated ID: Dupliacted_ID_subject
    '''
    
    ## These are the ZIP files whose names are to be updated ... 
    list_of_2_update_ZIPs = ['S_11475__240318_192653', 'R_68020__240110_143730', 'R_69972__240417_125615', 'S_98225__240514_154931', 'S_71214__240608_172213', 'S_77261__240404_184926', 'S_23376__240406_214245', 'S_13483__240320_094310', 'S_28093__240203_143218', 'S_66880__231216_114710', 'S_72577__240208_204817', 'S_27369__231207_175714', 'S_87334__240131_120355', 'S_70454__230519_124655', 'S_62692__231210_175804', 'S_38609__240315_124944', 'S_13201__240321_092731', 'S_95500__231128_192609', 'S_62755__231116_111945', 'S_99715__250122_113659']
    
    
    
    # log_file = '../logs/cogno_zip_list__2024-08-02.txt'
    # log_file = '../logs/cogno_zip_list__'+ct.strftime("%Y-%m-%d") + '_' + ct.strftime("%H-%M-%S")+'.txt'
    ## I realised that it might be a good idea to keep only the date not time in the log file names 
    log_file = '../logs/cogno_zip_list__'+ct.strftime("%Y-%m-%d") +'.txt'
    
    
    
    ##### Saved in config.py now ... 
    
    ## There have also been situations where I needed to ignore some assessments ... 
    ## Some of these assessments do not appear on the portal and has been mentioned on the tracker, on 28/11/2024
    ## Make sure to add '__' here ... 
    # to_ignore_assessments = ['R_32882__241010_140101', 'R_32882__241107_154458', 'R_03749__241126_134803', 'R_72014__241126_141640', 'R_45234__240603_120827', 'S_23974__240405_170053', 'S_23974__240405_123053', 'S_992397499__240405_123053', 'R_84513__240814_104736', 'R_998451399__240814_104736', 'R_25600__240515_193138', 'R_01541__240227_100039', 'MND_S_23376__240406_214245']
    
    ## This is to check if I have forrgotten to put __ 
    nod__ = [x for x in to_ignore_assessments if not '__' in x]
    
    if len(nod__) > 0:
        print('The following dirs do not have __ in it: ')
        print(nod__)
        sys.stdout.flush()
        time.sleep(100000000)
    
    
    
    if os.path.exists(log_file):
        
        print('Reading from already existing log file ..... ', log_file)
        sys.stdout.flush()
        
        log_ZIP_ID_list, _ = get_ZIP_4M_logs(log_file)
        downloaded_ZIP_ID_list = get_ZIP_downloaded()
        
        if len(log_ZIP_ID_list) < len(downloaded_ZIP_ID_list):
            print('The log file is incomplete. Downloading it again .... ')
            generate_log()
        
        
    else:
        generate_log()
    
    
    time.sleep(1)
    
    
    log_ZIP_ID_list, _ = get_ZIP_4M_logs(log_file)
    downloaded_ZIP_ID_list = get_ZIP_downloaded()
    
    
    ########## This is to update the dir with extension 'MND_' which are already exisiing ... 
    
    # log_ZIP_ID_list = list(set([x.replace(x.split('_')[0]+'_', '') if len(x.split('_')) == 6 else x for x in log_ZIP_ID_list ]))
    
    # len(set(unq))
    
    # n = 0
    # for x in log_ZIP_ID_list:
    #     if len(x.split('_')) == 6:
    #         n += 1
    
    df_dupl_check = pd.DataFrame([], columns=['ori_dir', 'trim_dir'])

    for x in log_ZIP_ID_list:
        
        if len(x.split('_')) == 6:
            
            oRi = x
            cHgd = x.replace(x.split('_')[0]+'_', '')
            
            if cHgd in log_ZIP_ID_list:
                
            
                df_dupl_check.loc[len(df_dupl_check.index)] = [oRi] + [cHgd] 
    
    
    ## Delete the ori_dir column from raw_dir and log_ZIP_ID_list
    
    for a_zip in df_dupl_check.ori_dir:
        
        
        rm_cmd = 'rm {}'.format( raw_data_dir+a_zip+'.zip' )
        rename_a_file(rm_cmd)
        
        delete_folder(extracted_data_dir, a_zip)
        delete_folder(final_extract_dir, a_zip)
        delete_folder(final_transcript_dir, a_zip)
        
        print('This file has been deleted: ', a_zip)
    
    ###########################################
    
    
    log_ZIP_ID_list = diff_list(log_ZIP_ID_list, df_dupl_check.ori_dir)
    
    downloaded_ZIP_ID_list = get_ZIP_downloaded()
    
    
    
    
    
    
    
    print( 'Number of ZIP files in LOG file', len(log_ZIP_ID_list) )
    print( 'Number of already DOWNLOADED ZIP files ', len(downloaded_ZIP_ID_list) )
    # check_list_len( log_ZIP_ID_list, downloaded_ZIP_ID_list )
    sys.stdout.flush()
    
    
    
    
    
    
    
    '''
    Collection of all ZIP files = list(set(log_ZIP_ID_list + downloaded_ZIP_ID_list))
    
    ZIPs which I don't want to download: downloaded_ZIP_ID_list + to_ignore_assessments
    
    So, I will download: diff_list( list(set(log_ZIP_ID_list + downloaded_ZIP_ID_list)), (downloaded_ZIP_ID_list + to_ignore_assessments) )
    
    
    Then, I need to exclude those (list_of_2_update_ZIPs) who are changed: diff_list( diff_list( list(set(log_ZIP_ID_list + downloaded_ZIP_ID_list)), (downloaded_ZIP_ID_list + to_ignore_assessments) ), get_list_exist_name_ZIP_2_update() )
    
    '''
    
    
    
    ZIP_files_to_download = diff_list( diff_list( list(set(log_ZIP_ID_list + downloaded_ZIP_ID_list)), (downloaded_ZIP_ID_list + to_ignore_assessments) ), get_list_exist_name_ZIP_2_update() )
    
    
    if len(ZIP_files_to_download) > 0:
        ####### This is downloading one file at a time. It is slow but working fine .... #########
        
        for a_file in tqdm(ZIP_files_to_download):
            
            download_cmd = 'gcloud storage cp {}/*/{}.zip {}'.format(cloud_base, a_file, raw_data_dir)
            print('Command to download the ZIP files from the server : ', download_cmd)
            sys.stdout.flush()
            
            os.system(download_cmd)
        
        #######################################################################
        
        
        print('Downloading ', len(ZIP_files_to_download), ' files are complete.')
        sys.stdout.flush()
        
    else:
        print('All the ZIP files are already downloaded.')
        sys.stdout.flush()
    
    
    
    
    
    
    '''
    ZIP_ID_NOTES
    The following steps I needed to take for the issue of duplicated IDs for different participants. 
    These IDs are needed to be sorted sperately as they had issues while being recorded. 


    ## Same IDs for different people ... 

    As of 25/05/2024, following are such IDs 

    11475, 23376, 68020, 69972, 77261, 71214

    11475: two appearances. both HC. one has been renamed. 
    
    23376: two appearances. S_23376__240406_214245 does not have any audio. So, this one has been renamed 
    
    68020: two appearances. one has been renamed. they were done within 1 day.  

    69972: these two are for the same subject: ['S_69972__231207_153042', 'S_69972__231207_153838']

    77261: two appearances. Keeping this one as it is: S_77261__240124_140906 and changing this one:S_77261__240404_184926
    
    98225: two ZIP files and two assessments on the portal. They are done on the same day and only for one subject. The other subject data was missing, so I manually downloaded that and renamed it. 
    these two are for the same subject: ['R_98225__240603_112047', 'R_98225__240603_112139']
    
    71214: two appearnce on the portal and two on ZIP files (I manually downloaded one). The latest one has been renamed. 
    
    13483, 28093, 66880, 72577 : two appearances, one has been renamed
    
    '''
    
    # IDs_2_b_changed = [11475, 23376, 68020, 69972, 98225, 71214, 77261, 13483, 28093, 66880, 72577, 27369, 87334, 70454, 62692, 38609]
    
    IDs_2_b_changed = [int(x.split('__')[0].split('_')[-1]) for x in list_of_2_update_ZIPs]
    
    
    for a_zip in list_of_2_update_ZIPs:
        # chng_cmd = 'mv {} {}'.format(raw_data_dir+'S_11475__240318_192653.zip', raw_data_dir+'S_991147599__240318_192653.zip')
        
        a_zip += '.zip'
        
        # print('raw_data_dir+a_zip : ', raw_data_dir+a_zip)
        
        if os.path.exists( raw_data_dir+a_zip ):
            
            chng_cmd = 'mv {} {}'.format(raw_data_dir+a_zip, raw_data_dir+a_zip.replace('_'+a_zip.split('__')[0].split('_')[-1]+'__', '_99'+a_zip.split('__')[0].split('_')[-1]+'99__'))
            
            rename_a_file(chng_cmd)
            
            print('This rename command has been executed: ', chng_cmd)
            
            # Delete the folders which are renamed inside other three folders as well ... 
            
            delete_folder(extracted_data_dir, a_zip)
            delete_folder(final_extract_dir, a_zip)
            delete_folder(final_transcript_dir, a_zip)
        # else:
        #     print('No exisit : raw_data_dir+a_zip : ', raw_data_dir+a_zip)
        
    
    
    ## Delete the folders for which assessments are ignored ... 
    
    for a_zip in to_ignore_assessments:
        a_zip += '.zip'
        if os.path.exists( raw_data_dir+a_zip ):
            
            rm_cmd = 'rm {}'.format( raw_data_dir+a_zip )
            rename_a_file(rm_cmd)
            
            # chng_cmd = 'mv {} {}'.format(raw_data_dir+a_zip, raw_data_dir+a_zip.replace('_'+a_zip.split('__')[0].split('_')[-1]+'__', '_99'+a_zip.split('__')[0].split('_')[-1]+'99__'))
            
            # rename_a_file(chng_cmd)
            
            # print('This remane command has been executed: ', chng_cmd)
            
        # Delete the folders which are renamed inside other three folders as well ... 
        
        delete_folder(extracted_data_dir, a_zip)
        delete_folder(final_extract_dir, a_zip)
        delete_folder(final_transcript_dir, a_zip)
    
    
    
    downloaded_ZIP_ID_list = get_ZIP_downloaded()
    
    
    '''
    These are the assessments which came from the same subject (with IDs which have been assigned to other poeple as well)
    Only add the ID to overlook after checking them inside raw_data folder 
    '''
    
    list_same_ZIPs = [['S_69972__231207_153042', 'S_69972__231207_153838'], ['R_98225__240603_112047', 'R_98225__240603_112139'], ['R_28093__240911_142344', 'R_28093__250506_092734', 'R_28093__250506_092834', 'R_28093__251006_140349'], ['R_13201__241219_135902', 'R_13201__241219_140320']]
    
    dupl_issues_exist = 0
    
    for ID in IDs_2_b_changed:
        
        id_appears = []
        for file in natsorted(downloaded_ZIP_ID_list):
            if '_'+make_N_chars_a_val(ID, 5)+'__' in file:
                id_appears.append( file )
        
        # if len(id_appears) > 1:
        if len(id_appears) > 1 and not id_appears in list_same_ZIPs:
            print('\n\n******** The duplicated ID issue persists for : ', ID)
            print('Appearances: ', id_appears)
            print('PLEASE double check. ********\n\n')
            sys.stdout.flush()
            # time.sleep(100000000)
            dupl_issues_exist = 1
    
    # print('Check the notes about these ZIP files towards the end of this script, titled : ZIP_ID_NOTES')
    
    if dupl_issues_exist == 1:
        print('\n\n**** Check these ZIPs manually and add notes at the section titled : ZIP_ID_NOTES')
    
    
    # print('\n\n***************************************')
    # print('Ignore the following appearances as they are manually checked as coming from one person: ')
    # print('[\'S_23376__230824_192211\', \'S_23376__240406_214245\']')
    # print('[\'S_69972__231207_153042\', \'S_69972__231207_153838\']')
    # print('[\'R_98225__240603_112047\', \'R_98225__240603_112139\']')
    # print('***************************************\n\n')
    
    
    # '''
    # I need to add this section as there are assessments for which two ZIP files, one starting with MND or Stroke 
    # '''
    
    # all_ZIP_files = [x.split(raw_data_dir)[-1] for x in find_files_in_a_dir(raw_data_dir, '.zip')]
    
    # find_values_counts(all_ZIP_files, 1)
    
    # for i in all_ZIP_files:
        
    #     if 'MND_' + i in all_ZIP_files:
            
    #         print(i)
    
    
    
    
    
    
    executionTime = (datetime.now() - startTime)
    current_time = datetime.now().strftime("%Y/%m/%d at %H:%M:%S")
    print('\n\nThe script completed at: ' + str(current_time))
    print('Execution time: ' + str(executionTime), ' \n\n')





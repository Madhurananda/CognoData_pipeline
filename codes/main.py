import os
import sys
import pickle
import numpy as np
import time
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix, f1_score, precision_score, recall_score, roc_auc_score, r2_score, mean_squared_error, root_mean_squared_error
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.utils.class_weight import compute_class_weight

from sklearn.metrics import precision_recall_fscore_support as score

# from nltk.corpus import stopwords
# import re

import scipy.stats as stats




def check_endWith(basecalled_folder):
    if not basecalled_folder.endswith('/'):
        basecalled_folder+='/'
    return basecalled_folder

def check_create_dir(folder):
    if_create = False
    if not os.path.isdir(folder):
        os.makedirs(folder, exist_ok=True)
        if_create = True
        print('**\nThe Folder has been created: ', folder, '**\n')
    # else:
    #     print('The folder already exists: ', folder)
    return if_create

def check_env(env):
    if not os.environ['CONDA_DEFAULT_ENV'] == env:
        print('\n\n*** Please use:    conda activate '+env+'    and run the script again.***\n\n')
        sys.exit(1)

# This function writes content to a file. 
def write_file(file_name, to_write):
    # replaces the contents 
    file = open(file_name,"w")#write mode 
    file.write(to_write) 
    file.close() 

# This function appends content to a file. 
def append_file(file_name, to_write):
    # Append-adds at last 
    file = open(file_name,"a")#append mode 
    file.write(to_write) 
    file.close() 

# calculate file size in KB, MB, GB
def convert_bytes(size):
    """ Convert bytes to KB, or MB or GB"""
    for x in ['bytes', 'KB', 'MB', 'GB', 'TB']:
        if size < 1024.0:
            return "%3.1f %s" % (size, x)
        size /= 1024.0

def count_lines(a_fastQ_file):
    stream = os.popen('cat {} | wc -l'.format(a_fastQ_file))
    output = stream.read()
#    print('line no: ', output, ' for file: ', a_fastQ_file)
    return output

def del_dir_content_files(dir):
    delete_dir_content_cmd = 'rm '+dir+'*'
    os.system(delete_dir_content_cmd)
    print('The files are deleted inside: ', dir, ' using the command: ', delete_dir_content_cmd)
    sys.stdout.flush()

def read_file(file):
    f = open(file, "r")
    return f.read()



def save_file(file_save_name, file_data):
    # with open('/home/madhu/work/comp_tools/paper_6/download_tools/EpiNano/df.pickle', 'wb') as handle:
    with open(file_save_name, 'wb') as handle:
        pickle.dump(file_data, handle, protocol=pickle.HIGHEST_PROTOCOL)

def load_file(file_load_name):
    # with open('/home/madhu/work/comp_tools/paper_6/test_paper_6/m6A_detection/pd.pkl', 'rb') as file:
    with open(file_load_name, 'rb') as file:
        file_data = pickle.load(file)
    return file_data



'''
find_files_in_a_dir('/home/madhu/work/basecall/guppy_v5.0.11/MY_TEST_p3/GSM3528751/', '.fast5')
'''
def find_files_in_a_dir(input_dir, file_extension):
    list_files = [os.path.join(root, name)
             for root, dirs, files in os.walk(input_dir)
             for name in files
             if name.endswith((file_extension))]
    return list_files



'''
count_files_in_a_dir('/home/madhu/work/basecall/guppy_v5.0.11/MY_TEST_p3/GSM3528751/', '.fast5')
'''

def count_files_in_a_dir(input_dir, file_extension):
   list_files = [os.path.join(root, name)
             for root, dirs, files in os.walk(input_dir)
             for name in files
             if name.endswith((file_extension))]
   return len(list_files)



'''
get the directory size 
get_size('/home/madhu/work/basecall/guppy_v5.0.11/MY_TEST_p3/')
'''
def get_size(start_path = '.'):
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(start_path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            # skip if it is symbolic link
            if not os.path.islink(fp):
                total_size += os.path.getsize(fp)

    return convert_bytes(total_size)




'''
It works for: 
list_1 = [1, 2, 3, 4]
list_2 = [2, 4]

It doesn't work for:
list_2 = [1, 2, 3, 4]
list_1 = [2, 4]

It should be called as:
    diff_list(list_1, list_2)

'''
def diff_list(list_1, list_2):
    # diff_list = [x for x in list_1 if x not in list_2]
    return [x for x in list(list_1) if x not in list(list_2)]



'''
This method find intersection between two lists
'''
# Python program to illustrate the intersection
# of two lists using set() method
def intersection(lst1, lst2):
    return list(set(lst1) & set(lst2))



'''
This method find values and their counts in a list
'''
def find_values_counts(given_list, mult_only=0):
    
    freq_dist = []
    
    counted_list = np.unique(given_list, return_counts=True)
    for i in range(len(counted_list[0])):
        if mult_only == 1:
            if counted_list[1][i] > 1:
                # print('Value : ', counted_list[0][i], ' ; Count: ', counted_list[1][i])
                freq_dist.append([ counted_list[0][i], counted_list[1][i] ])
        else:
            # print('Value : ', counted_list[0][i], ' ; Count: ', counted_list[1][i])
            freq_dist.append([ counted_list[0][i], counted_list[1][i] ])        
            
    # print( '*** TOTAL : ', len(given_list) )
    return freq_dist



def check_list_len(list_1, list_2):
    if len(list_1) != len(list_2):
        print('The lengths of these two lists are not the same.' )
        
        print('list 1 len: ', len(list_1))
        print('list 2 len: ', len(list_2))
        
        sys.stdout.flush()
        time.sleep(100000000)


def check_dir_exists(a_dir):
    if not os.path.exists(a_dir):
        print('******** CHECK: Destination do not exist ', a_dir)
        sys.stdout.flush()
        sys.exit()


## Find the strings in between i_str and f_str for given_str
def find_str_between(given_str, i_str, f_str):
    list_strs = []
    for i in range(len(given_str.split(i_str))):
        if i != 0:
            list_strs.append( given_str.split(i_str)[i].split(f_str)[0] )
            # print( given_str.split(i_str)[i].split(f_str)[0] )
    
    return list_strs
    
def remove_item_list(a_list, item):
    list1 = [i for i in a_list if i != item]
    return list1
    

## Find all the positions of a char 'c' in the string 's'
def find_char_string(s, c):
    return [pos for pos, char in enumerate(s) if char == c]
    



def calc_metrics(actual_labels, pred_vals, avg=None):
    if avg == None: 
        f1_val = f1_score(actual_labels, pred_vals)
        pres_val = precision_score(actual_labels, pred_vals)
        rec_val = recall_score(actual_labels, pred_vals)
    else:
        f1_val = f1_score(actual_labels, pred_vals, average=avg)
        pres_val = precision_score(actual_labels, pred_vals, average=avg)
        rec_val = recall_score(actual_labels, pred_vals, average=avg)
    
    conf_val = confusion_matrix(actual_labels, pred_vals)
    
    specificity = conf_val[0][0]/(conf_val[0][0]+conf_val[0][1])
    sensitivity = conf_val[1][1]/(conf_val[1][0]+conf_val[1][1])
    
    
    acc = accuracy_score(list(actual_labels), list(pred_vals))
    
    return f1_val, pres_val, rec_val, acc, conf_val, specificity, sensitivity





def get_rmspe(y_true, y_pred):
    rmspe = np.sqrt(np.mean(np.square(((y_true - y_pred) / y_true)), axis=0))
    return rmspe


def calc_regress_metrics( y_true, y_pred ):
    print('R2-score: ', round(r2_score( y_true, y_pred ), 2))
    print('MSE: ', round(mean_squared_error( y_true, y_pred ), 2))
    print('RMSE: ', round(root_mean_squared_error( y_true, y_pred ), 2))
    print('RMSPE: ', round(get_rmspe( y_true, y_pred ), 2))



'''
The following function should calcualte and print the predicted labels based on majority voting. 
The pandas dataframe df should have two columns: r_IDs and pred_label
'''
def majority_voting_pred_labels(df, a_class_type, verbose):
    data = {'r_IDs':df[['r_IDs', 'pred_label']].groupby('r_IDs').mean().index.values, 
            'mean_pred_label':df[['r_IDs', 'pred_label']].groupby('r_IDs').mean().pred_label.values,
            'mean_pred_proba':df[['r_IDs', 'pred_proba']].groupby('r_IDs').mean().pred_proba.values}
    df_final_test_grouped = df.merge(pd.DataFrame(data), on='r_IDs', how='inner')
    
    # print('df_final_test_grouped before : ')
    # print(df_final_test_grouped)
    
    df_final_test_grouped = df_final_test_grouped.drop_duplicates(subset="r_IDs", keep='first')
    
    # print('df_final_test_grouped after : ')
    # print(df_final_test_grouped)
    
    
    ## I need to fix this error: when there is only one value for a r_ID, the final_pred_label is wrong 
    
    mult_Quests = 0
    
    if df.shape[0] > df_final_test_grouped.shape[0]:
        mult_Quests = 1
        
        # if df.shape[0]%df_final_test_grouped.shape[0] != 0:
        #     print('The test dataframe contains uneqaul number of r_IDs for each r_ID.')
        #     print('The test df: ')
        #     print(df)
        #     print('The grouped df: ')
        #     print(df_final_test_grouped)
        #     sys.exit(0)
    
    
    ## If there are multiple entriesd for an r_ID, I will consider the mean pred_labels, otherwise I will keep those values 
    if mult_Quests == 1:
    
        if a_class_type == '3-way':
            thrs_val = 0.333333
            
            final_pred_label_list = []
            for x in df_final_test_grouped.mean_pred_label:
                if x < thrs_val:
                    final_pred_label_list.append(0)
                elif x >= thrs_val and x < (2*thrs_val):
                    final_pred_label_list.append(1)
                else:
                    final_pred_label_list.append(2)
            
        else:
            thrs_val = 0.5
            
            final_pred_label_list = []
            for x in df_final_test_grouped.mean_pred_label:
                if x < thrs_val:
                    final_pred_label_list.append(0)
                else:
                    final_pred_label_list.append(1)
            
        df_final_test_grouped.insert(len(df_final_test_grouped.columns), 'final_pred_label', final_pred_label_list)
        
        
    else:
        # df_final_test_grouped.insert(len(df_final_test_grouped.columns), 'final_pred_label', final_pred_label_list)
        # df_final_test_grouped['final_pred_label'] = df['pred_label']
        df_final_test_grouped.insert(len(df_final_test_grouped.columns), 'final_pred_label', list(df['pred_label']))
    
    
    
    ## Calculate the initial results 
    actual_labels = df_final_test_grouped.labels
    
    pred_vals = df_final_test_grouped['final_pred_label']
    
    f1_val, pres_val, rec_val, acc, conf_val, specificity, sensitivity = calc_metrics(list(actual_labels), list(pred_vals), avg='macro')
    
    # calc_metrics(actual_labels, pred_vals, avg='micro')
    # calc_metrics(actual_labels, pred_vals, avg='weighted')
    
    # print('with threshold = 0.5')
    if verbose == 1:
        print('Macro F1-score: ', round(f1_val, 2))
        print('Macro Precision: ', round(pres_val, 2))
        print('Macro Recall: ', round(rec_val, 2))
        print('conf mat')
        print(conf_val)
    
    if a_class_type == '3-way':
        
        # print('actual_labels: ')
        # print(list(actual_labels))
        # print('mean_pred_proba')
        # print(list(df_final_test_grouped['mean_pred_proba']))
        
        # AUC = roc_auc_score( list(actual_labels), list(df_final_test_grouped['mean_pred_proba']), multi_class='ovr' )
        # AUC = roc_auc_score( np.array(actual_labels), np.array(df_final_test_grouped['mean_pred_proba']), multi_class='ovr' )
        
        #### I realsied on 12/Nov/2025 that I need to sort out the list to array for calculating AUC scores for 3-way classification, and I am not spending more time on this
        # https://scikit-learn.org/stable/modules/generated/sklearn.metrics.roc_auc_score.html
        
        AUC = 0
        
        precision, recall, fscore, support = score(list(actual_labels), list(pred_vals))
        if verbose == 1:
            print('Metric \t HC \t MCI \t Demen')
            # print('------ \t ------ \t ------ \t ------')
            print('Precis \t {} \t {} \t {}'.format( round(precision[0], 2), round(precision[1], 2), round(precision[2], 2) ))
            print('Recall \t {} \t {} \t {}'.format( round(recall[0], 2), round(recall[1], 2), round(recall[2], 2) ))
            print('F1-val \t {} \t {} \t {}'.format( round(fscore[0], 2), round(fscore[1], 2), round(fscore[2], 2) ))
            
        
            
    elif a_class_type == '2-way':
        AUC = roc_auc_score( list(actual_labels), list(df_final_test_grouped['mean_pred_proba']) )
    else:
        print('There should be either 2-way or 3-way classification.')
        sys.stdout.flush()
        time.sleep(100000000)
    
    return f1_val, pres_val, rec_val, acc, conf_val, AUC, specificity, sensitivity



def calc_class_weight(train_y):
    """
    Compute class weight given imbalanced training data
    Usually used in the neural network model to augment the loss function (weighted loss function)
    Favouring/giving more weights to the rare classes.
    """
    
    class_list = list(set(train_y))
    # class_weight_value = scikit_class_weight.compute_class_weight(class_weight ='balanced', classes = class_list, y = train_y)
    class_weight_value = compute_class_weight(class_weight ='balanced', classes = np.unique(train_y), y = train_y)
    class_weight = dict()

    # Initialize all classes in the dictionary with weight 1
    curr_max = int(np.max(class_list))
    for i in range(curr_max):
        class_weight[i] = 1

    # Build the dictionary using the weight obtained the scikit function
    for i in range(len(class_list)):
        class_weight[class_list[i]] = class_weight_value[i]

    return class_weight
    

def gen_train_test_loss_fig(train_losses_mean, train_losses_std, val_losses_mean, val_losses_std, num_epochs, fig_out_file, a_class_type):
    ## This is saving the train and test losses 
    
    # fig_out_file = results_path+FINAL_TOKEN+'__FOLD-'+str(k)+'.png'
    
    
    
    fig, axes = plt.subplots(nrows = 1, ncols = 1, figsize=(20, 15))
    
    x = range(num_epochs)
    
    plt.plot(x, train_losses_mean, label='train_loss')
    plt.plot(x, val_losses_mean, label='val_loss')
    
    plt.errorbar(x, train_losses_mean, yerr = train_losses_std, fmt ='o')
    plt.errorbar(x, val_losses_mean, yerr = val_losses_std, fmt ='o')
    
    plt.xlabel('epochs', fontsize = 22)
    plt.ylabel('losses', fontsize = 22)
    
    # plt.xlim([-5, 20]) 
    if a_class_type == '2-way':
        plt.ylim([0, 1]) 
    
    plt.xticks(x, range(1, num_epochs+1), fontsize = 18)
    # plt.yticks(np.linspace(0, 1, 11), [str(int(x*100))+'%' for x in np.linspace(0, 1, 11)], fontsize = 12)
    plt.yticks(np.linspace(0, 1, 11), [str(round(x, 2)) for x in np.linspace(0, 1, 11)], fontsize = 18)
    
    plt.legend(loc="upper right", fontsize = 18)
    plt.tight_layout()
    plt.show()
    
    
    
    plt.savefig(fig_out_file)
    plt.close()
    print('\nThe figure has been successfully generated as: ', fig_out_file, '\n')




# def get_cuda_cmd(cuda_ids):
#     device_cmd = 'device = torch.device("cuda:'
    
#     for i in range(len(cuda_ids)):
#         if i == 0:
#             device_cmd += str(cuda_ids[i])
#         else:
#             device_cmd += ','+str(cuda_ids[i])
    
#     device_cmd += '" if torch.cuda.is_available() else "cpu")'
    
#     return device_cmd
    

def get_os_cmd(cuda_ids):
    os_cmd = 'os.environ["CUDA_VISIBLE_DEVICES"] ="'
    
    # os.environ['CUDA_VISIBLE_DEVICES'] ='1,2'
    
    # print('Len of cuda_ids ', len(cuda_ids))
    
    for i in range(len(cuda_ids)):
        if i == 0:
            os_cmd += str(cuda_ids[i])
        else:
            os_cmd += ','+str(cuda_ids[i])
    
    os_cmd += '"'
    
    return os_cmd
    

def get_weight_list(df):
    
    weights = calc_class_weight(df.labels)
    
    weight_list = []
    for key, weight in weights.items():
        weight_list.append(weight)
    
    return weight_list
    



'''
This is to do the independant two-tailed t-test 

# Sample data (different sample sizes)
group1 = np.array([10, 12, 15, 13, 11, 14])
group2 = np.array([16, 18, 20, 17, 19])
do_t_test( group1, group2 )

'''

def do_t_test( group1, group2 ):
    # Perform Welch's t-test
    t_statistic, p_value = stats.ttest_ind(np.array(group1), np.array(group2), equal_var=False)
    
    print('\n\n********\n')
    print('Group 1 mean ', np.mean(group1), ' STD: ', np.std(group1))
    print('Group 2 mean ', np.mean(group2), ' STD: ', np.std(group2))
    
    print("T-statistic:", t_statistic)
    print("P-value:", p_value)
    
    alpha = 0.01
    if p_value < alpha:
        print("Reject the null hypothesis - significant difference at 1% level of significance")
    else:
        print("Fail to reject the null hypothesis - no significant difference at 1% level of significance")
    
    alpha = 0.05
    if p_value < alpha:
        print("Reject the null hypothesis - significant difference at 5% level of significance")
    else:
        print("Fail to reject the null hypothesis - no significant difference at 5% level of significance")
    print('\n********\n\n')
    
    return t_statistic, p_value

## Normalise a signal to 0.99 
def normalise_sig(y):
    mult = 0.99/(max(abs(y)))
    
    Y = np.array([x*mult for x in y], dtype=np.float32)
    
    return Y


# from sklearn.datasets import load_iris
# X, y = load_iris(return_X_y=True)
# clf = LogisticRegression(solver="newton-cholesky").fit(X, y)
# roc_auc_score(y, clf.predict_proba(X), multi_class='ovr')


# import numpy as np
# from sklearn.datasets import make_multilabel_classification
# from sklearn.multioutput import MultiOutputClassifier
# X, y = make_multilabel_classification(random_state=0)
# clf = MultiOutputClassifier(clf).fit(X, y)
# # get a list of n_output containing probability arrays of shape
# # (n_samples, n_classes)
# y_score = clf.predict_proba(X)
# # extract the positive columns for each output
# y_score = np.transpose([score[:, 1] for score in y_score])
# roc_auc_score(y, y_score, average=None)
# from sklearn.linear_model import RidgeClassifierCV
# clf = RidgeClassifierCV().fit(X, y)
# roc_auc_score(y, clf.decision_function(X), average=None)

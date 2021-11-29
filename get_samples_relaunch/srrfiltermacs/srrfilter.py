import pandas as pd
import numpy as np 
import os
from pathlib import Path
import shutil
import sys



def get_count(path_df):
    '''It receives a df_metadata
    and returns a df with counts per
    GSE'''

    df = pd.read_csv(path_df)
    df_gse_count = df['GSE'].value_counts().rename_axis('GSE').reset_index(name='counts') #renaming columns; dataframe type
    df_gse_count.to_csv(os.path.join(os.getcwd(), os.path.basename(path_df+'_count.txt')), header=False, index=False)

    return df_gse_count


def filter_gse_count(df_gse_count, list_gse):
    '''It receives a df with GSE and count and 
    a list of the desired GSE to explore. It will
    return a df containing the desired GSE'''

    file = open(list_gse, 'r')
    gse_list = file.readlines() #txt to list including \n
    gse_list_strip = list(map(lambda s: s.strip(), gse_list)) #removing \n for each ele
    df_filter = df_gse_count[df_gse_count['GSE'].isin(gse_list_strip)] #Ok 
    df_filter.to_csv(os.path.join(os.getcwd(), os.path.basename(list_gse+'_filtered.txt')), header=False, index=False)

    return df_filter


def get_gse_rerun(df_filter, list_macs2, logger):
    '''it receives a df_filter (launched GSEs)
    and a list of SRR.pval.bigwig to extract the
    GSEs with pval.bigwig files. It will return a 
    list of GSEs with samples to be relaunched.'''

    #working with list_macs2
    dict_gse_count = {}
    file = open(list_macs2, 'r') #get series that have pval.bw

    for line in file:
        line = line.strip()
        GSE = Path(line).parts[9] #get GSE from macs2 path 
        
        if GSE in dict_gse_count:
            dict_gse_count[GSE] += 1

        else: 
            dict_gse_count[GSE] = 1

    #working with df_filter
    dict_df_count = dict(df_filter.values) #converting our filtered_df (launched series to IHEC pipeline) to a dict
    
    #get the dict with series where all samples have the pval.bigwig files (checking the equal key,value pair between our dict_df and dict_gse containing pval bw)
    shared_items = {k: dict_gse_count[k] for k in dict_gse_count if k in dict_df_count and dict_gse_count[k] == dict_df_count[k]}
    
    print('The dictionaries were generated!')
    
    logger.info('Your dict of launched series (GSEs) using the IHEC pipeline has a length of:' + str(len(dict_df_count)))
    logger.info('Your dict of launched series (GSEs) using the IHEC pipeline containing samples with pval.bigwigs has a length of:' + str(len(dict_gse_count))) #ok
    logger.info('Your dict of completed analyzed series (GSEs) using the IHEC pipeline has a length of:' + str(len(shared_items)))
    
    #return a list of GSEs that needs to be relaunched
    set_GSE_relaunch = set(dict_df_count.keys()) - set(shared_items.keys())
    list_GSE_relaunch = list(set_GSE_relaunch)
    print('The list of GSEs to be relaunched was saved!!')
    logger.info('Saving list of GSEs to relaunch...')
    logger.info('Your list of series (GSEs) to relaunch (IHEC pipeline) has a length of:' + str(len(list_GSE_relaunch)))

    #saving list to relaunch 
    with open('gse_relaunch_file.txt', 'w') as f:
        f.write('\n'.join(list_GSE_relaunch))

    return list_GSE_relaunch
    

def create_dir_data(list_GSE_relaunch, path_gse):
    '''It receives a list of GSEs with SRR to be
    relaunched and the absolut path to the GSE dir.
    It will create a new subdir for each GSE dir
    (data_already)'''
    
    for gse in list_GSE_relaunch:
        gse = gse.strip()
        path_create = os.path.join(path_gse,gse,'data_already')
        os.mkdir(os.path.join(path_gse,gse,'data_already')) #DONE
    
        print(path_create,' created')


def create_tomove(list_macs2, list_GSE_relaunch):
    '''It receives a list_macs2 (pval) and a list
    with GSEs to relaunch. It returns a list with 
    samples to move to the new directory (data_already)
    '''

    to_move = []

    file = open(list_macs2, 'r') #get series that have pval.bw
    for line in file:
        line = line.strip()
        # print(line) ok
        for i in list_GSE_relaunch:
            # print(i)
            # print(Path(line).parts[9], i)
            if i == Path(line).parts[9]:
                to_move.append(line) #samples from GSEs to be relaunched that were analyzed successfully (series with part of the samples with pval bigwig)
                

    return to_move


def move_srr(path_gse, list_macs2, list_GSE_relaunch, logger): #to think: if paired end? 
    '''It receives a absolut path, a list of samples (pval.bw)
    and a list of GSE. It will move the samples already analyzed
    to anoter directory.'''

    to_move = create_tomove(list_macs2, list_GSE_relaunch) #creating a list of samples to move to data_already
    print(to_move)

    list_SRR_ori = []
    list_SRR_dest = []
    
    for sample in to_move: #to get list of ori and list of dest
        
        sample = sample.strip()
        SRR = os.path.basename(sample).split('merged')[0] + 'fastq.gz' #OK - SRR to move - keys of dict
        SRR_ori_path = os.path.join(path_gse,Path(sample).parts[9],'data_srr',SRR)
        list_SRR_ori.append(SRR_ori_path)
        
        GSE = Path(sample).parts[9] #getting GSE
        path_dest = os.path.join(path_gse,GSE,'data_already')
        list_SRR_dest.append(path_dest)


    for ori, dest in zip(list_SRR_ori,list_SRR_dest):
        print(ori,dest)
        try:

            shutil.move(ori,dest)
            print('File moved from source to destination')
            logger.info('File moved from source to destination') # Ok, just add the shutil cp, and after shutil mv
        
        except shutil.SameFileError:
            print('Source and destination are the same file')
            logger.info('Source and destination are the same file')

        except PermissionError:
            print('Permission denied')
            logger.info('Permission denied')

        except:
            print('An error ocurred during the process')
            logger.info('An error ocurred during the process')




def move_paired(path_gse, list_macs2, list_GSE_relaunch, logger): #it does not work with technical replicates...think about 
    '''It receives a absolut path, a list of samples (pval.bw)
    and a list of GSE. It will move the _2.gz samples already analyzed
    to anoter directory.'''

    to_move = create_tomove(list_macs2, list_GSE_relaunch) #creating a list of samples to move to data_already
    print(to_move)    

    for sample in to_move: #to get list of ori and list of dest
        
        sample = sample.strip()
        SRR = os.path.basename(sample).split('_')[0] + '_2.fastq.gz' #OK - SRR to move - keys of dict
        # print(SRR)

        GSE = Path(sample).parts[9] #getting GSE
        path_data_srr = os.path.join(path_gse,GSE,'data_srr')
        # print(path_data_srr)

        list_dir = os.listdir(path_data_srr)
        # print(list_dir)

        if SRR in list_dir:

            ori = os.path.join(path_data_srr,SRR)
            dest = os.path.join(path_gse,GSE,'data_already')

            print(ori,dest)

            try:

                shutil.move(ori,dest)
                print('File moved from source to destination')
                logger.info('File moved from source to destination') # Ok, just add the shutil cp, and after shutil mv
            
            except shutil.SameFileError:
                print('Source and destination are the same file')
                logger.info('Source and destination are the same file')

            except PermissionError:
                print('Permission denied')
                logger.info('Permission denied')

            except:
                print('An error ocurred during the process')
                logger.info('An error ocurred during the process')


        else:
            continue
            
















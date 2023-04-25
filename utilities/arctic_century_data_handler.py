# -*- coding: utf-8 -*-
"""
Created on Mon Sep 26 12:12:51 2022

@author: moallemi
"""

import os
import glob
from pathlib import Path
import pandas as pd
import numpy as np

"""

this modul is for handelling image data from arctic century

"""


def get_all_ac_img_folder_names(stereo_data_prent_path:str) -> pd.DataFrame:
    
    """
    THIS ONLY WORKS FOR ARCTIC CENTURY DATA
    
    
    Creates dataframe of the timeseries of highlevel stereo image datefolders
    with datetime index
    
    Highlevel here means all the folders (an not subforlder) in the parent 
    
    stereo image path (stereo_data_prent_path) which contains all the data from
    
    Arctic Century
    
    As of 2023-01-18 the stereo_data_prent_path is current at:
    
        X:\archive\ArcticCentury\Ocean_photos 

    argumenets: 
        
        stereo_data_prent_path (str): the parent stereo image path 
        
    output:
        
        df_high_level_folders (pd.Dataframe): time series of all high level forlders
        
    """
    
    high_level_folders = glob.glob(stereo_data_prent_path+'/*')
    high_level_folders_datetime_list = list(map(lambda data_str: pd.to_datetime(data_str.split('\\')[-1], format = '%Y-%m-%d---%H-%M'), high_level_folders))
    df_high_level_folders = pd.DataFrame(high_level_folders, index = high_level_folders_datetime_list, columns = ['folder_path'])
    
    return df_high_level_folders


def get_img_data_path_closets_to_datetime(stereo_data_prent_path:str, selected_datetime:str) -> str:
    
    """
    select the sample data path with date closest to the selected_datetime
    and extrect the data path
    
    argumenets:
        
        stereo_data_prent_path (str): the parent stereo image path 
        selected_datetime (str): is the datetime string for sample data
    
    output:
        
        sample_folder_path (str): the sample date path
    
    """
    
    # convert selected_datetime str to pd datetime format
    selected_datetime_ = pd.to_datetime((selected_datetime))
    
    #get the timeseries of all the highlevel image folders
    df_high_level_folders = get_all_ac_img_folder_names(stereo_data_prent_path)
    
    #finds the datetime index of stereo data with datetime closest to the input arg selected_datetime
    selected_folder_idx = np.argmin(np.abs(df_high_level_folders.index - selected_datetime_))
    
    #finds the foder of stereo data with datetime closest to the input arg selected_datetime
    sample_folder_path = df_high_level_folders.iloc[selected_folder_idx,0]
    
    print(f'selected date: {selected_datetime_}')
    print('')
    print(f'selected stereo data: {sample_folder_path}')
    print('')
    
    return sample_folder_path
    




def get_image_info_list(sample_folder_path, cam_name :str = 'camera1') -> pd.DataFrame:
    
    """
    
    this function takes the stereo_data_prent_path and specific sample datetime
    and camera name and for the specideid camera provides a dataframe 
    contiaing timeseries of imagedata file name, path, elapse time comapred 
    to intial image. 
    
    argumenets:
        
        stereo_data_prent_path (str): the parent stereo image path 
        selected_datetime (str): is the datetime string for sample data
        cam_name (str): camera name in arctice centure date the cam_name 
        could only be 'camera1' or 'camera0'
    
    
    """
    
    #sample_folder_path = get_img_data_path_closets_to_datetime(stereo_data_prent_path, selected_datetime)
    
    cam_name_dict = {'camera0':0, 'camera1':1}
    #image_path = str(Path(r'X:\archive\ArcticCentury\Ocean_photos'))
    #sample_date_time_file = date#'2021-08-27---15-39'
    
    try:
            

        listOfFile = [f for f in os.listdir(sample_folder_path+f'/{cam_name}') if 'tif' in f]
        cam_1_files = glob.glob(sample_folder_path+f'/{cam_name}/*tiff')
        
        # extract date time from image file names
        sample_date_time = [name[8:-5] for name in listOfFile]
        
        # make a dataframe containg image name and path info
        df = pd.DataFrame()
        
        
        df['file_name'] = listOfFile
        df['file_name_path'] = cam_1_files
        
        df['img_data_path'] = sample_folder_path+f'/{cam_name}'
        
        # create datetime index
        df.index = sample_date_time
        df.index = pd.to_datetime(df.index, format = '%Y-%m-%d---%H-%M-%S.%f')
        
        df = df.sort_index()
        
        elpased_time = ((df.index.to_series() - df.index[0]).dt.total_seconds()*1000000).values
        elpased_time[0] = 0
        elpased_time = elpased_time.astype(int)
        df['elpased_time (us)'] = elpased_time
        
        new_file_names = []
        
        j = 0
        for i, row in df.iterrows():
                
            sequ = "%06d" % (j,)
            time = "%013d" % (row['elpased_time (us)'],)
            cam_num_ = "%02d" % (cam_name_dict[cam_name],)
            
            file_name = f'{sequ}_{time}_{cam_num_}.tif'
            
            new_file_names.append(file_name)
            
            
            j += 1
        
        df['wass_image_name'] = new_file_names
        
        return df
        
    
    except FileNotFoundError:
        
        print('the data path or camera do not correspond to available data')
    
  



def sync_cams_datetimes(cam_0_dt_idx : np.datetime64, cam_1_dt_idx : np.datetime64)->tuple[np.datetime64, np.datetime64]:
    
    """
    this function provides the date time index values for cam1 and cam0 that
    are closet to each other
    
    argumenets:
        cam_0_dt_idx (np.datetime64): this the datetime index of 
        the image information dataframe, i.e, the output of get_image_info_list
        for camera0
        
        cam_1_dt_idx (np.datetime64): same as cam_0_dt_idx but for camera1
        
    returns:
        idx_sync_0: (np.datetime64): best matched datetime index of camera0 data
        to camera1 datetime index data
        
        idx_sync_1: (np.datetime64): best matched datetime index of camera0 data
        to camera1 datetime index data
        
    
    """
    # get datatime indices in df_cam_1 closest to df_cam_0 datetime index 
    idx_sync_1_dt_obj = [cam_1_dt_idx[cam_1_dt_idx.get_indexer([idx], method='nearest')[0]] for idx in cam_0_dt_idx]
    idx_sync_1 = cam_1_dt_idx[cam_1_dt_idx.isin(idx_sync_1_dt_obj)]

    # get datatime indices in df_cam_0 closest to idx_sync_1
    idx_sync_0_dt_obj = [cam_0_dt_idx[cam_0_dt_idx.get_indexer([idx], method='nearest')[0]] for idx in idx_sync_1]
    idx_sync_0 = cam_0_dt_idx[cam_0_dt_idx.isin(idx_sync_0_dt_obj)]

    # note the second step in necessary as df_cam_0.index having the same 
    # length as idx_sync_1 is not guarantied

    # Note: the lenght of idx_sync_0 and idx_sync_1 should be similar 
    # i am not sure how to handel that    
    # if len(idx_sync_0) != len(idx_sync_0):
        
    #     raise Error
    
    
    return idx_sync_1, idx_sync_0
    

def df_img_info_partitioning(df_img_info:pd.DataFrame, part_len: int = 100):

    """
    when running wass we would like to keep number of image data for a stereo 
    analysis to 100 images. this is to make sure that extrinsic data taken over
    smaller portion of the data
    
    
    This function virtually divide the input df_img_info  dataframe by the 
    partiontions with lenghts part_len. The function then provides a columns which 
    contains the part numbers in a consequtive order
    
    if the final partiontion has a lenght smaller than 10 it will be mergerd with
    partiontion-1
    
    argumenets:
        
        df_img_info: image information dataframe
        part_len: partition lenght
        
    output:
        there is no actual output rather df_img_info is upadted and part column
        is added
        
    """    

    df_img_info.loc[:,'part'] = df_img_info.groupby(np.arange(len(df_img_info.index))//part_len, axis=0).grouper.group_info[0] + 1
    
    parts = max(np.arange(len(df_img_info.index))//part_len) + 1
    
    len_last_part = df_img_info[df_img_info['part']==parts].shape[0]
    
    lower_lim = int(part_len/10)
    
    if len_last_part < lower_lim and parts>1:
        
        df_img_info.loc[df_img_info['part'] == parts, 'part'] = parts-1 


def get_parts_elapse_time(df_img_info:pd.DataFrame):
    
    """
    this function calculates the image sample elapse time for each part in the 
    df_img_info. 
    Note this function can only be applies if the df_img_info has already been 
    partitioned
    
    input: 
        df_img_info pd.DataFrame image information dataframe with partition data
    
    """
    
    try:
    
        part_lists = df_img_info['part'].unique()
        
        df_img_info.loc[:,'elpased_time (us) (parts)'] = np.nan
        
        for part in part_lists:
        
            df_part = df_img_info.loc[df_img_info['part'] == part].copy()
            parts_elapse_time = df_part['elpased_time (us)'].values - df_part['elpased_time (us)'].values[0]
            
            df_img_info.loc[df_img_info['part'] == part, 'elpased_time (us) (parts)'] = parts_elapse_time
    
    except KeyError:
        
        print('The input dataframe may not have the parts columns')
        
    
def rename_wass_col(df, cam_name, eplase_t_col = 'elpased_time (us)'):

    cam_num_dict = {'camera0':0, 'camera1':1}    

    new_file_names = []
    
    j = 0
    for i, row in df.iterrows():
            
        sequ = "%06d" % (j,)
        time = "%013d" % (row[eplase_t_col],)
        cam_num_ = "%02d" % (cam_num_dict[cam_name],)
        
        file_name = f'{sequ}_{time}_{cam_num_}.tif'
        
        new_file_names.append(file_name)
        
        
        j += 1
    
    df.loc[:,'wass_image_name'] = new_file_names






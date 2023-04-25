# -*- coding: utf-8 -*-
"""
Created on Thu Jan 19 10:53:10 2023

@author: moallemi
"""

from pathlib import Path
import sys
import datetime 
import os
import glob

#sys.path.append(str(Path(r'D:\Arctic_Century\Process_stereo_images\portable_wass_wrapper\utilities')))

sys.path.append(str(Path(r'.\utilities')))

import arctic_century_data_handler as acdh
import general_utility_functions as guf
import wass_module as wass
#import 8
import pandas as pd
import multiprocessing as mp
import tqdm #import *

"""
test delete file 
"""



def run_input_and_config_prep_single_input(input_data):
    
    wass__path_ = input_data[0]
    cal_fact_path_ = input_data[1]
    df_cam0_data_info_ = input_data[2]
    df_cam1_data_info_ = input_data[3]
    #input_data[4]
    
    part__ = input_data[4]+1
    
    
    wass__path_in = wass__path_+f'\\part_{part__}'
    print(wass__path_in)
    
    df_cam__0_ = df_cam0_data_info_.loc[df_cam0_data_info_['part'] == part__, :].copy()
    df_cam__1_ = df_cam1_data_info_.loc[df_cam1_data_info_['part'] == part__, :].copy()
    
    
    acdh.rename_wass_col(df_cam__0_, 'camera0', 'elpased_time (us) (parts)')
    acdh.rename_wass_col(df_cam__1_, 'camera1', 'elpased_time (us) (parts)')
    
    
    results = [df_cam__1_.index[0], df_cam__1_.index[-1]]
    
    print('sample slice start and end')
    
    print(df_cam__1_.index[0])
    print(df_cam__1_.index[-1])
    
    """
    make the 
    
    WASS dir test
    """
    
    WassCase = wass.WassCLass(wass__path_in)
    
    # """
    # gonfig file test
    # """
    # # put a replace key word
    # # if replace false don't delete it
    # # if replace if true delete it
    WassCase.make_wass_config_data(cal_fact_path_, query = False)
    
    # """
    # input file test
    # """
    
    WassCase.make_wass_input_data(df_cam__0_, df_cam__1_, query = False)
    
    print(results)
    
    return results #results#"done"


def main():
            

    img_info_data_path = str(Path('.\example\stereo_image_data_summary'))

    cal_fact_path = str(Path('.\calibration_and_configuration_files'))

    #for case in image_summary_datetime_list:

    case = '2021-08-18---18-30'


    work_dir_path = str(Path(f'.\example\WASS_wrk_dirs\{case}'))

    try:

        os.mkdir(work_dir_path)

    except FileExistsError:

        print("WASS working dir already exists!")


    df_test_cam_0 = pd.read_csv(f'{img_info_data_path}/cam0_image_info_summary_{case}.csv', parse_dates=True, index_col='datetime_')
    df_test_cam_1 = pd.read_csv(f'{img_info_data_path}/cam1_image_info_summary_{case}.csv', parse_dates=True, index_col='datetime_')

    parts = len(df_test_cam_0['part'].unique())
    input_data = ((work_dir_path, cal_fact_path, df_test_cam_0, df_test_cam_1, case_id) for case_id in range(parts))


    cores = 2

    pool = mp.Pool(processes=cores)

        
    results = []
    for result in tqdm.tqdm(pool.imap_unordered(run_input_and_config_prep_single_input, input_data), total=parts):
        results.append(result)
        
    

    #print(results)



if __name__ == "__main__":
    
   main()

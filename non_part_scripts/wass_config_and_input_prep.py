# -*- coding: utf-8 -*-
"""
Created on Thu Jan 19 10:53:10 2023

@author: moallemi
"""

from pathlib import Path
import sys
import datetime 
import os

sys.path.append(str(Path(r'../utilities')))
import arctic_century_data_handler as acdh
import general_utility_functions as guf
import wass_module as wass
#import 8
import pandas as pd

"""
test delete file 
"""
#make_test file

# test_dir = r'.\test_dir_del'

# guf.remove_folder(str(Path(test_dir)))
# os.mkdir(Path(test_dir))
# os.mkdir(str(Path(rf'{test_dir}/file_2')))

# #make_test file
# guf.remove_folder(str(Path(test_dir)))


"""
make the 

WASS dir test
"""

WASS_dir_test = str(Path(r'.\WASS_dir_test'))

WassCase = wass.WassCLass(WASS_dir_test)

"""
gonfig file test
"""

cal_config_data_path = str(Path(r'./calibration_and_configuration_files'))
# put a replace key word
# if replace false don't delete it
# if replace if true delete it
WassCase.make_wass_config_data(cal_config_data_path, query = False)

"""
input file test
"""

img_info_data_path = str(Path(r'./stereo_image_data_summary'))

df_test_cam_0 = pd.read_csv(f'{img_info_data_path}/cam0_image_info_summary_2021-08-15.csv', parse_dates=True, index_col='datetime_')
df_test_cam_1 = pd.read_csv(f'{img_info_data_path}/cam1_image_info_summary_2021-08-15.csv', parse_dates=True, index_col='datetime_')

df_sub_cam_0 = df_test_cam_0[df_test_cam_0['part'] == 18].iloc[:10].copy() 
df_sub_cam_1 = df_test_cam_1[df_test_cam_1['part'] == 18].iloc[:10].copy() 

acdh.rename_wass_col(df_sub_cam_0, cam_name = 'camera0', eplase_t_col = 'elpased_time (us) (parts)')
acdh.rename_wass_col(df_sub_cam_1, cam_name = 'camera1', eplase_t_col = 'elpased_time (us) (parts)')

WassCase.make_wass_input_data(df_sub_cam_0, df_sub_cam_1, query = False)



"""
output prep 
"""
#WassCase.do_prepare_parallel_autoframe(cores = 18, query = True)


 




# -*- coding: utf-8 -*-
"""
Created on Tue Jan 17 15:59:55 2023

@author: moallemi
"""

from pathlib import Path
import sys
import datetime 

sys.path.append(str(Path(r'.\utilities')))
import arctic_century_data_handler as acdh
    


if __name__ == "__main__":
    
    # Note: the directory to the image data (img_data_dir) has 
    # to contain two folders img_data_dir/camera0 and img_data_dir/camera1 

    img_data_dir = str(Path(r'.\example\sample_image_data\2021-08-18---18-30'))

    df_img_info_cam0 = acdh.get_image_info_list(img_data_dir, 
                                                    cam_name = 'camera0')
    df_img_info_cam1 = acdh.get_image_info_list(img_data_dir,
                                                    cam_name = 'camera1')
    
    
    idx_1, idx_0 = acdh.sync_cams_datetimes(df_img_info_cam0.index, df_img_info_cam1.index)
    
    df_img_info_sync_cam0 = df_img_info_cam0[df_img_info_cam0.index.isin(idx_0)].copy()
    df_img_info_sync_cam1 = df_img_info_cam1[df_img_info_cam1.index.isin(idx_1)].copy()
    
    #partition df_img_info_sync_cam0 with base partition lenght of 100 images
    part_len = 360 #~ 3min
    
    acdh.df_img_info_partitioning(df_img_info_sync_cam0, part_len)
    
    #parts elapse time calculations
    acdh.get_parts_elapse_time(df_img_info_sync_cam0)
    
    
    #partition df_img_info_sync_cam1 with base partition lenght of 100 images
    acdh.df_img_info_partitioning(df_img_info_sync_cam1, part_len)
    
    #parts elapse time calculations
    acdh.get_parts_elapse_time(df_img_info_sync_cam1)
    
    # set index col name
    df_img_info_sync_cam0.index.name = 'datetime_'
    df_img_info_sync_cam1.index.name = 'datetime_'
    
    # #save the data in WASS parent dir
    dt = df_img_info_sync_cam0.index[0]
    sample_file_date = datetime.datetime(dt.year, dt.month, dt.day, dt.hour, dt.minute).strftime("%Y-%m-%d---%H-%M")
    wass_parent_dit = './example/stereo_image_data_summary'
    
    
    df_img_info_sync_cam0.to_csv(f'{wass_parent_dit}/cam0_image_info_summary_{sample_file_date}.csv')
    df_img_info_sync_cam1.to_csv(f'{wass_parent_dit}/cam1_image_info_summary_{sample_file_date}.csv')


    print(f'cam0 len:{len(df_img_info_sync_cam0)}')
    print(f'cam1 len:{len(df_img_info_sync_cam1)}')


# Note: 
# when processing image data from arctic century the user can obtain
# the data path temporally closest to the available data using
# get_img_data_path_closets_to_datetime(img_data_parent_dir, img_data_sample_datetime)
# The following code snippet could be use to extract the proper image data:

## the parent directory to all arctic century image data 
#img_data_parent_dir = str(Path(r'...'))

#img_sample_datetime_list = ['2021-08-27 03:50:00']

#for img_data_sample_datetime in img_sample_datetime_list:
    
    #img_data_dir = get_img_data_path_closets_to_datetime(img_data_parent_dir, img_data_sample_datetime)

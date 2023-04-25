# -*- coding: utf-8 -*-
"""
Created on Thu Jan 19 13:19:44 2023

@author: moallemi
"""



from pathlib import Path
import sys
import datetime 
import os
import glob

sys.path.append(str(Path(r'./utilities')))
import arctic_century_data_handler as acdh
import general_utility_functions as guf
import wass_module as wass
#import 8
import pandas as pd




def main():
    
    WASS_analysis_dir = str(Path('D:\Arctic_Century\Process_stereo_images\WASS_wrk_dirs'))
    image_summary_datetime_list = ['2021-08-27---03-50', '2021-08-27---12-37',
                                    '2021-08-27---13-35', '2021-08-27---14-38',
                                    '2021-08-27---15-39', '2021-08-27---16-35',
                                    '2021-08-27---17-31', '2021-08-27---18-27',
                                    '2021-08-27---19-23', '2021-08-27---20-18']
                                     
    
    
    # ['2021-08-14---11-52', '2021-08-14---23-39',
    #                                 '2021-08-15---12-00', '2021-08-15---20-34',
    #                                 '2021-08-16---00-20', '2021-08-16---11-46',
    #                                 '2021-08-17---00-16', '2021-08-17---11-41',
    #                                 '2021-08-17---23-49', '2021-08-18---11-41',
    #                                 '2021-08-19---00-19']
                                   
                                   #'2021-08-14---11-52']#,     
    
    do_wass_out_prep = False
    do_wass_matching = False
    do_wass_autocali = False
    do_wass_stereo = True
    
    
    for sample_data in image_summary_datetime_list:
        
        WASS_dir_main_ = f'{WASS_analysis_dir}//{sample_data}'
        
        
        WASS_dir_main_content = glob.glob(str(f'{WASS_dir_main_}/*/'), recursive = True)
        
        get_part = lambda x: x.split('\\')[-2] 
        parts = list(map(get_part, WASS_dir_main_content))
        
    
        for part in parts:
            
            WASS_dir_test = f'{WASS_dir_main_}/{part}'
            
            print(WASS_dir_test)
            
            WassCase = wass.WassCLass(WASS_dir_test)
            
            if do_wass_out_prep:
                WassCase.do_prepare_parallel_autoframe(cores = 20, query = True)
                
            if do_wass_matching:
                WassCase.do_match_parallel_autoframe(cores = 20)
            
            if do_wass_autocali:
                WassCase.do_autocalibrate()
            
            if do_wass_stereo:
                WassCase.do_stereo_parallel()
            
        
        
    
    
if __name__ == '__main__':
    
    main()
# -*- coding: utf-8 -*-
"""
Created on Thu Jan 19 13:19:44 2023

@author: moallemi
"""



from pathlib import Path
import sys
import datetime 
import os

sys.path.append(str(Path(r'./utilities')))
import arctic_century_data_handler as acdh
import general_utility_functions as guf
import wass_module as wass
#import 8
import pandas as pd




def main():

    WASS_dir_test = str(Path(r'.\test_wass_module\WASS_dir_test'))
    WassCase = wass.WassCLass(WASS_dir_test)
    
    do_wass_out_prep = True #False
    do_wass_matching = True #False
    do_wass_autocali = True #False
    do_wass_stereo = False #True
    
    if do_wass_out_prep:
        WassCase.do_prepare_parallel_autoframe(cores = 18, query = True)
        
    if do_wass_matching:
        WassCase.do_match_parallel_autoframe(cores = 18)
    
    if do_wass_autocali:
        WassCase.do_autocalibrate()
    
    if do_wass_stereo:
        WassCase.do_stereo_parallel()
    
        
    
    
if __name__ == '__main__':
    
    main()
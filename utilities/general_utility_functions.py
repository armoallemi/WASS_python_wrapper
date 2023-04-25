# -*- coding: utf-8 -*-
"""
Created on Mon Jan 16 18:25:59 2023

@author: moallemi
"""

import sys
from shutil import copyfile
import os
import shutil


def copy_paste(src_dir, dst_dir, src_file_names_list, dst_file_names_list = []):
    
    """
    this function copy specified file names (original_file_names_list) from original_dir to destination_dir
    
    the user can specify a list of new file names (destination_file_names_list) which corresponds to the original_file_names_list  
    
    if the file names in destination_file_names_list has to be changed according to destination_file_names_list
    
    by default destination_file_names_list is set to [] and this means that the destination_file_names_list is euqal to 
    
    original_file_names_list
    
    """
    
    if dst_file_names_list == []:
        
        # print("Note: destination_file_names_list not specified,")
        # print("therefor by default destination_file_names_list is set")
        # print("equal to original_file_names_list")
        
        dst_file_names_list = src_file_names_list
        
    # check if original_file_names_list and destination_file_names_list have the same lengths
    
    if not (len(dst_file_names_list) == len(src_file_names_list)):
        
        print("the size of orignal and detination file name does not match")
        print("make sure that the ")
        
        return sys.exit(-1)
    
    
    # rename and copy 
    for src_filename, dst_filename in zip(src_file_names_list,dst_file_names_list):
    
        
        #target_filename = filename.replace("xls", "xlsx")
        src_filename_path = src_dir+'/'+src_filename
        
        copyfile(src_filename_path, os.path.join(dst_dir, dst_filename))
        
        

def yes_no_query(query_str):
    
    while True: 
     query = input(query_str) 
     Fl = query[0].lower() 
     if query == '' or not Fl in ['y','n', 'yes', 'no']: 
        print('Please answer with yes or no!') 
     else: 
         break 
     
    if Fl == 'y': 
        return True
    if Fl == 'n': 
        return False

   
def remove_folder(file_path):

    shutil.rmtree(file_path, ignore_errors=True)
    #os.mkdir(file_path)
    
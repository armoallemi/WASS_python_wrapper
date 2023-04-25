# -*- coding: utf-8 -*-
"""
Created on Wed Jan 18 14:11:50 2023

@author: moallemi
"""


import os
import sys
import glob
import tqdm
import colorama
import subprocess
import numpy as np
import multiprocessing as mp

import pandas as pd
import cv2

from pathlib import Path

sys.path.append(str(Path(r'./utilities')))
import general_utility_functions as guf
import img_processing_functions as ipf


VERSION = "0.0.1"


WASS_PIPELINE_PATH = str(Path(r'./wass_executables'))

WASS_PIPELINE = {
    "wass_prepare": WASS_PIPELINE_PATH+'/wass_prepare.exe',
    "wass_match": WASS_PIPELINE_PATH+'/wass_match.exe',
    "wass_autocalibrate": WASS_PIPELINE_PATH+'/wass_autocalibrate.exe',
    "wass_stereo": WASS_PIPELINE_PATH+'/wass_stereo.exe'
}
SUPPORTED_IMAGE_FORMATS = ["tif", "tiff", "png", "jpg", "jpeg"]

CALIB_CONFIG_FILES = ["intrinsics_00.xml", "intrinsics_01.xml", "distortion_00.xml", "distortion_01.xml"]

"""
global functions
"""

def get_all_folders(path:str):
    
    folder_content = []

    for root, dirs, files in os.walk(path):
        
        folder_content.append(root)
        
    return folder_content


def get_image_files( directory ):

    for extension in SUPPORTED_IMAGE_FORMATS:
        imgfiles = glob.glob( "%s/*.%s"%(directory,extension))
        if len(imgfiles)>1:
            return sorted(imgfiles)
    return []


class WassCLass:
    
    def __init__(self, wrk_dir:str):
        
        """
        arguments:
            
            wrk_dir (str): the path to the working directroy to run wass analysis
    
        """
        
        self.wrk_dir = wrk_dir
        self.file_flags = {'wrk_dir': False, 'config' : False,
                           'input' : False, 'output' : False}
        
        
        # all possible wass working dirs
        self.wass_main_wrk_dir = self.wrk_dir
        self.wass_config_dir = f'{self.wass_main_wrk_dir}\\config'
        self.wass_input_dir = f'{self.wass_main_wrk_dir}\\input'
        self.wass_output_dir = f'{self.wass_main_wrk_dir}\\output'
        
        # all existing dirs in wass working dirs
        self.folder_content = get_all_folders(self.wass_main_wrk_dir)
        
        self.assess_working_dir()
        
        if not self.file_flags['wrk_dir']:
            
            #self.mk_wass_main_dir()
            os.mkdir(self.wass_main_wrk_dir)
    
    def assess_working_dir(self):
        
        #
        
        folder_content = get_all_folders(self.wass_main_wrk_dir)
        
        self.file_flags['wrk_dir'] = self.wass_main_wrk_dir  in self.folder_content
        self.file_flags['config'] = self.wass_config_dir  in self.folder_content
        self.file_flags['input'] = self.wass_input_dir  in self.folder_content
        self.file_flags['output'] = self.wass_output_dir  in self.folder_content
        
        
        for key in self.file_flags.keys():
            
            response = 'does not exist'
            
            if self.file_flags[key]:
                
                response = 'exists'
        
            print(f'WASS {key} folder {response}')    
            
    
    def query_and_remove(self, component_key : str, component_path : str, query : bool = True):
        
        # component_keys are one of these ['config', 'input', 'output']
        key = component_key
        
        if self.file_flags[key]:
            
            del_cond = True # replace
                        
            if query:
            
                query_message = f'{component_path}, may contain data, do you want to delete it?'    
                del_cond = guf.yes_no_query(query_message)
            
            
            
            if del_cond:
                
                guf.remove_folder(component_path)
                self.file_flags[key] = False

    # def mk_wass_main_dir(self):
    #     # make a workin
        

    
    def make_wass_config_data(self, cal_config_data_path : str, query:bool = True):
        
        """
        a function that creates the wass config directory
        and puts the proper calibration and config files there
        """
        
        self.query_and_remove(component_key = 'config', component_path = self.wass_config_dir, query = query)
        
        if not self.file_flags['config']:
        
            #make directory
            config_path = self.wass_config_dir
            os.mkdir(f"{config_path}")
            
            #copy and paste all config and calibration files from source file to wass config folder
            cal_and_config_file_list = ['intrinsics_00.xml', 'intrinsics_01.xml', 'distortion_00.xml',
                                         'distortion_01.xml', 'matcher_config.txt', 'stereo_config.txt']
            
            print('placing cal factors from specified paths to wass path')
            guf.copy_paste(src_dir = cal_config_data_path, dst_dir = config_path, src_file_names_list = cal_and_config_file_list)
            
            # check if all the configs are included
            wass_conf_list =  [file.split('\\')[-1] for file in glob.glob(config_path+'/*')]
            if not all(item in wass_conf_list for item in cal_and_config_file_list):
                
                print("Intrinsic cal factors are not complete, make sure all cal factor files are in wass config directory. Exiting the program ...")
                sys.exit(-1)
            
            # update the config dir flag status
            self.file_flags['config'] = True
         
        else:
            
            print('WASS input already exists and are unchanged')

    
    def make_wass_input_data(self, df_cam_0 : pd.DataFrame, df_cam_1 : pd.DataFrame, deblur = True, query:bool = True):
        
        
        """
        a function that creates the wass input directories for cam1 and cam0
        and place the image data in the wass input directories 
        """
        
        self.query_and_remove(component_key = 'input', component_path = self.wass_input_dir, query = query)
        
        if not self.file_flags['input']:
            
            input_path = self.wass_input_dir
            os.mkdir(f"{input_path}")
            
            #make input directories
            input_cam0_path = f'{input_path}\\cam0'
            os.mkdir(f"{input_cam0_path}")
        
            input_cam1_path = f'{input_path}\\cam1'
            os.mkdir(f"{input_cam1_path}")
        
            # specify the image data source path and destination path
            # for each camera case
            
            cam_0_data_dir = df_cam_0['img_data_path'].iloc[0]
            cam_1_data_dir = df_cam_1['img_data_path'].iloc[0]
            
            
            img_data_list_cam0 = list(df_cam_0['file_name'].values)
            img_data_list_cam1 = list(df_cam_1['file_name'].values)
            
            WASS_img_data_list_cam0 = list(df_cam_0['wass_image_name'].values)
            WASS_img_data_list_cam1 = list(df_cam_1['wass_image_name'].values)
        
        
        
            # display number of samples
            cam0_files_num = len(glob.glob(f'{input_cam0_path}/*'))
            cam1_files_num = len(glob.glob(f'{input_cam1_path}/*'))
        
            print("input data already exists and may have data")
            print(f"there are {cam0_files_num} files for cam0")
            print(f"there are {cam1_files_num} files for cam1")
            
            
            if not deblur:
                print("placing image data in input paths without debluring cam 1 data")
                
                # copy and paste image data from source to wass directories    
                guf.copy_paste(src_dir = cam_0_data_dir, dst_dir = input_cam0_path, 
                            src_file_names_list = img_data_list_cam0, 
                            dst_file_names_list = WASS_img_data_list_cam0)
                
                guf.copy_paste(src_dir = cam_1_data_dir, dst_dir = input_cam1_path, 
                            src_file_names_list = img_data_list_cam1, 
                            dst_file_names_list = WASS_img_data_list_cam1)
                
                # update the config dir flag status
                self.file_flags['input'] = True
                
            else:
                
                print("placing image data in input paths with debluring cam 1 data")
                
                
                guf.copy_paste(cam_0_data_dir, dst_dir = input_cam0_path, 
                            src_file_names_list = img_data_list_cam0, 
                            dst_file_names_list = WASS_img_data_list_cam0)
                
                for i ,img_name_i in enumerate(img_data_list_cam1):
                    
                    img_i = cv2.imread(cam_1_data_dir+'/'+img_name_i) 
                    # the arguments for the unsharp_mask made 
                    deblur_img_i = ipf.unsharp_mask(img_i, kernel_size=(11, 11), sigma=5, amount=3)
                    cv2.imwrite(input_cam1_path + '/' + WASS_img_data_list_cam1[i], deblur_img_i)
        
                # update the config dir flag status
                self.file_flags['input'] = True

        """
        
        following codes are for runing wass
        
        """

    
    def run_wass_prepare(self, input_data):
        
        wass_wrk_dir = input_data[0]
        cam0_files = input_data[1]
        cam1_files = input_data[2]
        case_idx = input_data[3]
        
        wdirname = f"{wass_wrk_dir}/output/%06d_wd"%case_idx
        
        print(case_idx)
        
        ret = subprocess.run([WASS_PIPELINE["wass_prepare"],"--workdir", wdirname, "--calibdir", f"{wass_wrk_dir}/config/", "--c0", cam0_files[case_idx], "--c1", cam1_files[case_idx]], capture_output=True )
        
        if ret.returncode != 0:
            # print( colorama.Fore.RED+("ERROR while running wass_prepare on frame %06d ****************"%case_idx)+colorama.Style.RESET_ALL)
            # print(ret.stdout.decode("ascii"))
            # print( colorama.Fore.RED+("*********************************************************************")+colorama.Style.RESET_ALL)
            print( colorama.Fore.RED+("ERROR while running wass_prepare on frame %06d ****************"%case_idx)+colorama.Style.RESET_ALL)
            
            # return Exception
    
        return ret.returncode#, case_idx
    
    
    def do_prepare_parallel_autoframe(self, cores = 15, query = True):
    
        
        
    
        self.query_and_remove(component_key = 'output', component_path = self.wass_output_dir, query = query)
        
        if self.file_flags['output']:
            
            print('*** The output files seem to already exist in the working directroy')
            print('*** Stereo output prep did not run')
            print('*** Make sure to check and remove files from output before running')
            print('*** Check the output key in self.file_flags if you think this is not correct')
            
            return False
            
        else:
            
            os.mkdir(f"{self.wass_output_dir}")
            wass_wrk_dir = self.wass_main_wrk_dir
            
            # this is redundant but cant be fixed now
            
            if len(os.listdir(f"{wass_wrk_dir}/output/")) != 0:
                print( colorama.Fore.RED+"ERROR: "+colorama.Style.RESET_ALL, end="")
                print("output/ directory must be empty to continue. Please manually remove all the content before attempting to prepare again.")
                
                return False
        
        
            print("Checking calibration files...")
            for calib_file in CALIB_CONFIG_FILES:
                if not os.path.exists( f'{wass_wrk_dir}/config/'+calib_file ):
                    print( colorama.Fore.RED+"ERROR: "+colorama.Style.RESET_ALL, end="")
                    print( "%s not found, aborting"%calib_file )
                    return False
        
            print("Checking input/cam0 and input/cam1...")
            cam0_files = get_image_files(f"{wass_wrk_dir}/input/cam0")
            cam1_files = get_image_files(f"{wass_wrk_dir}/input/cam1")
        
            if len(cam0_files) == 0:
                print( colorama.Fore.RED+"ERROR: "+colorama.Style.RESET_ALL, end="")
                print("No image found in input/cam0 with the following formats: ", SUPPORTED_IMAGE_FORMATS)
                return False
        
            if len(cam1_files) == 0:
                print( colorama.Fore.RED+"ERROR: "+colorama.Style.RESET_ALL, end="")
                print("No image found in input/cam1 with the following formats: ", SUPPORTED_IMAGE_FORMATS)
                return False
        
            if len(cam0_files) != len(cam1_files):
                print( colorama.Fore.RED+"ERROR: "+colorama.Style.RESET_ALL, end="")
                print("cam0 and cam1 directories contain a different set of images. Aborting")
                return False
        
            N = len(cam0_files)
            print(colorama.Fore.GREEN+("%d"%N)+colorama.Style.RESET_ALL+" stereo pairs found!")
        
            while True:
                try:
                    number1 = N#int(input(f'How many stereo frames do you want to prepare? (3 ... {N}): '))
                    print(f'prepare for {N} stereo frames')
                    
                    if number1 < 3 or number1 > N:
                        
                        raise ValueError #this will send it to the print message and back to the input option
                    break
                except ValueError:
                    print(f"Invalid integer. The number must be in the range of 3-{N}.")
        
            print("Running wass_prepare... please be patient")

        
            input_data = ((wass_wrk_dir, cam0_files, cam1_files, case_id) for case_id in range(number1))
            #result = list()
            
            
            pool = mp.Pool(processes=cores)
            results = []
            for result in tqdm.tqdm(pool.imap_unordered(self.run_wass_prepare, input_data), total=number1):
                results.append(result)
            

            if np.any(results):
                
                print(result)
                
                return False
            
            # print(f'time took: {time.monotonic() - start:.1f}')
            # print(result)
        
        
        
            print( colorama.Fore.GREEN+("Prepare completed!")+colorama.Style.RESET_ALL)
            return True
    

            
    def run_wass_match(self, input_data):
        
        wrk_dir = input_data[0]
        case_id = input_data[1] 
        
        filedirname = f"{wrk_dir}/output/%06d_wd"%case_id
    
        ret = subprocess.run( [WASS_PIPELINE["wass_match"], f"{wrk_dir}/config/matcher_config.txt", filedirname], capture_output=True )
        
        if ret.returncode != 0:
            print( colorama.Fore.RED+("ERROR while running wass_prepare on frame %06d ****************"%case_id)+colorama.Style.RESET_ALL)
    
        return ret.returncode#, case_idx

    
    
    def do_match_parallel_autoframe(self, cores = 10):
        
        """
        
        questions: I am not sure of parallelizing this process is a valid act?
        
        what happens if we have less than workdirs selected frames? 
        
        not sure if two subsequent multiprocessing is a good idea
        
        """
        
        wass_wrk_dir = self.wass_main_wrk_dir
        
        workdirs = sorted(glob.glob(f"{wass_wrk_dir}/output/*_wd"))
        
        #workdirs = get_workdirs()
        # if workdirs is None: return False
    
        
        suggested_num_to_match = min(20, len(workdirs))
        
        
        print('test code')
        
        while True:
            try:
                number1 = suggested_num_to_match #int(input(f'How many stereo frames do you want to prepare? (1 ... to {suggested_num_to_match}): '))
                
                print(f'matching {number1} stereo frames')
                
                if number1 < 1 or number1 > suggested_num_to_match:
                    
                    raise ValueError #this will send it to the print message and back to the input option
                break
            except ValueError:
                print(f"Invalid integer. The number must be in the range of 1-{suggested_num_to_match}.")
        
    
        indices = np.random.permutation( len(workdirs) )[ :int(number1)]
        print("Matcher will use the following frames: ", indices)
        print("Running wass_match... please be patient")
        
    
        input_data = ((wass_wrk_dir, indices[case_id]) for case_id in range(number1))
        #result = list()
        
        
        pool = mp.Pool(processes=cores)
        results = []
        for result in tqdm.tqdm(pool.imap_unordered(self.run_wass_match, input_data), total=number1):
            results.append(result)
        
        if np.any(results):
            
            print(result)
            
            return False
        
    
        print( colorama.Fore.GREEN+("Match completed!")+colorama.Style.RESET_ALL)
        return True
    
    
    
    def do_autocalibrate(self):
        
        wass_wrk_dir = self.wass_main_wrk_dir  
        
        workdirs = sorted(glob.glob(f"{wass_wrk_dir}/output/*_wd"))
        
        if workdirs is None: 
            
            return False
        
    
        with open(f'{wass_wrk_dir}/output/workspaces.txt', 'w') as f:
            f.write('\n'.join(workdirs))
    
        print("Running wass_autocalibrate... please be patient")
        ret = subprocess.run( [WASS_PIPELINE["wass_autocalibrate"], f"{wass_wrk_dir}/output/workspaces.txt"], capture_output=True )
        if ret.returncode != 0:
            print( colorama.Fore.RED+("ERROR while running wass_autocalibrate ****************")+colorama.Style.RESET_ALL)
            print(ret.stdout.decode("ascii"))
            print( colorama.Fore.RED+("*******************************************************")+colorama.Style.RESET_ALL)
            return False
        else:
            tqdm.tqdm.write(ret.stdout.decode("ascii"))
            print( colorama.Fore.GREEN+("Autocalibrate completed!")+colorama.Style.RESET_ALL)
        
        return True
    
    
    
    
    def run_wass_stereo(self, input_data):
        
        
        wrk_dir = input_data[0]
        case_id = input_data[1] 
        
        
        wdirname = f"{wrk_dir}\output\%06d_wd"%case_id
        
        ret = subprocess.run( [WASS_PIPELINE["wass_stereo"],f"{wrk_dir}\config\stereo_config.txt", wdirname ], capture_output=True )
        if ret.returncode != 0:
            print( colorama.Fore.RED+("ERROR while running wass_stereo on frame %06d ****************"%case_id)+colorama.Style.RESET_ALL)
            print(ret.stdout.decode("ascii"))
            print( colorama.Fore.RED+("*********************************************************************")+colorama.Style.RESET_ALL)
            
            
        return ret.returncode
    
    
    def do_stereo_parallel(self, cores = 15):
        
        """
        this code runs stereo process for all the available frames
        """
        
        wass_wrk_dir = self.wass_main_wrk_dir
        
        workdirs = sorted(glob.glob(f"{wass_wrk_dir}/output/*_wd"))
        
        if workdirs is None: 
            
            return False
        
        number1 = len(workdirs)
        
        input_data = ((wass_wrk_dir, case_id) for case_id in range(number1))
        
        print("Running wass_stereo... please be patient")
        
        pool = mp.Pool(processes=cores)
        results = []
        for result in tqdm.tqdm(pool.imap_unordered(self.run_wass_stereo, input_data), total=number1):
            results.append(result)
        
        if np.any(results):
            
            print(result)
            
            return False
        
        
        print( colorama.Fore.GREEN+("Stereo completed!")+colorama.Style.RESET_ALL)
        
        return True
        




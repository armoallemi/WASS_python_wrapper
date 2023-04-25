## WASS_python_wrapper

Waves Acquisition Stereo System ([WASS](https://sites.google.com/unive.it/wass)) is an open-source software developed Filippo Bergamasco and Alvise Benetazzo. By processing pairs of ocean surface stereo images taken from marine platforms (vessels and fixed platforms), WASS provides the 3D reconstruction of ocean surface and point cloud of ocean surface elevation ([Bergamasco et al., 2016](https://doi.org/10.1016/j.cageo.2017.07.001)). 

Given that one does not want to modify the source code, WASS can typically be used through its precompiled executable files. The WASS_python_wapper is package which is designed to facilitate running WASS through a python wrapper. 

The wrapper is designed to do streamline the following tasks:   

1) Input image data and configuration files 
2) Run image-based extrinsic calibration process 
3) Run the stereo reconstruction process

The require packages to run the python wrapper are: 

* numpy
* pandas
* opencv
* tqdm
* multiprocess
* subprocess
* colorama

__note__: WASS has four main executable files (`wass_prepare.exe`, `wass_match.exe`, `wass_autocalibrate.exe`, `wass_stereo.exe`) that are required for running the wrappers. In this repository, we provided the 1.7 version executable files, however, in the future the users could simply download the updated versions of the executables from WASS webpage and use them along with WASS_python_wrapper.     


Each of these components are explained in the following sections:

### Input image data and configuration files

Proper extraction of wave related properties require 10-20 min continuous measurements of ocean surface data. Therefore, a given data point typically consists of a collection of ocean surface image pairs acquired over a 10 to 20 min time interval. As explained in [WASS webpage](https://sites.google.com/unive.it/wass), to properly run WASS a certain working directory structure has to be followed for each data point of image pair collection.  

The first step to generate the proper input data is through the image_data_specification.py. In this script the paths to camera0 and camera1 data for a given sample point is specified, then the code will generate a csv file which contains paths, image names, elapsed time of the image sample and corresponding WASS format image name. Under certain condition the user may want to split the image data in a given sample point to different parts with n number of images per part. The code also allows the used to specify such "subsample parts" given the number of image per parts. Each part will then be processed as a separate WASS working directory. 

The next step is the construction of the WASS working directory and inclusion of image input data and config file in that directory. This is done through the wass_config_and_input_prep_multi_part.py script. In this script the user will specify a parent WASS working directory for the sample. By going through the csv file generated by image_data_specification.py, the script will create working directories for each "subsample part" and insert the image data with proper naming format in the corresponding input folders for camera0 and camera1. The wass_config_and_input_prep_multi_part.py also generate the config folder and insert the intrinsic calibration factors of cameras and WASS setting configuration there. The path to intrinsic calibration and config files has to be specified by the user in the wass_module.py (located in the utility folder). The wass_module contains the class and methods to be used for running the WASS related operations. 

If the input and config data are already available in proper WASS format the user can skip the __Input image data and configuration files__ step. 

### Run image-based extrinsic calibration process
In this step the wass_output_calibration_multi_part code will do the following:

Firstly, given the path to WASS working directory, the code generates a WASS class which automatically checks if the input and config files are properly defined in the working directory. If the input and config files are not defined properly the code will spit an error message and stop. Next given that the `do_wass_out_prep` flag variable is `True`, the code will check the availability of the output folder and ask the user if the want to delete it and generate a new output folder. Given that the output folder does not exist the code will execute `wass_prepare.exe` which generates the output folder and proper output sample sub-folders according to WASS convention. The code can do this operation in parallel and the user can specify the number of cores to use for running the wass_prepare operation. 

If the `do_wass_matching` flag variable is `True`, the code will execute the WASS `wass_match.exe`. By default in the wass_module package the WASS match will be operated on randomly selected images with the number of random images being the max(number_of_image_pairs, 20). The value of 20 can be changes by the user if they require more images for the calibration operation. 

If the `do_wass_autocali` flag variable is `True`, the code will execute the WASS `wass_autocalibrate.exe`. This operation will use the outputs from `do_wass_matching` step to obtain the extrinsic calibration factors. 


### Run the stereo reconstruction process

In this step given that the input data, config files, and extrinsic calibration factors are known, the stereo reconstruction process will be carried out. 

The script for running this step is the same as `wass_output_calibration_multi_part.py` with the `do_wass_stereo` flag set to `True`. The code will run `wass_stereo.exe` in parallel over output folders. 



## Notes and possible future modifications 
In the current code we use the wass_module which basically define a wass class containing information on input, config, and output files for each WASS working directory. While this approach is convinent of a given stereo sample point (containing a collection of stereo image data) running multiple sample points in parallel may require modification and even full alteration of the wass_module. This can be done in future versions of the WASS_python_wrapper.  
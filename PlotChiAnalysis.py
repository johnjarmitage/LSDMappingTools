#=============================================================================
# Script to plot chi analysis. 
#
# Authors:
#   Simon M. Mudd  
#   Fiona J. Clubb
#=============================================================================
#=============================================================================
# IMPORT MODULES
#=============================================================================
# set backend to run on server
import matplotlib
matplotlib.use('Agg')

#from __future__ import print_function
import sys
import os
from LSDPlottingTools import LSDMap_MOverNPlotting as MN
import LSDMapWrappers as LSDMW
from LSDMapFigure import PlottingHelpers as phelp
import LSDPlottingTools as LSDP
from osgeo import ogr



#=============================================================================
# This is just a welcome screen that is displayed if no arguments are provided.
#=============================================================================
def print_welcome():

    print("\n\n=======================================================================")
    print("Hello! I'm going to plot chi analysis results for you.")
    print("You will need to tell me which directory to look in.")
    print("Use the -dir flag to define the working directory.")
    print("If you don't do this I will assume the data is in the same directory as this script.")
    print("For help type:")
    print("   python PlotChiAnalysis.py -h\n")
    print("=======================================================================\n\n ")

#=============================================================================
# This parses a comma separated string
#=============================================================================    
def parse_list_from_string(a_string):
    if len(a_string) == 0:
        print("No items found, I am returning and empty list.")
        return_list = []
    else:
        return_list = [int(item) for item in a_string.split(',')]
        print("The parsed string is:")
        print(return_list)
        
    return return_list

#=============================================================================
# This parses a dict separated string
#=============================================================================    
def parse_dict_from_string(a_string):
    if len(a_string) == 0:
        print("No rename dictionary found. I will return and empty dict.")
        this_rename_dict = {}
    else:
        listified_entry = [item for item in a_string.split(',')]
        this_rename_dict = {}
        
        # now loop through these creating a dict
        for entry in listified_entry:
            split_entry = entry.split(":")
            this_rename_dict[int(split_entry[0])]=split_entry[1]
    
    print("The parsed dict is: ")
    print(this_rename_dict)
    return this_rename_dict

#=============================================================================
# This parses a list of lists separated string. Each list is separated by a colon
#=============================================================================    
def parse_list_of_list_from_string(a_string):
    
    if len(a_string) == 0:
        print("No list of list found. I will return an empty list.")
        list_of_list = []
    else:
        listified_entry = [item for item in a_string.split(':')]
        list_of_list = []
        
        # now loop through these creating a dict
        for entry in listified_entry:
            split_entry = [int(item) for item in entry.split(',')]
            list_of_list.append(split_entry)
    
    print("This list of lists is: ")
    print(list_of_list)
    
    return list_of_list

#=============================================================================
# This takes the basin stack list and then gives each basin in a stack layer
# a constant value. Used for plotting. 
#=============================================================================  
def convert_basin_stack_to_value_dict(basin_stack_list):
    
    N_stacks = len(basin_stack_list)
    print("The number of stacks are: "+ str(N_stacks))
    if len(basin_stack_list) == 0:
        this_value_dict = {}
    else:
        this_value_dict = {}
        for idx,stack in enumerate(basin_stack_list):
            value = float(idx)/float(N_stacks)
            for item in stack:
                this_value_dict[item] = value
    return this_value_dict
                

#=============================================================================
# This pads an offset list so it is the same size as the basin list
#=============================================================================     
def pad_offset_lists(basin_stack_list,offset_list):
    
    # I need to check chi the offsets
    n_basin_stacks = len(basin_stack_list)
    if len(offset_list) == 0:
        const_offset = 5
    else:
        const_offset = offset_list[-1]
    final_offsets = offset_list
    if len(offset_list) < n_basin_stacks:
        final_offsets = offset_list + [const_offset]*(n_basin_stacks - len(offset_list))
    else:
        final_offsets = offset_list

    print("Initial offsets are: ")
    print(offset_list)
    print("And const offset is: "+str(const_offset))
    print("Final offset is: ")
    print(final_offsets)
    
    return final_offsets
    
    
    
#=============================================================================
# This is the main function that runs the whole thing
#=============================================================================
def main(argv):

    # If there are no arguments, send to the welcome screen
    if not len(sys.argv) > 1:
        full_paramfile = print_welcome()
        sys.exit()

    # Get the arguments
    import argparse
    parser = argparse.ArgumentParser()
    # The location of the data files
    parser.add_argument("-dir", "--base_directory", type=str, help="The base directory with the m/n analysis. If this isn't defined I'll assume it's the same as the current directory.")
    parser.add_argument("-fname", "--fname_prefix", type=str, help="The prefix of your DEM WITHOUT EXTENSION!!! This must be supplied or you will get an error (unless you're running the parallel plotting).")
    parser.add_argument("-out_fname", "--out_fname_prefix", type=str, help="The prefix of the figures WITHOUT EXTENSION!!! If not supplied the fname prefix will be used.")

    # Selecting and renaming basins
    parser.add_argument("-basin_keys", "--basin_keys",type=str,default = "", help = "This is a comma delimited string that gets the list of basins you want for the plotting. Default = no basins")  
    parser.add_argument("-rename_dict", "--rename_dict",type=str,default = "", help = "This is a string that initiates a dictionary for renaming basins. The different dict entries should be comma separated, and key and value should be separated by a colon. Default = no dict")   
    parser.add_argument("-basin_lists", "--basin_lists",type=str,default = "", help = "This is a string that initiates a list of a list for grouping basins. The object becomes a list of a list but the syntax is comma seperated lists, and each one is separated by a colon. Default = no dict")
    parser.add_argument("-chi_offsets", "--chi_offsets",type=str,default = "", help = "This is a string that initiates a list of chi offsets for each of the basin lists. Default = no list")
    parser.add_argument("-fd_offsets", "--flow_distance_offsets",type=str,default = "", help = "This is a string that initiates a list of flow distance offsets for each of the basin lists. Default = no list")
    
    
    # What sort of analyses you want
    parser.add_argument("-PB", "--plot_basins", type=bool, default=False, help="If this is true, I'll make a simple basin plot.")    
    parser.add_argument("-PC", "--plot_chi_coord", type=bool, default=False, help="If this is true, I'll make a chi coordinate plot.")  
    parser.add_argument("-all", "--all_chi_plots", type=bool, default=False, help="If this is true, I'll make all the plots including raster and chi profile plots.")
    parser.add_argument("-all_rasters", "--all_raster_plots", type=bool, default=False, help="If this is true, I'll make all the raster plots.")
    parser.add_argument("-all_stacks", "--all_stacked_plots", type=bool, default=False, help="If this is true, I'll make all the stacked plots.")
    
    # Some simple geographic functions that can aid in plotting regional maps. They do things like create shapefile that
    # can then be used with basemap. We don't include the basemap functions since that is not in the LSDTT toolchain (but
    # might get included later)
    parser.add_argument("-RF", "--create_raster_footprint_shapefile",type=bool, default=False, help="If true, create a shapefile from the raster. Can be used with basemap to make regional maps")
    parser.add_argument("-BM", "--create_basemap_figure",type=bool, default=False, help="If true, create a basemap file")

    # These control the format of your figures
    parser.add_argument("-fmt", "--FigFormat", type=str, default='png', help="Set the figure format for the plots. Default is png")
    parser.add_argument("-size", "--size_format", type=str, default='ESURF', help="Set the size format for the figure. Can be 'big' (16 inches wide), 'geomorphology' (6.25 inches wide), or 'ESURF' (4.92 inches wide) (defualt esurf).")
    parser.add_argument("-parallel", "--parallel", type=bool, default=False, help="If this is true I'll assume you ran the code in parallel and append all your CSVs together before plotting.")
    parser.add_argument("-dpi", "--dpi", type=int, default=250, help="The dots per inch of your figure.")
    
    args = parser.parse_args()

    if not args.fname_prefix:
        if not args.parallel:
            print("WARNING! You haven't supplied your DEM name. Please specify this with the flag '-fname'")
            sys.exit()

    # get the base directory
    if args.base_directory:
        this_dir = args.base_directory
        # check if you remembered a / at the end of your path_name
        if not this_dir.endswith(os.sep):
            print("You forgot the separator at the end of the directory, appending...")
            this_dir = this_dir+os.sep
    else:
        this_dir = os.getcwd()

    # See if you should create a shapefile of the raster footprint             
    if args.create_raster_footprint_shapefile:
        print("Let me create a shapefile of the raster footprint")
        
        driver_name = "ESRI shapefile"
        driver = ogr.GetDriverByName(driver_name)
        
        print("Driver is: ")
        print(driver)
        
        print("Now I'll try it from LSDPlottingTools")
              
        RasterFile = args.fname_prefix+".bil"
        LSDP.CreateShapefileOfRasterFootprint(this_dir, RasterFile)
        
    # See if you should create a basemap
    if args.create_basemap_figure:
        import LSDBasemapTools as LSDM
        
        RasterFile = args.fname_prefix+".bil"
        
        lat_0 = 25.7
        lon_0 = 91.5
        LSDM.GenerateBasemapImage(this_dir, RasterFile,lat_0 = lat_0 , lon_0 = lon_0)
        
        
            
    # See if a basin info file exists and if so get the basin list
    print("Let me check if there is a basins info csv file.")
    BasinInfoPrefix = args.fname_prefix+"_AllBasinsInfo.csv"
    BasinInfoFileName = this_dir+BasinInfoPrefix
    existing_basin_keys = []
    if os.path.isfile(BasinInfoFileName): 
        print("There is a basins info csv file")
        BasinInfoDF = phelp.ReadBasinInfoCSV(this_dir, args.fname_prefix)
        existing_basin_keys = list(BasinInfoDF['basin_key'])
        existing_basin_keys = [int(x) for x in existing_basin_keys]
    else:
        print("I didn't find a basins info csv file. Check directory or filename.")
    

    # Parse any lists, dicts, or list of lists from the arguments   
    these_basin_keys = parse_list_from_string(args.basin_keys)
    this_rename_dict = parse_dict_from_string(args.rename_dict)
    basin_stack_list = parse_list_of_list_from_string(args.basin_lists)
    chi_offset_list = parse_list_from_string(args.chi_offsets)
    fd_offset_list = parse_list_from_string(args.flow_distance_offsets)

    # If the basin keys are not supplited then assume all basins are used. 
    if these_basin_keys == []:
        these_basin_keys = existing_basin_keys
        
    # Python is so amazing. Look at the line below.
    Mask_basin_keys = [i for i in existing_basin_keys if i not in these_basin_keys]
    print("All basins are: ")
    print(existing_basin_keys)
    print("The basins to keep are:")
    print(these_basin_keys)
    print("The basins to mask are:")
    print(Mask_basin_keys)    
    
    # Look to see if there is a basin stack list. If there is, organise it so that we have different values in the
    # value dict
    if len(basin_stack_list) == 0:
        temp_stack = []
        temp_stack.append(these_basin_keys)
        this_value_dict = convert_basin_stack_to_value_dict(temp_stack)
    else:
        this_value_dict = convert_basin_stack_to_value_dict(basin_stack_list)
        
    # Now make sure all basins have a value dict value
    value_dict_single_basin = {}
    for basin in these_basin_keys:
        value_dict_single_basin[basin] = 1
        if basin not in this_value_dict:
            this_value_dict[basin] = 1
     
    #print("The value dict is:")
    #print(this_value_dict)
    
    # Now if there is a rename dict, replace the value dict values with the rename keys
    if len(this_rename_dict) != 0:
        #print("There is a rename dict. Let me adjust some values.")
        rename_value_dict = {}
        for key in this_value_dict:
            #print("Key is: "+str(key))
            if key in this_rename_dict:
                #print("I found a rename key in the value dict, changing to :"+ str(this_rename_dict[key]))
                rename_value_dict[this_rename_dict[key]] = this_value_dict[key]
            else:
                rename_value_dict[key] = this_value_dict[key]
        this_value_dict = rename_value_dict
    #print("The new value dict is: ")
    print(this_value_dict)
            

    # Set default offsets
    if len(chi_offset_list) == 0:
        chi_offset_list.append(5)
    if len(fd_offset_list) == 0:
        fd_offset_list.append(20000)
    
    #print("I am matching the offest list lengths to the number of basin stacks")    
    final_chi_offsets = pad_offset_lists(basin_stack_list,chi_offset_list)
    final_fd_offsets = pad_offset_lists(basin_stack_list,fd_offset_list)



    # some formatting for the figures
    if args.FigFormat == "manuscipt_svg":
        print("You chose the manuscript svg option. This only works with the -ALL flag. For other flags it will default to simple svg")
        simple_format = "svg"
    elif args.FigFormat == "manuscript_png":
        print("You chose the manuscript png option. This only works with the -ALL flag. For other flags it will default to simple png")
        simple_format = "png"
    else:
        simple_format = args.FigFormat
 

    # This just plots the basins. Useful for checking on basin selection
    if args.plot_basins:
        print("I am only going to print basins.")
        
        # check if a raster directory exists. If not then make it.
        raster_directory = this_dir+'raster_plots/'
        if not os.path.isdir(raster_directory):
            os.makedirs(raster_directory)
        
        raster_out_prefix = "/raster_plots/"+args.fname_prefix      
        # Now for raster plots
        # First the basins, labeled:
        LSDMW.PrintBasins_Complex(this_dir,args.fname_prefix,use_keys_not_junctions = True, show_colourbar = False,Remove_Basins = Mask_basin_keys, Rename_Basins = this_rename_dict,cmap = "jet", size_format = args.size_format,fig_format = simple_format, dpi = args.dpi, out_fname_prefix = raster_out_prefix+"_basins")

    # This just plots the basins. Useful for checking on basin selection
    if args.plot_chi_coord:
        print("I am only going to print basins.")
        
        # check if a raster directory exists. If not then make it.
        raster_directory = this_dir+'raster_plots/'
        if not os.path.isdir(raster_directory):
            os.makedirs(raster_directory)
          
        # Get the names of the relevant files
        ChannelFname = args.fname_prefix+"_chi_data_map.csv"
        
        raster_out_prefix = "/raster_plots/"+args.fname_prefix      
        # Now for raster plots
        # First the basins, labeled:
        LSDMW.PrintBasins_Complex(this_dir,args.fname_prefix,use_keys_not_junctions = True, show_colourbar = False,Remove_Basins = Mask_basin_keys, Rename_Basins = this_rename_dict,cmap = "jet", size_format = args.size_format,fig_format = simple_format, dpi = args.dpi, out_fname_prefix = raster_out_prefix+"_basins")
        
        # Then the chi plot
        LSDMW.PrintChiCoordChannelsAndBasins(this_dir,args.fname_prefix, ChannelFileName = ChannelFname, add_basin_labels = False, cmap = "cubehelix", cbar_loc = "top", size_format = args.size_format, fig_format = simple_format, dpi = args.dpi,plotting_column = "chi", colour_log = False, colorbarlabel = "$\chi$", Basin_remove_list = Mask_basin_keys, Basin_rename_dict = this_rename_dict , value_dict = this_value_dict, out_fname_prefix = raster_out_prefix+"_raster", plot_chi_raster = True)  
        
        LSDMW.PrintChiCoordChannelsAndBasins(this_dir,args.fname_prefix, ChannelFileName = ChannelFname, add_basin_labels = False, cmap = "cubehelix", cbar_loc = "top", size_format = args.size_format, fig_format = simple_format, dpi = args.dpi,plotting_column = "chi", colour_log = False, colorbarlabel = "$\chi$", Basin_remove_list = Mask_basin_keys, Basin_rename_dict = this_rename_dict , value_dict = this_value_dict, out_fname_prefix = raster_out_prefix+"_channels", plot_chi_raster = False)  
        
    # This bundles a number of different analyses    
    if args.all_chi_plots:
        print("You have chosen to plot all raster and stacked plots.")
        args.all_raster_plots = True
        args.all_stacked_plots = True

    # make the plots depending on your choices
    if args.all_raster_plots:
        print("I am goint to print some raster plots for you.")
        
        # check if a raster directory exists. If not then make it.
        raster_directory = this_dir+'raster_plots/'
        if not os.path.isdir(raster_directory):
            os.makedirs(raster_directory)
          
        # Get the names of the relevant files
        ChannelFname = args.fname_prefix+"_MChiSegmented.csv"
        
        raster_out_prefix = "/raster_plots/"+args.fname_prefix
        
        # Now for raster plots
        # First the basins, labeled:
        LSDMW.PrintBasins_Complex(this_dir,args.fname_prefix,use_keys_not_junctions = True, show_colourbar = False,Remove_Basins = Mask_basin_keys, Rename_Basins = this_rename_dict,cmap = "jet", size_format = args.size_format,fig_format = simple_format, dpi = args.dpi, out_fname_prefix = raster_out_prefix+"_basins")
        
        # Basins colour coded
        print("The value dict is: ")
        print(this_value_dict)
        LSDMW.PrintBasins_Complex(this_dir,args.fname_prefix,use_keys_not_junctions = True, show_colourbar = False,Remove_Basins = Mask_basin_keys, Rename_Basins = this_rename_dict, Value_dict = this_value_dict, cmap = "gray", size_format = args.size_format,fig_format = simple_format, dpi = args.dpi, out_fname_prefix = raster_out_prefix+"_stack_basins")
        
        # Now the chi steepness
        LSDMW.PrintChiChannelsAndBasins(this_dir, args.fname_prefix, ChannelFileName = ChannelFname, add_basin_labels = False, cmap = "viridis", cbar_loc = "right", size_format = args.size_format, fig_format = simple_format, dpi = args.dpi,plotting_column="m_chi",colorbarlabel = "$\mathrm{log}_{10} \; \mathrm{of} \; k_{sn}$", Basin_remove_list = Mask_basin_keys, Basin_rename_dict = this_rename_dict, value_dict = value_dict_single_basin, out_fname_prefix = raster_out_prefix+"_ksn")
        
        # Now plot the channels coloured by the source number
        LSDMW.PrintChiChannelsAndBasins(this_dir, args.fname_prefix, ChannelFileName = ChannelFname, add_basin_labels = False, cmap = "tab20b", cbar_loc = "None", size_format = args.size_format, fig_format = simple_format, dpi = args.dpi,plotting_column="source_key", Basin_remove_list = Mask_basin_keys, Basin_rename_dict = this_rename_dict, value_dict = this_value_dict, out_fname_prefix = raster_out_prefix+"sources", discrete_colours = True, NColours = 20, colour_log = False)
        
    if args.all_stacked_plots:
 
        # check if a chi profile directory exists. If not then make it.
        chi_profile_directory = this_dir+'chi_profile_plots/'
        if not os.path.isdir(chi_profile_directory):
            os.makedirs(chi_profile_directory)   

         # Get the names of the relevant files
        ChannelFname = args.fname_prefix+"_MChiSegmented.csv"
        
        raster_out_prefix = "/raster_plots/"+args.fname_prefix       
        
        print("I am going to plot some chi stacks for you.")
        cbl = "$\mathrm{log}_{10} \; \mathrm{of} \; k_{sn}$"  
        i = 0
        for little_list in basin_stack_list:
            i = i+1
            this_prefix = "chi_profile_plots/Stacked_"+str(i) 
            
            print("The offset is: ")
            print("chi: "+str(final_chi_offsets[i-1]) )
            print("flow distance: "+ str(final_fd_offsets[i-1]) )
            
            
            # This prints the chi profiles coloured by k_sn
            LSDMW.PrintChiStacked(this_dir, args.fname_prefix, ChannelFname, cmap = "viridis", size_format = args.size_format, fig_format = simple_format, dpi = args.dpi,axis_data_name="chi",plot_data_name = "m_chi",colorbarlabel = cbl, cbar_loc = "bottom", Basin_select_list = little_list, Basin_rename_dict = this_rename_dict, out_fname_prefix = this_prefix+"_chi",X_offset = final_chi_offsets[i-1])
        
            # This prints channel profiles coloured by k_sn
            LSDMW.PrintChiStacked(this_dir, args.fname_prefix, ChannelFname, cmap = "viridis", size_format = args.size_format, fig_format = simple_format, dpi = args.dpi,axis_data_name="flow_distance",plot_data_name = "m_chi", plotting_data_format = 'log', colorbarlabel = cbl, Basin_select_list = little_list, Basin_rename_dict = this_rename_dict, out_fname_prefix = this_prefix+"_FD", X_offset = final_fd_offsets[i-1])    

            # This prints the channel profiles coloured by source number
            LSDMW.PrintChiStacked(this_dir, args.fname_prefix, ChannelFname, cmap = "tab20b", size_format = args.size_format, fig_format = simple_format, dpi = args.dpi,axis_data_name="flow_distance",plot_data_name = "source_key", plotting_data_format = 'normal', colorbarlabel = cbl, cbar_loc = "None", discrete_colours = True, NColours = 20, Basin_select_list = little_list, Basin_rename_dict = this_rename_dict, out_fname_prefix = this_prefix+"_Sources", X_offset = final_fd_offsets[i-1])        


#=============================================================================
if __name__ == "__main__":
    main(sys.argv[1:])

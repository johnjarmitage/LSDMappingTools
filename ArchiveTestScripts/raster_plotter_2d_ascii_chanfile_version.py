## raster_plotter.py
##=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
## Function to plot the raster data in *.flt format generated by the 
## chi analysis code. read_flt() returns flt data as numpy arrays and is 
## called by the plot_ChiMValues_hillshade() to quickly visualise the 
## m values without launching arcmap. Vectorize() plots the m values
## as individual points. Next step may be to thin the points?
##
## flt reading Built around code from http://pydoc.net/Python/PyTOPKAPI/0.2.0/pytopkapi.arcfltgrid/
##=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
## SWDG 19/06/2013
## modified SMM 09/08/2013
## modified DAV 09/04/2015 - reads ascii files and the .Chan file format by default
##=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-

def round_to_n(x, n):
    if n < 1:
        raise ValueError("number of significant digits must be >= 1")
    # Use %e format to get the n most significant digits, as a string.
    format = "%." + str(n-1) + "e"
    as_string = format % x
    return float(as_string)


def read_headers(input_file):

    with open(input_file+'.hdr','r') as f:   
        return [float(h) if not h.isalpha() else h for h in [l.split()[1] for l in f.readlines()]]  #isdigit() does not catch floats      

def read_bin(filename):
    import sys
    import numpy as np

    with open(filename + '.flt', "rb") as f:
        raster_data = np.fromstring(f.read(), 'f')

    if sys.byteorder == 'big':
        raster_data = raster_data.byteswap()  #ensures data is little endian

    return raster_data
    
def read_flt(input_file):

    if input_file.endswith('.flt') or input_file.endswith('.hdr'):
        input_file = input_file[:-4]    
    else:
        print 'Incorrect filename'
        return 0,0 #exits module gracefully
    
    headers = read_headers(input_file)
    
    #read the data as a 1D array and reshape it to the dimensions in the header
    raster_array = read_bin(input_file).reshape(headers[1], headers[0]) 
    raster_array = raster_array.reshape(headers[1], headers[0]) #rows, columns

    return raster_array, headers

def read_ascii_raster(ascii_raster_file):
    import numpy as np
    
    with open(ascii_raster_file) as f:
        header_data = [float(f.next().split()[1]) for x in xrange(6)] #read the first 6 lines
         
    raster_data = np.genfromtxt(ascii_raster_file, delimiter=' ', skip_header=6)
    raster_data = raster_data.reshape(header_data[1], header_data[0]) #rows, columns
    
    return raster_data, header_data

def format_ticks_for_UTM_imshow(hillshade_header,x_max,x_min,y_max,y_min,n_target_tics):
    import numpy as np    
   
    xmax_UTM = hillshade_header[2]+x_max*hillshade_header[4]
    xmin_UTM = hillshade_header[2]+x_min*hillshade_header[4]
      
    # need to be careful with the ymax_UTM since the rows go from the top
    # but the header index is to bottom corner    
    
    print "yll: "+str(hillshade_header[3])+" and nrows: " +str(hillshade_header[1]) + " dx: "+str(hillshade_header[4])   
    
    ymax_from_bottom = hillshade_header[1]-y_min
    ymin_from_bottom = hillshade_header[1]-y_max
    ymax_UTM = hillshade_header[3]+ymax_from_bottom*hillshade_header[4]
    ymin_UTM = hillshade_header[3]+ymin_from_bottom*hillshade_header[4]
    
    print "now UTM, xmax: " +str(xmax_UTM)+" x_min: " +str(xmin_UTM)+" y_maxb: " +str(ymax_UTM)+" y_minb: " +str(ymin_UTM)
    
    dy_fig = ymax_UTM-ymin_UTM
    dx_fig = xmax_UTM-xmin_UTM
    
    dx_spacing = dx_fig/n_target_tics
    dy_spacing = dy_fig/n_target_tics
    
    if (dx_spacing>dy_spacing):
        dy_spacing = dx_spacing
    
    str_dy = str(dy_spacing)
    str_dy = str_dy.split('.')[0]
    n_digits = str_dy.__len__()
    nd = int(n_digits)
        
    first_digit = float(str_dy[0])
    
    print "str_dy: " +str_dy+ " n_digits: " +str(nd)+" first_digit: " + str(first_digit)    
    
    dy_spacing_rounded = first_digit*pow(10,(nd-1))
    print "n_digits: "+str(n_digits)+" dy_spacing: " +str(dy_spacing) + " and rounded: "+str(dy_spacing_rounded)
 
    str_xmin = str(xmin_UTM)
    str_ymin = str(ymin_UTM)
    str_xmin = str_xmin.split('.')[0]
    str_ymin = str_ymin.split('.')[0]
    xmin_UTM = float(str_xmin)
    ymin_UTM = float(str_ymin)
    
    n_digx = str_xmin.__len__() 
    n_digy = str_ymin.__len__() 
    
    front_x = str_xmin[:(n_digx-nd+1)]
    front_y = str_ymin[:(n_digy-nd+1)]
      
    print "xmin: " + str_xmin + " ymin: " + str_ymin + " n_digx: " + str(n_digx)+ " n_digy: " + str(n_digy)
    print "frontx: " +front_x+" and fronty: "+ front_y
     
    round_xmin = float(front_x)*pow(10,nd-1)
    round_ymin = float(front_y)*pow(10,nd-1)
    
    print "x_min: " +str(xmin_UTM)+ " round xmin: " +str(round_xmin)+ " y_min: " +str(ymin_UTM)+" round y_min: " + str(round_ymin)
    
    # now we need to figure out where the xllocs and ylocs are
    xUTMlocs = np.zeros(2*n_target_tics)
    yUTMlocs = np.zeros(2*n_target_tics)
    xlocs = np.zeros(2*n_target_tics)
    ylocs = np.zeros(2*n_target_tics)
    
    new_x_labels = []
    new_y_labels = []
    
    for i in range(0,2*n_target_tics):
        xUTMlocs[i] = round_xmin+(i)*dy_spacing_rounded
        yUTMlocs[i] = round_ymin+(i)*dy_spacing_rounded
                  
        xlocs[i] = (xUTMlocs[i]-hillshade_header[2])/hillshade_header[4]
        
        # need to account for the rows starting at the upper boundary
        ylocs[i] = hillshade_header[1]-((yUTMlocs[i]-hillshade_header[3])/hillshade_header[4])
        
        new_x_labels.append( str(xUTMlocs[i]).split(".")[0] )
        new_y_labels.append( str(yUTMlocs[i]).split(".")[0] )
   
    return xlocs,ylocs,new_x_labels,new_y_labels




def vectorize(hillshade_file, m_value_file):
    
    import matplotlib.pyplot as pp
    import numpy as np
    import matplotlib.colors as colors
    import matplotlib.cm as cmx
    from matplotlib import rcParams
    
    #get data
    hillshade, hillshade_header = read_flt(hillshade_file)
    m_values, m_values_header = read_flt(m_value_file)
    
    #handle plotting hillshades which are larger than the m_value raster
    #cannot cope with m_value raster larger than the hillshade
    corrected_x = 0    
    corrected_y = 0
    if (hillshade_header[0] != m_values_header[0]) or (hillshade_header[1] != m_values_header[1]):
         corrected_x = (m_values_header[2] - hillshade_header[2]) / hillshade_header[4]
         corrected_y = (((m_values_header[3] / m_values_header[4] )+ m_values_header[1]) - ((hillshade_header[3] / hillshade_header[4]) + hillshade_header[1])) * -1
    
    #ignore nodata values    
    hillshade = np.ma.masked_where(hillshade == -9999, hillshade)    
    m_values = np.ma.masked_where(m_values == -9999, m_values)
    
    #fonts
    rcParams['font.family'] = 'sans-serif'
    rcParams['font.sans-serif'] = ['arial']
    rcParams['font.size'] = 12  
    
    fig, ax = pp.subplots()
    
    ax.imshow(hillshade, vmin=0, vmax=255, cmap=cmx.gray)
          
    xlocs, xlabels = pp.xticks()
    ylocs, ylabels = pp.yticks()
   
    new_x_labels = np.linspace(hillshade_header[2],hillshade_header[2]+(hillshade_header[1]*hillshade_header[4]), len(xlocs))
    new_y_labels = np.linspace(hillshade_header[3],hillshade_header[3]+(hillshade_header[0]*hillshade_header[4]), len(ylocs))        
    
    new_x_labels = [str(x).split('.')[0] for x in new_x_labels] #get rid of decimal places in axis ticks
    new_y_labels = [str(y).split('.')[0] for y in new_y_labels][::-1] #invert y axis
    pp.xticks(xlocs[1:-1], new_x_labels[1:-1], rotation=30)  #[1:-1] skips ticks where we have no data
    pp.yticks(ylocs[1:-1], new_y_labels[1:-1])
    
    pp.xlabel('Easting (m)')
    pp.ylabel('Northing (m)')    
    
    # SET UP COLOURMAPS
    jet = pp.get_cmap('jet')
    
    m_MIN = np.min(m_values)
    m_MAX = np.max(m_values)
    cNorm_m_values  = colors.Normalize(vmin=m_MIN, vmax=m_MAX)
    scalarMap_m_values = cmx.ScalarMappable(norm=cNorm_m_values, cmap=jet)    
    
    for i in xrange(len(m_values)):
        for j in xrange(len(m_values[0])):
            if m_values[i][j] > 0:
                colorVal = scalarMap_m_values.to_rgba(m_values[i][j])
                pp.scatter(j + corrected_x, i + corrected_y, marker=".", color=colorVal,edgecolors='none')               
                  
    # Configure final plot
    sm = pp.cm.ScalarMappable(cmap=jet,norm=pp.normalize(vmin=m_MIN, vmax=m_MAX))
    sm._A = []
    cbar = pp.colorbar(sm)
    cbar.set_label('M Values')
    
    pp.show()
    
def plot_ChiMValues_hillshade(hillshade_file, m_value_file):
    
    """
    Pass in a hillshade and chiMvalues flt file and plot the results over
    a greyscale hillshade
    """

    import matplotlib.pyplot as pp
    import matplotlib.cm as cm
    from matplotlib import rcParams
    import numpy as np
    
    #get data
    hillshade, hillshade_header = read_flt(hillshade_file)
    m_values, m_values_header = read_flt(m_value_file)
    
    #ignore nodata values    
    hillshade = np.ma.masked_where(hillshade == -9999, hillshade)    
    m_values = np.ma.masked_where(m_values == -9999, m_values)
    
    #fonts
    rcParams['font.family'] = 'sans-serif'
    rcParams['font.sans-serif'] = ['arial']
    rcParams['font.size'] = 12  

    fig, ax = pp.subplots()
    
    #plot the arrays
    ax.imshow(hillshade, vmin=0, vmax=255, cmap=cm.gray)
    data = ax.imshow(m_values, interpolation='none', vmin=m_values.min(), vmax=m_values.max(), cmap=cm.jet)
    
    xlocs, xlabels = pp.xticks()
    ylocs, ylabels = pp.yticks()
   
    new_x_labels = np.linspace(hillshade_header[2],hillshade_header[2]+(hillshade_header[1]*hillshade_header[4]), len(xlocs))
    new_y_labels = np.linspace(hillshade_header[3],hillshade_header[3]+(hillshade_header[0]*hillshade_header[4]), len(ylocs))        
    
    new_x_labels = [str(x).split('.')[0] for x in new_x_labels] #get rid of decimal places in axis ticks
    new_y_labels = [str(y).split('.')[0] for y in new_y_labels][::-1] #invert y axis
    pp.xticks(xlocs[1:-1], new_x_labels[1:-1], rotation=30)  #[1:-1] skips ticks where we have no data
    pp.yticks(ylocs[1:-1], new_y_labels[1:-1])    
    
    fig.colorbar(data).set_label('M Values')
    pp.xlabel('Easting (m)')
    pp.ylabel('Northing (m)')
    
    pp.show()    


def cumulative_rainfall_catchment(hillshade_file, radar_data_totals):
    """
    Plots the catchment hillshade and overlays the total rainfalls accumulated
    during the model run.
    """
    label_size = 20
    #title_size = 30
    axis_size = 28

    import matplotlib.pyplot as pp
    import numpy as np
    import matplotlib.colors as colors
    import matplotlib.cm as cmx
    from matplotlib import rcParams
    import matplotlib.lines as mpllines
    
    #get data
    #hillshade, hillshade_header = read_flt(hillshade_file)
    
    hillshade, hillshade_header = read_ascii_raster(hillshade_file)
    rainfall_totals = np.loadtxt(radar_data_totals)
    
    #ignore nodata values    
    hillshade = np.ma.masked_where(hillshade == -9999, hillshade)    
    
    #fonts
    rcParams['font.family'] = 'sans-serif'
    rcParams['font.sans-serif'] = ['arial']
    rcParams['font.size'] = label_size      
    
    fig = pp.figure(1, facecolor='white',figsize=(10,7.5))
    ax = fig.add_subplot(1,1,1)
    
    plt.imshow(hillshade, vmin=0, vmax=255, cmap=cmx.gray)
    plt.imshow(rainfall_totals, interpolation="none", alpha=0.2)
    
    

def coloured_chans_like_graphs(hillshade_file, tree_file):
    """
    Plots outlines of channels taken from the *.tree file over a hillshade
    giving each channel a unique colour which corresponds to the colours used
    in the Chi plotting routines in chi_visualisation.py.
    
    """
 
    label_size = 20
    #title_size = 30
    axis_size = 28

    
   
    import matplotlib.pyplot as pp
    import numpy as np
    import matplotlib.colors as colors
    import matplotlib.cm as cmx
    from matplotlib import rcParams
    import matplotlib.lines as mpllines
    
    #get data
    #hillshade, hillshade_header = read_flt(hillshade_file)
    
    hillshade, hillshade_header = read_ascii_raster(hillshade_file)
    
    #ignore nodata values    
    hillshade = np.ma.masked_where(hillshade == -9999, hillshade)    
    
    #fonts
    rcParams['font.family'] = 'sans-serif'
    rcParams['font.sans-serif'] = ['arial']
    rcParams['font.size'] = label_size  

    #get coordinates of streams from tree file   
    channel_id = []
    row = []
    col = []
        
    with open(tree_file, 'r') as f:
        lines = f.readlines()
        
    for q,line in enumerate(lines):
        #if q > 0: #skip first line
        if q > 5: #skip header (6 lines) for .Chan file
            channel_id.append(int(line.split()[0]))
            row.append(float(line.split()[4]))
            col.append(float(line.split()[5]))

    #get bounding box & pad to 10% of the dimension
    x_max = max(col)
    x_min = min(col)
    y_max = max(row)
    y_min = min(row) 
    
    pad_x = (x_max - x_min) * 0.1
    pad_y = (x_max - y_min) * 0.1
    
    if (pad_y > pad_x):
        pad_x = pad_y
    else:
        pad_y = pad_x
    
    x_max += pad_x
    x_min -= pad_x
    y_max += pad_y
    y_min -= pad_y 
    
    fig = pp.figure(1, facecolor='white',figsize=(10,7.5))
    ax = fig.add_subplot(1,1,1)
    ax.imshow(hillshade, vmin=0, vmax=255, cmap=cmx.gray)
    

    # now get the tick marks    
    n_target_tics = 5
    xlocs,ylocs,new_x_labels,new_y_labels = format_ticks_for_UTM_imshow(hillshade_header,x_max,x_min,y_max,y_min,n_target_tics)  
    pp.xticks(xlocs, new_x_labels, rotation=60)  #[1:-1] skips ticks where we have no data
    pp.yticks(ylocs, new_y_labels) 

    # some formatting to make some of the ticks point outward    
    for line in ax.get_xticklines():
        line.set_marker(mpllines.TICKDOWN)
        #line.set_markeredgewidth(3)

    for line in ax.get_yticklines():
        line.set_marker(mpllines.TICKLEFT)
        #line.set_markeredgewidth(3)  
    
    pp.xlim(x_min,x_max)    
    pp.ylim(y_max,y_min)   
   
    pp.xlabel('Easting (m)',fontsize = axis_size)
    pp.ylabel('Northing (m)', fontsize = axis_size)  
                  
    # channel ID
    Channel_ID_MIN = np.min(channel_id)
    #Channel_ID_MAX = np.max(channel_id)
    Channel_ID_MAX = 1
    cNorm_channel_ID  = colors.Normalize(vmin=Channel_ID_MIN, vmax=Channel_ID_MAX)  # the max number of channel segs is the 'top' colour
    jet = pp.get_cmap('jet')
    scalarMap_channel_ID = cmx.ScalarMappable(norm=cNorm_channel_ID, cmap=jet) 
    

#    #for a,i in enumerate(reversed(channel_id)):
#    for a,i in enumerate(channel_id):
#        if i != 0:
#            # plot other stream segments
#            colorVal = scalarMap_channel_ID.to_rgba(i) # this gets the distinct colour for this segment
#            pp.scatter(col[a], row[a], 30,marker=".", color=colorVal,edgecolors='none') 

    # Use this to highlight individual channels
    for a,i in enumerate(channel_id):
        if i == 3:
            # plot highlighted stream
            pp.scatter(col[a], row[a], 30,marker=".", color='c',edgecolors='none')
        
        elif i == 0:
            # plot trunk stream in black
            pp.scatter(col[a], row[a], 40,marker=".", color='b',edgecolors='none')
        # Plot other tribs if you want to
#        else:
#            colorVal = scalarMap_channel_ID.to_rgba(i) # this gets the distinct colour for this segment
#            pp.scatter(col[a], row[a], 30,marker=".", color=colorVal,edgecolors='none') 
            
    ax.spines['top'].set_linewidth(2.5)
    ax.spines['left'].set_linewidth(2.5)
    ax.spines['right'].set_linewidth(2.5)
    ax.spines['bottom'].set_linewidth(2.5) 
    ax.tick_params(axis='both', width=2.5)     
 
    pp.xlim(x_min,x_max)    
    pp.ylim(y_max,y_min) 
 
    pp.title("Ryedale Catchment Main Channels",fontsize=label_size)  
    pp.tight_layout()        

    
    
    pp.show()
    
    
    
    
    
def m_values_over_hillshade(hillshade_file, tree_file):
    """
    Plots m values of channels taken from the *.tree file over a hillshade
    
    """
 
    label_size = 20
    #title_size = 30
    axis_size = 28
   
    import matplotlib.pyplot as pp
    import numpy as np
    import matplotlib.colors as colors
    import matplotlib.cm as cmx
    from matplotlib import rcParams
    import matplotlib.lines as mpllines
    
    #get data
    hillshade, hillshade_header = read_flt(hillshade_file)
    
    #ignore nodata values    
    hillshade = np.ma.masked_where(hillshade == -9999, hillshade)    
    
    #fonts
    rcParams['font.family'] = 'sans-serif'
    rcParams['font.sans-serif'] = ['arial']
    rcParams['font.size'] = label_size  

    #get coordinates of streams from tree file   
    M_chi_value = []
    channel_id = []
    row = []
    col = []
        
    with open(tree_file, 'r') as f:
        lines = f.readlines()
        
    for q,line in enumerate(lines):
        if q > 0: #skip first line
            channel_id.append(float(line.split()[0]))
            M_chi_value.append(float(line.split()[11]))
            row.append(float(line.split()[4]))
            col.append(float(line.split()[5]))

    #get bounding box & pad to 10% of the dimension
    x_max = max(col)
    x_min = min(col)
    y_max = max(row)
    y_min = min(row) 
    
    pad_x = (x_max - x_min) * 0.1
    pad_y = (x_max - y_min) * 0.1
    
    if (pad_y > pad_x):
        pad_x = pad_y
    else:
        pad_y = pad_x
    
    x_max += pad_x
    x_min -= pad_x
    y_max += pad_y
    y_min -= pad_y 
    
    fig = pp.figure(1, facecolor='white',figsize=(10,7.5))
    ax = fig.add_subplot(1,1,1)
    ax.imshow(hillshade, vmin=0, vmax=255, cmap=cmx.gray)
    
    # now get the tick marks    
    n_target_tics = 5
    xlocs,ylocs,new_x_labels,new_y_labels = format_ticks_for_UTM_imshow(hillshade_header,x_max,x_min,y_max,y_min,n_target_tics)  
    pp.xticks(xlocs, new_x_labels, rotation=60)  #[1:-1] skips ticks where we have no data
    pp.yticks(ylocs, new_y_labels) 
    
    for line in ax.get_xticklines():
        line.set_marker(mpllines.TICKDOWN)
        #line.set_markeredgewidth(3)

    for line in ax.get_yticklines():
        line.set_marker(mpllines.TICKLEFT)
        #line.set_markeredgewidth(3)  
 
    pp.xlim(x_min,x_max)    
    pp.ylim(y_max,y_min)  
   
    pp.xlabel('Easting (m)',fontsize = axis_size)
    pp.ylabel('Northing (m)',fontsize = axis_size)    
              
    # channel ID
    M_chi_value_MIN = np.min(M_chi_value)
    M_chi_value_MAX = np.max(M_chi_value)
    cNorm_M_chi_value  = colors.Normalize(vmin=M_chi_value_MIN, vmax=M_chi_value_MAX)  # the max number of channel segs is the 'top' colour
    hot = pp.get_cmap('RdYlBu_r')
    scalarMap_M_chi_value = cmx.ScalarMappable(norm=cNorm_M_chi_value, cmap=hot) 
    
    
    for a,i in enumerate(M_chi_value):
        #print "a: " +str(a)+" i: " +str(i)
        if channel_id[a] != 0:     
            # plot other stream segments
            colorVal = scalarMap_M_chi_value.to_rgba(i) # this gets the distinct colour for this segment
            pp.scatter(col[a], row[a], 30,marker=".", color=colorVal,edgecolors=colorVal) 

    for a,i in enumerate(M_chi_value):
        if channel_id[a] == 0:
            # plot trunk stream in black
            colorVal = scalarMap_M_chi_value.to_rgba(i)
            pp.scatter(col[a], row[a], 40,marker=".", color=colorVal,edgecolors=colorVal)

    sm = pp.cm.ScalarMappable(cmap=hot, norm=pp.normalize(vmin=min(M_chi_value), vmax=max(M_chi_value)))
    sm._A = []
    


    
    ax.spines['top'].set_linewidth(2.5)
    ax.spines['left'].set_linewidth(2.5)
    ax.spines['right'].set_linewidth(2.5)
    ax.spines['bottom'].set_linewidth(2.5) 
    ax.tick_params(axis='both', width=2.5)      
    
    from mpl_toolkits.axes_grid1 import make_axes_locatable
    divider = make_axes_locatable(pp.gca())
    cax = divider.append_axes("right", "5%", pad="3%")
    pp.colorbar(sm, cax=cax).set_label('$M_{\chi}$',fontsize=axis_size) 
    cax.tick_params(labelsize=label_size) 
    
    #pp.xlim(x_min,x_max)    
    #pp.ylim(y_max,y_min) 

    pp.tight_layout()
        
    pp.show()

#coloured_chans_like_graphs('/home/dav/DATADRIVE/CODE_DEV/LSD_devel/LSDTopoTools/trunk/driver_functions/build_long_profile_swath/RYEDALE_20m_fillcrop_HS.asc', \
#'/home/dav/DATADRIVE/CODE_DEV/LSD_devel/LSDTopoTools/trunk/driver_functions/build_long_profile_swath/RYEDALE_20m_fillcrop_ChanNet.chan')
#coloured_chans_like_graphs('C:\\DATA\\CODE_DEV\\LSD_devel\\LSDTopoTools\\trunk\\driver_functions\\build_long_profile_swath\\RYEDALE_20m_fillcrop_HS.asc', \
#'C:\\DATA\\CODE_DEV\\LSD_devel\\LSDTopoTools\\trunk\\driver_functions\\build_long_profile_swath\\RYEDALE_20m_fillcrop_ChanNet.chan')
   
cumulative_rainfall_catchment("/run/media/dav/LEWIS/CODE_DEV/PyToolsPhD/Radardata_tools/RYEDALE_20m_fillcrop_HS.asc", \
    "/run/media/dav/LEWIS/CODE_DEV/PyToolsPhD/Radardata_tools/rainfall_totals_test.asc")   
   
   
#plot_ChiMValues_hillshade('M:\\LSDRaster_chi_package\\Test_data\\rio_torto_HS.flt', 'M:\\LSDRaster_chi_package\\Test_data\\rio_torto_ChiMValues_115.flt')
#vectorize('S:\\PA\\pa_basin_HS.flt', 'S:\\PA\\pa_basin_ChiMValues_1189.flt')
#coloured_chans_like_graphs('S:\\PA\\pa_basin_HS.flt', 'S:\\PA\\pa_basin_fullProfileMC_mainstem_1189.tree')
#coloured_chans_like_graphs('c:\\code\\topographic_analysis\\LSDRaster_chi_package\\PA\\pa_basin_HS.flt', 'c:\\users\\smudd\\Documents\\topographic_analysis\\LSDRaster_chi_package\\PA\\pa_basin_fullProfileMC_mainstem_1189.tree')
#m_values_over_hillshade('S:\\PA\\pa_basin_HS.flt', 'S:\\PA\\pa_basin_fullProfileMC_mainstem_1189.tree')
#m_values_over_hillshade('c:\\code\\topographic_analysis\\LSDRaster_chi_package\\PA\\pa_basin_HS.flt', 'c:\\users\\smudd\\Documents\\topographic_analysis\\LSDRaster_chi_package\\PA\\pa_basin_fullProfileMC_mainstem_1189.tree')
#m_values_over_hillshade('c:\\code\\topographic_analysis\\LSDRaster_chi_package\\PA\\pa_basin_HS.flt', 'c:\\users\\smudd\\Documents\\topographic_analysis\\LSDRaster_chi_package\\PA\\pa_basin_fullProfileMC_mainstem_445.tree')
#coloured_chans_like_graphs('M:\\topographic_tools\\LSDRaster_chi_package\\Test_data\\rio_torto_HS.flt', 'M:\\topographic_tools\\LSDRaster_chi_package\\Test_data\\rio_torto_fullProfileMC_forced_0.8_634.tree')
#m_values_over_hillshade('M:\\topographic_tools\\LSDRaster_chi_package\\Test_data\\rio_torto_HS.flt', 'M:\\topographic_tools\\LSDRaster_chi_package\\Test_data\\rio_torto_fullProfileMC_forced_0.8_634.tree')
#m_values_over_hillshade('M:\\topographic_tools\\LSDRaster_chi_package\\Test_data\\rio_torto_HS.flt', 'M:\\topographic_tools\\LSDRaster_chi_package\\Test_data\\rio_torto_fullProfileMC_mainstem_633.tree')
#m_values_over_hillshade('M:\\topographic_tools\\LSDRaster_chi_package\\Test_data\\rio_torto_HS.flt', 'M:\\topographic_tools\\LSDRaster_chi_package\\Test_data\\rio_torto_fullProfileMC_mainstem_114.tree')
#coloured_chans_like_graphs('M:\\topographic_tools\\LSDRaster_chi_package\\Test_data\\rio_torto_HS.flt', 'M:\\topographic_tools\\LSDRaster_chi_package\\Test_data\\rio_torto_fullProfileMC_mainstem_114.tree')
#coloured_chans_like_graphs('c:\\code\\topographic_analysis\\LSDRaster_chi_package\\Test_data\\rio_torto_HS.flt', 'c:\\code\\topographic_analysis\\LSDRaster_chi_package\\Test_data\\rio_torto_fullProfileMC_mainstem_110.tree')
#m_values_over_hillshade('c:\\code\\topographic_analysis\\LSDRaster_chi_package\\Test_data\\rio_torto_HS.flt', 'c:\\code\\topographic_analysis\\LSDRaster_chi_package\\Apennines\\rio_torto_fullProfileMC_forced_0.6_20_1_12_100_110.tree')
#coloured_chans_like_graphs('c:\\code\\topographic_analysis\\LSDRaster_chi_package\\Test_data\\rio_torto_HS.flt', 'c:\\code\\topographic_analysis\\LSDRaster_chi_package\\Test_data\\rio_torto_fullProfileMC_colinear_633.tree')
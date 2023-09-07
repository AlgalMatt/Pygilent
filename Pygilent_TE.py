import os
import pandas as pd
import numpy as np
import sympy as sym
from tkinter import filedialog
import tkinter as tk
import csv
import math
import warnings
import statsmodels.api as sm
import time
import statistics
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib 
from tkinter import ttk
from tkinter.scrolledtext import ScrolledText






####### Functions ################
#function for finding occurrences of substring (or a selection of substrings) 
#within an array of strings
def contains1d(array1, string1, ret_array=True, case_sensitive=False):
    """
    Looks for occurrences of substring(s) within an array of strings, returning
    a boolean array. This is essentially the Pandas series.str.contains method, 
    but slightly adapted.
    
    Parameters
    ----------
    array1 : 1d array (list, numpy array)
        array to search.
    string1 : string, or 1d array of strings (list or numpy array)
        substrings used to search for within array1.
    ret_array : boolean, optional
        If true, then the output will be a 1d array of the same size as array1, 
        providing True/False values for each element that contains/does not 
        contain any of the substrings within string1. 
        If false, then the output will be a matrix of len(array1) by
        len(string1) with each column being a separate boolean array of 
        occurrences of each substring in string1 within array1.
        The default is True.
    case_sensitive : boolean, optional
        If true, the search will be case-sensitive. The default is False.

    Returns
    -------
    retarray : numpy array or matrix of len(array1)
        An array of boolean values where True values indicate the presence of the 
        substring, string1, at the same index of array1. An element-wise 
        string1 in array1.

    """
    
    #vectorize lower cases
    nlower=np.vectorize(str.lower)
    
    retarray=[]
    #if argument string1 is a single string
    if type(string1)==str:
        #lower all cases
        if case_sensitive==False:
            array1=nlower(array1)
            string1=string1.lower()
        for i in array1:
            retarray.append(string1 in i)   
    #if string1 is a list of strings             
    else:
        #lower all cases
        if case_sensitive==False:
            array1=nlower(array1)
            string1=nlower(string1)
        retarray=np.full((len(array1), len(string1)), False)
        #iterate over the list of substrings
        for j, s in enumerate(string1):
            #iterate over the array of strings a check if the iterated 
            #substring is in it            
            for i, a in enumerate(array1):
                retarray[i, j]=s in a
        #if true, return a 1D array, else it returns a len(array1) by 
        #len(string1) matrix of occurrences of each substring within the array
        if ret_array:
            retarray=np.any(retarray, axis=1)           
    return retarray







def fancycheckbox(items,  title="", defaults=None, single=False):
    """    
    Creates a pop-up simple checkbox from a list of items. Returns indexes of 
    the checked items.

    Parameters
    ----------
    items : 1d array (list or numpy array)
        list of items to fill the checkbox.
    title : string, optional
        Descriptive title of the checkbox window. The default is "".
    defaults : boolean array, optional
        Indexes which items to have check boxes ticked by default. 
        The default is None.
    single : boolean, optional
        If true, only one checkbox can be selected. The default is False.

    Returns
    -------
    selected_indexes : numpy.array
        array of indexes of checked items.

    """
    global selected
    #if no defaults used, create a list of False to implement defaults.
    if defaults is None:
        defaults=[False]*len(items)
    # Create the main window
    window = tk.Tk()
    window.title(title)
    #Keep the window at the front of other apps.
    window.lift()
    window.attributes("-topmost", True)
    
    
    w = 400 # width for the Tk root
    h = 700 # height for the Tk root
    
    # get screen width and height
    ws = window.winfo_screenwidth() # width of the screen
    hs = window.winfo_screenheight() # height of the screen
    
    # calculate x and y coordinates for the Tk root window
    x = (ws/2) - (w/2)
    y = (hs/2) - (h/2)
    
    # set the dimensions of the screen 
    # and where it is placed
    window.geometry('%dx%d+%d+%d' % (w, h, x, y))
    
    #make sure scrolling area always fills the window area
    window.rowconfigure(1, weight=1)
    window.columnconfigure(0, weight=1)
       
    # Create a list of booleans to store the state of each checkbox
    selected = defaults
    
    # Function to update the list of selected items
    def update_selected(var):
        global selected        
        if single:
            for i in range(len(cb_vars)):
                if i != var:
                    cb_vars[i].set(False)
                    cb_list[i]['bg']='white'
        selected = [cb_vars[i].get() for i in range(len(cb_vars))]
        if cb_vars[var].get():
            cb_list[var]['bg']='yellow'
        else:
            cb_list[var]['bg']='white'
    

    
    # Create a list to store the checkbox variables
    cb_vars = []
       
    #The title of the window
    label=tk.Label(window, text=title, font=("Helvetica", 10))
    label.grid(row=0, column=0, pady=5)
    
    textframe=ScrolledText(window, width=40, height=50)
    textframe.grid(row=1, column=0, sticky='ewns')
    cb_list=[]
    # Create a 4-column grid of checkboxes
    for i, item in enumerate(items):
        cb_var = tk.BooleanVar()
        cb = tk.Checkbutton(textframe, text=item, variable=cb_var,
                            command=lambda var=i: update_selected(var), 
                            font=("Arial",10),fg="black", bg="white")
        
        cb_list.append(cb)
        textframe.window_create('end', window=cb)
        textframe.insert('end', '\n')
        cb_vars.append(cb_var)
        if defaults[i]:
            cb.select()
            cb['bg']='yellow'

    # Create a "Submit" button
    submit_button = tk.Button(window, text="Submit", command=lambda: window.destroy())
    submit_button.grid(row=2, column=0)
    
    # Run the main loop
    window.mainloop()
    selected_indexes = np.array([i for i, x in enumerate(selected) if x])
    return selected_indexes






#function for calling unique values with order retained.
def unique(list1):
    array1=np.array(list1)
    indx=np.unique(array1, return_index=True)[1]
    indx.sort()
    uarray=array1[indx]
    return uarray







#Enter name for file
def textinputbox(title=""):
    #setup the window
    root=tk.Tk()
    
    w = 200 # width for the Tk root
    h = 100 # height for the Tk root
    
    # get screen width and height
    ws = root.winfo_screenwidth() # width of the screen
    hs = root.winfo_screenheight() # height of the screen
    
    # calculate x and y coordinates for the Tk root window
    x = (ws/2) - (w/2)
    y = (hs/2) - (h/2)
    
    # set the dimensions of the screen 
    # and where it is placed
    root.geometry('%dx%d+%d+%d' % (w, h, x, y))
    
    #make sure scrolling area always fills the window area
    root.rowconfigure(1, weight=3)
    root.rowconfigure(0, weight=2)
    root.columnconfigure(0, weight=1)
    
    #The title of the window
    label=tk.Label(root, text=title, font=("Helvetica", 14))
    label.grid(row=0, column=0, pady=5)
    
    #Button function that saves input value and closes the window
    def retrieve_input():
        global inputValue
        inputValue=textBox.get("1.0","end-1c")
        root.destroy()
    #Text input
    textBox=tk.Text(root, height=2, width=10)
    textBox.grid(row=1, column=0, sticky='ewns')
    #Save button (see function above)
    buttonSave=tk.Button(root, height=1, width=10, text="Save", 
                        command=lambda: retrieve_input())
    buttonSave.grid(row=2, column=0)  
    
    tk.mainloop()   
    return inputValue   






def outsbool(array1, mod=1.5):
    """
    Returns boolean array where true values denote outliers in original array
    
    Parameters
    ----------
    array1 : 1d or 2d array (numpy array)
        array to search for outliers.
    mod : modifier of outlier distance (iqr multiplier), default 1.5.

    Returns
    -------
    retarray : numpy array of len(array1)
        An array of boolean values where True values indicate the presence of 
        outliers at the same index of array1.

    """

    array1=array1.flatten()
    x = array1[~np.isnan(array1)]
    if len(x)>2:
        q75, q25 = np.percentile(x, [75 ,25])
        iqr = q75 - q25
        outs=((array1>iqr*mod+q75) | (array1<q25-iqr*mod))
    else:
        outs=np.isnan(array1)
        
    return outs





def pickfig(df, xvar, title):
    global selected_ind, variable
    df[xvar]=df[xvar]/3600
    df2=df.copy()
    variable=df.columns[df.columns!=xvar][0]
    selected_ind=np.array([], dtype=int)
          
    def on_pick(event):
        global ind, selected_ind
        ind = event.ind
    
        newind=np.setdiff1d(ind, selected_ind)
        
        if newind.size>0:
            selected_ind=np.append(selected_ind, newind)
            df2.iloc[ind]=np.nan
            scatter2.set_data(df2[xvar], df2[variable])
            fig.canvas.draw_idle()
            
        else:
            selected_ind=np.setdiff1d(selected_ind, ind)
            df2.iloc[ind]=df.iloc[ind]
            scatter2.set_data(df2[xvar], df2[variable])
            fig.canvas.draw_idle()
    
    
 
    # Create the initial plot without showing the figure
    fig, ax = plt.subplots()
    scatter1, = ax.plot([], [], linestyle='None', marker='o', color='red', picker=5)
    scatter2, = ax.plot([], [], linestyle='None', marker='o', color='blue')
    ax.set_xlabel('Analysis time (hours)')
    ax.set_ylabel(variable)
    ax.legend(['Remove', 'Keep'])
    
    
    
    # Register the pick event
    fig.canvas.mpl_connect('pick_event', on_pick)
    
    plt.close(fig)  # Close the figure to prevent it from being displayed
    
    
    # Define the update function for the dropdown
    def update_y_axis(*args):
        global variable
        variable = dropdown_var.get()
        scatter1.set_data(df[xvar], df[variable])
        scatter2.set_data(df2[xvar], df2[variable])
        ax.set_ylabel(variable)
        ax.relim()
        ax.autoscale_view()
        fig.canvas.draw_idle()
    
    # Create the Tkinter window
    window = tk.Tk()
    window.title(title)
    
    
    # Create a label for the dropdown menu
    label = tk.Label(window, text="Choose an isotope")
    label.pack(padx=10, pady=5)
    
    # Create the dropdown menu
    dropdown_var = tk.StringVar(window)
    dropdown_var.set(df.columns[df.columns!=xvar][0])  # Set default value
    dropdown = tk.OptionMenu(window, dropdown_var, *df.columns[df.columns!=xvar], 
                             command=update_y_axis)
    dropdown.pack(padx=10, pady=10)
    
    
    submit_button = tk.Button(window, text="Submit", 
                              command=lambda: window.destroy())
    submit_button.pack( side = tk.BOTTOM)


    
    
    # Create the FigureCanvasTkAgg object
    canvas = FigureCanvasTkAgg(fig, master=window)
    canvas.draw()
    canvas.get_tk_widget().pack()
    
    # Run the Tkinter event loop
    window.mainloop()
    
    
    return np.array(df.index[selected_ind])









def pickfig_cross(dfy, dfx, variables, title=None, fitted=None):
    global selected_ind, variable
    dfx2=dfx.copy()
    variable=variables[0]
    selected_ind={k: np.array([], dtype=int) for k in variables}
    
    
    def on_pick(event):
        global ind, selected_ind
        ind = dfx.index[event.ind]
        
    
        newind=np.setdiff1d(ind, selected_ind[variable])
        
        if newind.size>0:
            selected_ind[variable]=np.append(selected_ind[variable], newind)
            dfx2.loc[ind, variable]=np.nan
            scatter2.set_data(dfx2[variable], dfy[variable])
            fig.canvas.draw_idle()
            
        else:
            selected_ind[variable]=np.setdiff1d(selected_ind[variable], ind)
            dfx2.loc[ind, variable]=dfx.loc[ind, variable]
            scatter2.set_data(dfx2[variable], dfy[variable])
            fig.canvas.draw_idle()
            
 
 
    # Create the initial plot without showing the figure
    fig, ax = plt.subplots()
    scatter1, = ax.plot([], [], linestyle='None', marker='o', color='red', picker=True)
    scatter2, = ax.plot([], [], linestyle='None', marker='o', color='blue')
    if all(fitted!=None):
        fit1=ax.plot([], [], linestyle='-', marker=None, color='black')
    ax.set_xlabel(variable)
    ax.set_ylabel(variable)
    ax.legend(['Remove', 'Keep'])
    
    
    
    # Register the pick event
    fig.canvas.mpl_connect('pick_event', on_pick)
    
    plt.close(fig)  # Close the figure to prevent it from being displayed
    
    
    # Define the update function for the dropdown
    def update_y_axis(*args):
        global variable
        variable = dropdown_var.get()
        scatter1.set_data(dfx[variable], dfy[variable])
        scatter2.set_data(dfx2[variable], dfy[variable])
        if all(fitted!=None):
            fit1[0].set_data(dfx[variable], fitted[variable])
        ax.set_ylabel(variable)
        ax.set_xlabel(variable)
        ax.relim()
        ax.autoscale_view()
        fig.canvas.draw_idle()
        
    
    # Create the Tkinter window
    window = tk.Tk()
    window.title(title)
    
    
    # Create a label for the dropdown menu
    label = tk.Label(window, text="Choose an isotope")
    label.pack(padx=10, pady=5)
    
    # Create the dropdown menu
    dropdown_var = tk.StringVar(window)
    dropdown_var.set(variables[0])  # Set default value
    dropdown = tk.OptionMenu(window, dropdown_var, *variables, 
                             command=update_y_axis)
    dropdown.pack(padx=10, pady=10)
    
    
    submit_button = tk.Button(window, text="Submit", 
                              command=lambda: window.destroy())
    submit_button.pack( side = tk.BOTTOM)

    # Create the FigureCanvasTkAgg object
    canvas = FigureCanvasTkAgg(fig, master=window)
    canvas.draw()
    canvas.get_tk_widget().pack()
    
    # Run the Tkinter event loop
    window.mainloop()
    
    
    return selected_ind






def blankfigsaver(df1, df2, iso_vars, variable='CPS mean',  title='Blanks CPS',  
                  xvar='Acq. Date-Time'):
    global iso
    iso=iso_vars[0]
    
    #Isolate one element
    df1_el=df1.loc[df1['Isotope gas']==iso]
    if df1_el.size>0:
        outs=outsbool(np.array(df1_el[variable]))
        df1_el=df1_el.loc[~outs]
    df2_el=df2.loc[df2['Isotope gas']==iso]
    
    def saveonefig():        
        #Save the current figure
        fig.savefig(figpath+'/'+title+iso+'.png')
        
    def saveallfig():   
        
         #reset the progressbar
         progressbar['value']=0  
         progressbar.update()
         
         for j, el in enumerate(iso_vars):
            
            #increment the progressbar
            progressbar['value']=(j+1)/len(iso_vars)*100
            progressbar.update()
                 
            #get the specific isotope data 
            df1_elb=df1.loc[df1['Isotope gas']==el]
            #remove outliers from archive
            if df1_elb.size>0:
                outs=outsbool(np.array(df1_elb[variable]))
                df1_elb=df1_elb.loc[~outs]
            df2_elb=df2.loc[df2['Isotope gas']==el]
               
            #plot figure
            figall, ax = plt.subplots()
            figall.set_figheight(6)
            figall.set_figwidth(12)
            #Archive data 
            scatter1 = ax.scatter(df1_elb[xvar].astype('datetime64[ns]'), 
                            df1_elb[variable],
                            linestyle='None', marker='o', color='blue', s=4)
            #Batch data 
            scatter2 = ax.scatter(df2_elb[xvar].astype('datetime64[ns]'), 
                            df2_elb[variable], 
                            linestyle='None', marker='o', color='red', s=4)
                                    
            ax.xaxis.set_tick_params(rotation=45)
            ax.set_xlabel(xvar)
            ax.set_ylabel(variable+' '+el)
            ax.legend(['Archive', 'This run'])
            figall.savefig(figpath+'/'+title+el+'.png')
            plt.close(figall)
              
     
              
     
    #turn off interactive plotting
    plt.ioff()

    
    # Create the initial plot without showing the figure
    fig, ax = plt.subplots()   
    #Archive data
    scatter1 = ax.scatter(df1_el[xvar].astype('datetime64[ns]'), 
                    df1_el[variable],
                    linestyle='None', marker='o', color='blue', s=4)
    #Batch data
    scatter2 = ax.scatter(df2_el[xvar].astype('datetime64[ns]'), 
                    df2_el[variable],
                    linestyle='None', marker='o', color='red', s=4)
    ax.xaxis.set_tick_params(rotation=45)
    ax.set_xlabel(xvar)
    ax.set_ylabel(variable+' '+iso)
    ax.legend(['Archive', 'This run'])
    
    plt.close(fig)  # Close the figure to prevent it from being displayed
    
    
    # Define the update function for the dropdown
    def update_y_axis(*args):
        global iso
        iso = dropdown_var.get()
        #Get specific isotope data, remove outliers from archive   
        df1_el=df1.loc[df1['Isotope gas']==iso]
        if df1_el.size>0:
            outs=outsbool(np.array(df1_el[variable]))
            df1_el=df1_el.loc[~outs]        
        
        df2_el=df2.loc[df2['Isotope gas']==iso]
        
        #clear the old data from the plot
        ax.cla()
        #add new data from selected isotope
        scatter1 = ax.scatter(df1_el[xvar].astype('datetime64[ns]'), 
                        df1_el[variable], 
                        linestyle='None', marker='o', color='blue', s=4)
        
        scatter2 = ax.scatter(df2_el[xvar].astype('datetime64[ns]'), 
                        df2_el[variable],
                        linestyle='None', marker='o', color='red', s=4)
        ax.xaxis.set_tick_params(rotation=45)
        plt.xticks(rotation = 45)
        ax.set_xlabel(xvar)
        ax.set_ylabel(variable+' '+iso)
        ax.legend(['Archive', 'This run'])
        fig.canvas.draw_idle()
    
    # Create the Tkinter window
    window = tk.Tk()
    window.geometry("1000x800")
    window.title(title)
       
    
    button_frame = tk.Frame(window)
    button_frame.pack(side=tk.TOP, padx=10, pady=10)
    
    # Create a label for the dropdown menu
    label = tk.Label(button_frame, text="Choose the isotope")
    label.pack(side=tk.LEFT)
    
    # Create the dropdown menu
    dropdown_var = tk.StringVar(window)
    dropdown_var.set(iso_vars[0])  # Set default value
    dropdown = tk.OptionMenu(button_frame, dropdown_var, *iso_vars, 
                             command=update_y_axis)
    dropdown.pack(side=tk.LEFT)
    
    button_frame2 = tk.Frame(window)
    button_frame2.pack(side=tk.BOTTOM)
    
    figure_frame = tk.Frame(window)
    figure_frame.pack(fill=tk.BOTH,  side=tk.TOP)
    
    
    # Create the FigureCanvasTkAgg object
    canvas = FigureCanvasTkAgg(fig, master=figure_frame)
    canvas.draw()
    canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, ipady=20)
    
    
    #progress bar
    progressbar = ttk.Progressbar(window, orient=tk.HORIZONTAL, length=400)
    progressbar.pack(side=tk.BOTTOM)
  
    
    Save_button = tk.Button(button_frame2, text="Save", 
                              command=saveonefig)
    SaveAll_button = tk.Button(button_frame2, text="Save all", 
                              command=saveallfig)
    Exit_button = tk.Button(button_frame2, text="Exit", 
                              command=lambda: window.destroy())
    
    Save_button.pack(side=tk.LEFT)
    SaveAll_button.pack(side=tk.LEFT)
    Exit_button.pack(side=tk.LEFT)

    # Run the Tkinter event loop
    window.mainloop()
      
    
    
    


def stdfigsaver(df1, df2, title, iso_vars, expected,
                variables=['Cali_single', 'Cali_curve'],  
                errors=['Cali_single_se', 'Cali_curve_se'],  
             xvar='Acq. Date-Time'):
    global iso
    #set default value for the isotope
    iso=iso_vars[0]
    
    #Make a colour map to for shading different bracketing standards
    cmap = matplotlib.colormaps['rainbow'].resampled(len(unique(df1['BrktStnd'])))
    
    
    #this will be a list of the archive dataframes with each entry corresponding
    #to a different bracketing standard used.
    df1_ls=[]
    #cycle through the different bracketing standards
    for brk in unique(df1['BrktStnd']):
         
        #Subset the dataframe for the given isotope and bracketing standard
        df1_el=df1.loc[(df1['Isotope gas']==iso)&(df1['BrktStnd']==brk)]
        #If dataframe isn't empty, remove outliers in single-point data 
        if (df1_el[variables[0]].size>0) & (any(~np.isnan(df1_el[variables[0]]))):
            outs_s=outsbool(np.array(df1_el[variables[0]]))
            outs_s=outs_s | outsbool(np.array(df1_el[errors[0]]))
            df1_el.loc[outs_s, variables[0]]=np.nan       
            #If cali-curve isn't empty, remove outliers in cali-curve data 
            if (df1_el[variables[1]].size>0) & (any(~np.isnan(df1_el[variables[1]]))):
                outs_c=outsbool(np.array(df1_el[variables[1]]))
                outs_c=outs_c | outsbool(np.array(df1_el[errors[1]]))
                df1_el.loc[outs_c, variables[1]]=np.nan
        #add to the dataframe list
        df1_ls.append(df1_el)
        
    #subset the run dataframe for the given isotope 
    df2_el=df2.loc[df2['Isotope gas']==iso]
    
    
    
    #Save the current figure
    def saveonefig():        
        fig.savefig(figpath+'/'+title+'_'+iso+'.png')
    
    #Save all figures
    def saveallfig():  
         
        #reset the progressbar
        progressbar['value']=0  
        progressbar.update()
                
        #cycle through each isotope
        for j, el in enumerate(iso_vars):

            #increment the progressbar
            progressbar['value']=(j+1)/len(iso_vars)*100
            progressbar.update()
                
                
            #adjust the dataframes
            #this will be a list of the archive dataframes with each entry corresponding
            #to a different bracketing standard used.
            df1_ls=[]
            #cycle through the different bracketing standards
            for brk in unique(df1['BrktStnd']):
                 
                #Subset the dataframe for the given isotope and bracketing standard
                df1_el=df1.loc[(df1['Isotope gas']==el)&(df1['BrktStnd']==brk)]
                #If dataframe isn't empty, remove outliers in single-point data 
                if (df1_el[variables[0]].size>0) & (any(~np.isnan(df1_el[variables[0]]))):
                    outs_s=outsbool(np.array(df1_el[variables[0]]))
                    outs_s=outs_s | outsbool(np.array(df1_el[errors[0]]))
                    df1_el.loc[outs_s, variables[0]]=np.nan       
                    #If cali-curve isn't empty, remove outliers in cali-curve data 
                    if (df1_el[variables[1]].size>0) & (any(~np.isnan(df1_el[variables[1]]))):
                        outs_c=outsbool(np.array(df1_el[variables[1]]))
                        outs_c=outs_c | outsbool(np.array(df1_el[errors[1]]))
                        df1_el.loc[outs_c, variables[1]]=np.nan
                #add to the dataframe list
                df1_ls.append(df1_el)
                
                #subset the run dataframe for the given isotope 
                df2_el=df2.loc[df2['Isotope gas']==el]
            
      
            # Create the initial plot without showing the figure
            figall, ax = plt.subplots(nrows=1, ncols=2, sharex=True, sharey=True)   
            figall.set_figheight(6)
            figall.set_figwidth(12)
                
            #Cycle through bracketing standards in the archive data
            for i, brk in enumerate(unique(df1['BrktStnd'])):
                
                #Single-point calibration archive data
                if any(~np.isnan(df1_ls[i][variables[0]])):
                    
                    #shaded area showing +/-2SD
                    ystdev2=df1_ls[i][variables[0]].std()*2
                    ymean=df1_ls[i][variables[0]].mean()
                    ax[0].axhspan(ymean-ystdev2, ymean+ystdev2, 
                                  alpha=0.2, color=cmap(i), 
                                  label='Archive calibrated by '+brk+r'$\mu \pm2\sigma$')
                    #Archive data with +/-1SE errorbars
                    scatter1_s = ax[0].errorbar(df1_ls[i][xvar].astype('datetime64[ns]'), 
                                    df1_ls[i][variables[0]], yerr=df1_ls[i][errors[0]],
                                    linestyle='None', marker='.', 
                                    color=cmap(i), ms=4, 
                                    label='Archive calibrated by '+brk+r'$ \pm1\sigma$')
                 
                #Calibation curve archive data    
                if any(~np.isnan(df1_ls[i][variables[1]])):    
                    
                    #shaded area showing +/-2SD
                    ystdev2=df1_ls[i][variables[1]].std()*2
                    ymean=df1_ls[i][variables[1]].mean()
                    ax[1].axhspan(ymean-ystdev2, ymean+ystdev2, 
                                  alpha=0.2, color=cmap(i), 
                                  label='Archive calibrated by '+brk+r'$\mu \pm2\sigma$')
                    #Archive data with +/-1SE errorbars
                    scatter1_c = ax[1].errorbar(df1_ls[i][xvar].astype('datetime64[ns]'), 
                                    df1_ls[i][variables[1]], yerr=df1_ls[i][errors[1]],
                                    linestyle='None', marker='.', 
                                    color=cmap(i), ms=4, 
                                    label='Archive calibrated by '+brk+r'$ \pm1\sigma$')
                
            #Single-point run data with +/-1SE errorbars       
            scatter2_s = ax[0].errorbar(df2_el[xvar].astype('datetime64[ns]'), 
                                df2_el[variables[0]], yerr=df2_el[errors[0]],
                                linestyle='None', marker='s', color='black', ms=4, 
                                label='This run'+r'$ \pm1\sigma$')

            
            if any(df2_el.columns == variables[1]):
                #Calibration curve run data with +/-1SE errorbars
                scatter2_c = ax[1].errorbar(df2_el[xvar].astype('datetime64[ns]'), 
                                df2_el[variables[1]], yerr=df2_el[errors[1]],
                                linestyle='None', marker='s', color='black', ms=4, 
                                label='This run'+r'$ \pm1\sigma$')
                
            
            
            #draw expected values
            if ~np.isnan(expected[el]):
                ax[0].axhline(expected[el], color='black', label='Expected', ls='--')
                ax[1].axhline(expected[el], color='black', label='Expected', ls='--')
            
            #Legend    
            handles,labels = ax[0].get_legend_handles_labels()
            ax[0].legend(handles, labels)
            handles,labels = ax[1].get_legend_handles_labels()
            ax[1].legend(handles, labels)
            
            #Titles and tick marks
            ax[0].title.set_text('Single-point')
            ax[1].title.set_text('Calibration curve')
            ax[0].xaxis.set_tick_params(rotation=45)
            ax[1].xaxis.set_tick_params(rotation=45)
            #Axes labels
            ax[0].set_xlabel(xvar)
            ax[1].set_xlabel(xvar)
            ax[0].set_ylabel(el)
            #Main title
            figall.suptitle(title)
            
            
            figall.savefig(figpath+'/'+title+'_'+el+'.png')
            plt.close(figall)
            #plt.show()   
    
 
    #turn off interactive plotting
    plt.ioff()
    
    
    # Create the initial plot without showing the figure
    fig, ax = plt.subplots(nrows=1, ncols=2, sharex=True, sharey=True)   
    
    #Cycle through bracketing standards in the archive data
    for i, brk in enumerate(unique(df1['BrktStnd'])):
        
        #Single-point calibration archive data
        if any(~np.isnan(df1_ls[i][variables[0]])):
            
            #shaded area showing +/-2SD
            ystdev2=df1_ls[i][variables[0]].std()*2
            ymean=df1_ls[i][variables[0]].mean()
            ax[0].axhspan(ymean-ystdev2, ymean+ystdev2, 
                          alpha=0.2, color=cmap(i), 
                          label='Archive calibrated by '+brk+r'$\mu \pm2\sigma$')
            #Archive data with +/-1SE errorbars
            scatter1_s = ax[0].errorbar(df1_ls[i][xvar].astype('datetime64[ns]'), 
                            df1_ls[i][variables[0]], yerr=df1_ls[i][errors[0]],
                            linestyle='None', marker='.', 
                            color=cmap(i), ms=4, 
                            label='Archive calibrated by '+brk+r'$ \pm1\sigma$')
         
        #Calibation curve archive data    
        if any(~np.isnan(df1_ls[i][variables[1]])):    
            
            #shaded area showing +/-2SD
            ystdev2=df1_ls[i][variables[1]].std()*2
            ymean=df1_ls[i][variables[1]].mean()
            ax[1].axhspan(ymean-ystdev2, ymean+ystdev2, 
                          alpha=0.2, color=cmap(i), 
                          label='Archive calibrated by '+brk+r'$\mu \pm2\sigma$')
            #Archive data with +/-1SE errorbars
            scatter1_c = ax[1].errorbar(df1_ls[i][xvar].astype('datetime64[ns]'), 
                            df1_ls[i][variables[1]], yerr=df1_ls[i][errors[1]],
                            linestyle='None', marker='.', 
                            color=cmap(i), ms=4, 
                            label='Archive calibrated by '+brk+r'$ \pm1\sigma$')
        
    #Single-point run data with +/-1SE errorbars       
    scatter2_s = ax[0].errorbar(df2_el[xvar].astype('datetime64[ns]'), 
                        df2_el[variables[0]], yerr=df2_el[errors[0]],
                        linestyle='None', marker='s', color='black', ms=4, 
                        label='This run'+r'$ \pm1\sigma$')

    
    if any(df2_el.columns == variables[1]):
        #Calibration curve run data with +/-1SE errorbars
        scatter2_c = ax[1].errorbar(df2_el[xvar].astype('datetime64[ns]'), 
                        df2_el[variables[1]], yerr=df2_el[errors[1]],
                        linestyle='None', marker='s', color='black', ms=4, 
                        label='This run'+r'$ \pm1\sigma$')
        
    
    
    #draw expected values
    if ~np.isnan(expected[iso]):
        ax[0].axhline(expected[iso], color='black', label='Expected', ls='--')
        ax[1].axhline(expected[iso], color='black', label='Expected', ls='--')
    
    #Legend    
    handles,labels = ax[0].get_legend_handles_labels()
    ax[0].legend(handles, labels)
    handles,labels = ax[1].get_legend_handles_labels()
    ax[1].legend(handles, labels)
    
    #Titles and tick marks
    ax[0].title.set_text('Single-point')
    ax[1].title.set_text('Calibration curve')
    ax[0].xaxis.set_tick_params(rotation=45)
    ax[1].xaxis.set_tick_params(rotation=45)
    #Axes labels
    ax[0].set_xlabel(xvar)
    ax[1].set_xlabel(xvar)
    ax[0].set_ylabel(iso)
    #Main title
    fig.suptitle(title)

    plt.close(fig)  # Close the figure to prevent it from being displayed
    
    
    
    
    
    
    # Define the update function for the dropdown
    def update_y_axis(*args):
        global iso
            
        
        #set the isotope
        iso = dropdown_var.get()
        
      
        #this will be a list of the archive dataframes with each entry corresponding
        #to a different bracketing standard used.
        df1_ls=[]
        #cycle through the different bracketing standards
        for brk in unique(df1['BrktStnd']):
             
            #Subset the dataframe for the given isotope and bracketing standard
            df1_el=df1.loc[(df1['Isotope gas']==iso)&(df1['BrktStnd']==brk)]
            #If dataframe isn't empty, remove outliers in single-point data 
            if (df1_el[variables[0]].size>0) & (any(~np.isnan(df1_el[variables[0]]))):
                outs_s=outsbool(np.array(df1_el[variables[0]]))
                outs_s=outs_s | outsbool(np.array(df1_el[errors[0]]))
                df1_el.loc[outs_s, variables[0]]=np.nan       
                #If cali-curve isn't empty, remove outliers in cali-curve data 
                if (df1_el[variables[1]].size>0) & (any(~np.isnan(df1_el[variables[1]]))):
                    outs_c=outsbool(np.array(df1_el[variables[1]]))
                    outs_c=outs_c | outsbool(np.array(df1_el[errors[1]]))
                    df1_el.loc[outs_c, variables[1]]=np.nan
            #add to the dataframe list
            df1_ls.append(df1_el)
            
        #subset the run dataframe for the given isotope 
        df2_el=df2.loc[df2['Isotope gas']==iso]

        #clear the axes
        ax[0].cla()
        ax[1].cla()
        
        
        
      
        #Cycle through bracketing standards in the archive data
        for i, brk in enumerate(unique(df1['BrktStnd'])):
            
            #Single-point calibration archive data
            if any(~np.isnan(df1_ls[i][variables[0]])):
                
                #shaded area showing +/-2SD
                ystdev2=df1_ls[i][variables[0]].std()*2
                ymean=df1_ls[i][variables[0]].mean()
                ax[0].axhspan(ymean-ystdev2, ymean+ystdev2, 
                              alpha=0.2, color=cmap(i), 
                              label='Archive calibrated by '+brk+r'$\mu \pm2\sigma$')
                #Archive data with +/-1SE errorbars
                scatter1_s = ax[0].errorbar(df1_ls[i][xvar].astype('datetime64[ns]'), 
                                df1_ls[i][variables[0]], yerr=df1_ls[i][errors[0]],
                                linestyle='None', marker='.', 
                                color=cmap(i), ms=4, 
                                label='Archive calibrated by '+brk+r'$ \pm1\sigma$')
             
            #Calibation curve archive data    
            if any(~np.isnan(df1_ls[i][variables[1]])):    
                
                #shaded area showing +/-2SD
                ystdev2=df1_ls[i][variables[1]].std()*2
                ymean=df1_ls[i][variables[1]].mean()
                ax[1].axhspan(ymean-ystdev2, ymean+ystdev2, 
                              alpha=0.2, color=cmap(i), 
                              label='Archive calibrated by '+brk+r'$\mu \pm2\sigma$')
                #Archive data with +/-1SE errorbars
                scatter1_c = ax[1].errorbar(df1_ls[i][xvar].astype('datetime64[ns]'), 
                                df1_ls[i][variables[1]], yerr=df1_ls[i][errors[1]],
                                linestyle='None', marker='.', 
                                color=cmap(i), ms=4, 
                                label='Archive calibrated by '+brk+r'$ \pm1\sigma$')
            
        #Single-point run data with +/-1SE errorbars       
        scatter2_s = ax[0].errorbar(df2_el[xvar].astype('datetime64[ns]'), 
                            df2_el[variables[0]], yerr=df2_el[errors[0]],
                            linestyle='None', marker='s', color='black', ms=4, 
                            label='This run'+r'$ \pm1\sigma$')

        
        if any(df2_el.columns == variables[1]):
            #Calibration curve run data with +/-1SE errorbars
            scatter2_c = ax[1].errorbar(df2_el[xvar].astype('datetime64[ns]'), 
                            df2_el[variables[1]], yerr=df2_el[errors[1]],
                            linestyle='None', marker='s', color='black', ms=4, 
                            label='This run'+r'$ \pm1\sigma$')
            
        
        
        #draw expected values
        if ~np.isnan(expected[iso]):
            ax[0].axhline(expected[iso], color='black', label='Expected', ls='--')
            ax[1].axhline(expected[iso], color='black', label='Expected', ls='--')
        
        #Legend    
        handles,labels = ax[0].get_legend_handles_labels()
        ax[0].legend(handles, labels)
        handles,labels = ax[1].get_legend_handles_labels()
        ax[1].legend(handles, labels)
        
        #Titles and tick marks
        ax[0].title.set_text('Single-point')
        ax[1].title.set_text('Calibration curve')
        ax[0].xaxis.set_tick_params(rotation=45)
        ax[1].xaxis.set_tick_params(rotation=45)
        #Axes labels
        ax[0].set_xlabel(xvar)
        ax[1].set_xlabel(xvar)
        ax[0].set_ylabel(iso)
        #plt.show()
        
        fig.canvas.draw_idle()
        
  
    
    # Create the Tkinter window
    window = tk.Tk()
    
    width= window.winfo_screenwidth()*0.9               
    height= window.winfo_screenheight()*0.85               
    window.geometry("%dx%d" % (width, height))
    window.title(title)
    
    
    
    
    button_frame = tk.Frame(window)
    button_frame.pack(side=tk.TOP, padx=10, pady=10)
    
    # Create a label for the dropdown menu
    label = tk.Label(button_frame, text="Choose the isotope")
    label.pack(side=tk.LEFT)
    
    # Create the dropdown menu
    dropdown_var = tk.StringVar(window)
    dropdown_var.set(iso_vars[0])  # Set default value
    dropdown = tk.OptionMenu(button_frame, dropdown_var, *iso_vars, 
                             command=update_y_axis)
    dropdown.pack(side=tk.LEFT)
    
    button_frame2 = tk.Frame(window)
    button_frame2.pack(side=tk.BOTTOM)
    
    figure_frame = tk.Frame(window)
    figure_frame.pack(fill=tk.BOTH,  side=tk.TOP)
    
    
    # Create the FigureCanvasTkAgg object
    canvas = FigureCanvasTkAgg(fig, master=figure_frame)
    canvas.draw()
    canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, ipady=20)
    
    
    
    
    
    Save_button = tk.Button(button_frame2, text="Save", 
                              command=saveonefig)
    SaveAll_button = tk.Button(button_frame2, text="Save all", 
                              command=saveallfig)
    Exit_button = tk.Button(button_frame2, text="Exit", 
                              command=lambda: window.destroy())
    
    Save_button.pack(side=tk.LEFT)
    SaveAll_button.pack(side=tk.LEFT)
    Exit_button.pack(side=tk.LEFT)


    #progress bar
    progressbar = ttk.Progressbar(window, orient=tk.HORIZONTAL, length=400)
    progressbar.pack(side=tk.BOTTOM)
  
    
    # Run the Tkinter event loop
    window.mainloop()













########Directories###########

#Select directory for new data import
root=tk.Tk()
root.withdraw()
root.attributes('-topmost', True)
folder_select=filedialog.askdirectory()
root.destroy()


#Standard data
stndpath=(r"stndvals.csv")
#Archived data
archivepath=path=(r"AgilentArchive.csv")



#Flicker
flick=0.003



#############Import data #################


#load archive data and set datetimes
archive_df=pd.read_csv(archivepath, index_col=0)  
archive_df['Acq. Date-Time']=pd.to_datetime(archive_df['Acq. Date-Time'], 
                                        dayfirst=True)
archive_df['Elapse']=pd.to_timedelta(archive_df['Elapse']).dt.total_seconds()



#New data import
#reads batch file
folder_list=os.listdir(folder_select)
Batchlogloc=folder_select+'/BatchLog.csv'
batchdf=pd.read_csv(folder_select+'/BatchLog.csv') 
#gets time string and converts to datetime
batchdf['Acq. Date-Time']=pd.to_datetime(batchdf.iloc[:, 1]) 
batch_t=batchdf[(batchdf['Acquisition Result']=='Pass') & \
                (batchdf["Sample Type"].str.contains("Tune")==False)].copy()


#Get the runname
fsplit=folder_select.split('/')
runname=fsplit[-1]

#Get a list of the sample names, make them into directories and put them into the main df
values=[]
for i in batch_t["File Name"]:
    sfsplit=i.split('\\')    
    values.append(folder_select+'/'+sfsplit[-1])
   # print(sfsplit[-1])
batch_t['Sample Folder']=values
batch_t=batch_t.reset_index()
#Setup run info table
Run_df=pd.DataFrame(np.repeat(runname, len(batch_t)), columns=['Run Name'])
Run_df=pd.concat([Run_df, batch_t[['Acq. Date-Time', 'Sample Name', 'Vial#']]],
                 axis=1)

#Get the total elapsed time since first sample
Run_df['Elapse']=batch_t['Acq. Date-Time']-batch_t.loc[0,'Acq. Date-Time']
#Convert to seconds
Run_df['Elapse']=Run_df['Elapse'].dt.total_seconds()

#empty dataframes
repCPS_all_df=pd.DataFrame()
repPA_all_df=pd.DataFrame()
repSD_all_df=pd.DataFrame()

#set up the progressbar
root=tk.Tk()
progressbar = ttk.Progressbar(root, orient=tk.HORIZONTAL, length=400)

#Keep the window at the front of other apps.
root.lift()
root.attributes("-topmost", True)


w = 300 # width for the Tk root
h = 200 # height for the Tk root

# get screen width and height
ws = root.winfo_screenwidth() # width of the screen
hs = root.winfo_screenheight() # height of the screen

# calculate x and y coordinates for the Tk root window
x = (ws/2) - (w/2)
y = (hs/2) - (h/2)

# set the dimensions of the screen 
# and where it is placed
root.geometry('%dx%d+%d+%d' % (w, h, x, y))

l = tk.Label(root, text = "Importing data, please wait...")
l.pack(side=tk.TOP)
progressbar.pack(side=tk.BOTTOM)
progressbar['value']=0  
progressbar.update()


#Start iterating through samples
for i, folder in enumerate(batch_t['Sample Folder']):   
       
    #increment the progressbar
    progressbar['value']=(i+1)/len(batch_t['Sample Folder'])*100
    progressbar.update()

    
    #Get list of subfolders containing replicates and gas modes. Exclude quickscan
    csvlist = [s for s in os.listdir(folder) if ".csv" in s and "quickscan" 
               not in s]
    
    #Find out how many repeats and gas modes there are by reading first sample
    testmode=[]
    headlist=[]
    #iterate through all files in sample directory
    for c in csvlist:
        #open each file and take the gas mode by stripping other content
        with open(folder+'/'+c, newline='') as f:
            reader = csv.reader(f)
            row1 = next(reader)[0].rsplit('/')[-1].strip('\n ')
            testmode.append(row1)
    
    #Get the number of repeats and gases by counting occurrences of gas modes
    numrepeats=testmode.count(list(set(testmode))[0])
    numgases=len(set(testmode))
    
    #Extract all data from all samples
    #Create empty lists      
    listCPS=[]
    listPA=[]
    listSD=[]
    #iterate through replicates  
    for i in range(numrepeats):
        #Empty dataframe for each repeat
        allgas_df=pd.DataFrame()
        #iterate through gas modes
        for j in range(numgases):
            fileloc=folder+'/'+csvlist[i+j*numrepeats] #directory of file
            #Read the data
            gas_df=pd.read_csv(fileloc, skiprows=list(range(0, 7)), header=0) 
            #remove print info                               
            gas_df=gas_df.drop(gas_df.tail(1).index) 
            #get the current gas mode
            gasmodetxt=testmode[i+j*numrepeats].strip(' ') 
            
            #Get the element and mass info, which is printed differently in csv
            #depending on whether using single or double quads.
            if any(contains1d(gas_df.columns, 'Q1')
                   ) & any(contains1d(gas_df.columns, 'Q2')):
                
                 gas_df["Isotope_gas"]=(gas_df["Element"]
                                        +np.array(gas_df['Q1'], 
                                                  dtype=int).astype('str')
                                        +"_"+np.array(gas_df['Q2'], 
                                                      dtype=int).astype('str')
                                        +"_"+gasmodetxt)   
                
            else:                    
                #Make df of current gas mode
                #Combine mass and element to make isotope column
                gas_df["Isotope_gas"]=(gas_df["Element"]
                                       +gas_df.iloc[:, 0]+"_"+gasmodetxt) 
                    
                    
            gas_df["Gas mode"]=gasmodetxt
                        
            #PA column often wrongly named, so need to rename it.
            #first find the column next to CPS            
            idx=np.where(gas_df.columns == 'CPS')[0]+1
            gas_df['PA']=gas_df.iloc[:, idx]
            #Concat all gas modes of this repeat
            allgas_df=pd.concat([allgas_df, gas_df], ignore_index=True)
        #extract cps, PA and stdev info from all gas modes of this repeat
        listCPS.append((np.array(allgas_df['CPS']))) 
        listPA.append((np.array(allgas_df['PA'])))
        
    
    #arrays of isotopes and gas modes used
    isotopes=np.array(allgas_df['Isotope_gas'])    
    Gasmodes=np.array(allgas_df['Gas mode']) 
    
    #Create nested list of CPS, PA and stdev replicates
    repCPS=[list(s) for s in np.vstack(listCPS).T]
    repPA=[list(s) for s in np.vstack(listPA).T]
    
               
    #Form above lists into df
    repCPS_df=pd.DataFrame([repCPS], columns=isotopes)
    repPA_df=pd.DataFrame([repPA], columns=isotopes)
   # repSD_df=pd.DataFrame([repSD], columns=isotopes)
        
    #Concatenate all samples
    repCPS_all_df=pd.concat([repCPS_all_df, repCPS_df], ignore_index=True)       
    repPA_all_df=pd.concat([repPA_all_df, repPA_df], ignore_index=True)  
    #repSD_all_df=pd.concat([repSD_all_df, repSD_df], ignore_index=True) 
            

#close the progress bar
root.destroy()

# Add in the info    
repCPS_all_df=pd.concat([Run_df, repCPS_all_df], axis=1)            
repPA_all_df=pd.concat([Run_df, repPA_all_df], axis=1)                 

#Create means and stdevs.
CPSmean=np.array([])
CPSstd=np.array([])
for lab, row in repCPS_all_df.iterrows():    
    bb=np.array([np.array([np.array(b).mean(), np.array(b).std(ddof=1)]) for
                 b in row[isotopes]])
    CPSmean=np.concatenate([CPSmean, bb[:, 0]])
    CPSstd=np.concatenate([CPSstd, bb[:, 1]])
CPSmean=CPSmean.reshape([-1, len(bb)])
CPSstd=CPSstd.reshape([-1, len(bb)])

#Make dataframes
CPSmean_df=pd.DataFrame(CPSmean, columns=isotopes)
CPSstd_df=pd.DataFrame(CPSstd, columns=isotopes)
    
# Add in the info 
CPSmean_df=pd.concat([Run_df, CPSmean_df], axis=1)            
CPSstd_df=pd.concat([Run_df, CPSstd_df], axis=1) 

#Create average P/A table
PAarray=[]
for lab, row in repPA_all_df[isotopes].iterrows(): #iterate over rows of df
    els=np.array(list(row))
    PAlist=[]
    for x in els: #iterate through elements
        if all(x=='P') | all(x=='A'):
            PAlist.append(str(x[0]))
        
        #If there is a mix of 'P' and 'A' throughout the sample then label PA
        #as 'M' for mixed.
        else:
            PAlist.append('M')
    PAarray.append(PAlist) #list of lists
    
    
PA_df=pd.DataFrame(np.array(PAarray), columns=isotopes) #make the df
PA_df=pd.concat([Run_df, PA_df], axis=1) #add the info






########## Setup processing equations ########


#Use symbolic mode to apply data processing
#Define symbols
x_sym, xb2_sym, xb1_sym, y_sym, yb2_sym, yb1_sym=sym.symbols(
    'x_sym xb2_sym xb1_sym y_sym yb2_sym yb1_sym')
xs1_sym, xs2_sym, ys1_sym, ys2_sym=sym.symbols(
    'xs1_sym xs2_sym ys1_sym ys2_sym')
Dts_sym, Dts1b_sym, Dts2b_sym, Dtb_sym=sym.symbols(
    'Dts_sym Dts1b_sym Dts2b_sym Dtb_sym')
cov_xy_sym, cov_xs1ys1_sym, cov_xs2ys2_sym, cov_xb1yb1_sym, cov_xb2yb2_sym= \
    sym.symbols('''cov_xy_sym cov_xs1ys1_sym cov_xs2ys2_sym cov_xb1yb1_sym 
    cov_xb2yb2_sym''')
s_x_sym, s_y_sym, s_xb1_sym, s_xb2_sym, s_yb1_sym, s_yb2_sym, s_xs1_sym, \
    s_xs2_sym, s_ys1_sym, s_ys2_sym=sym.symbols(
    '''s_x_sym s_y_sym s_xb1_sym s_xb2_sym s_yb1_sym s_yb2_sym s_xs1_sym 
    s_xs2_sym s_ys1_sym s_ys2_sym''')

#TE/Ca ratio equation
R_sym=(x_sym - Dtb_sym*xb2_sym + xb1_sym*(Dtb_sym - 1)
       )/(y_sym - Dtb_sym*yb2_sym + yb1_sym*(Dtb_sym - 1))
#Make into function    
R_f = sym.lambdify((x_sym, xb2_sym, xb1_sym, y_sym, yb2_sym, yb1_sym, 
                    Dtb_sym), R_sym)  

#Variance in R
R_var_sym=(s_x_sym**2*R_sym.diff(x_sym)**2+s_y_sym**2*R_sym.diff(y_sym)**2
    +s_xb1_sym**2*R_sym.diff(xb1_sym)**2+s_xb2_sym**2*R_sym.diff(xb2_sym)**2
    +s_yb1_sym**2*R_sym.diff(yb1_sym)**2+s_yb2_sym**2*R_sym.diff(yb2_sym)**2
    +2*cov_xy_sym*R_sym.diff(x_sym)*R_sym.diff(y_sym)
    +2*cov_xb1yb1_sym*R_sym.diff(xb1_sym)*R_sym.diff(yb1_sym)
    +2*cov_xb2yb2_sym*R_sym.diff(xb2_sym)*R_sym.diff(yb2_sym))
#Make into function
R_var_f = sym.lambdify((x_sym, xb2_sym, xb1_sym, y_sym, yb2_sym, yb1_sym, 
                        Dtb_sym, cov_xy_sym, cov_xb1yb1_sym, cov_xb2yb2_sym, 
                        s_x_sym, s_y_sym, s_xb1_sym, s_xb2_sym, s_yb1_sym, 
                        s_yb2_sym), R_var_sym)    


#Bracketed sample equation                    
B_sym=-((x_sym - Dtb_sym*xb2_sym + xb1_sym*(Dtb_sym - 1))/((((Dts_sym - 1)
    *(xs1_sym - Dts1b_sym*xb2_sym + xb1_sym*(Dts1b_sym - 1)))
    /(ys1_sym - Dts1b_sym*yb2_sym + yb1_sym*(Dts1b_sym - 1))
    -(Dts_sym*(xs2_sym - Dts2b_sym*xb2_sym + xb1_sym*(Dts2b_sym - 1)))
    /(ys2_sym - Dts2b_sym*yb2_sym + yb1_sym*(Dts2b_sym - 1)))
    *(y_sym - Dtb_sym*yb2_sym + yb1_sym*(Dtb_sym - 1))))

#Make into function       
B_f = sym.lambdify((x_sym, xb2_sym, xb1_sym, y_sym, yb2_sym, yb1_sym, Dtb_sym, 
              xs1_sym, ys1_sym, Dts1b_sym, xs2_sym, ys2_sym, Dts2b_sym, 
              Dts_sym), B_sym)       
    
#Variance in B    
B_var_sym=(s_x_sym**2*B_sym.diff(x_sym)**2+s_y_sym**2*B_sym.diff(y_sym)**2
    +s_xb1_sym**2*B_sym.diff(xb1_sym)**2+s_xb2_sym**2*B_sym.diff(xb2_sym)**2
    +s_xs1_sym**2*B_sym.diff(xs1_sym)**2+s_xs2_sym**2*B_sym.diff(xs2_sym)**2
    +s_yb1_sym**2*B_sym.diff(yb1_sym)**2+s_yb2_sym**2*B_sym.diff(yb2_sym)**2
    +s_ys1_sym**2*B_sym.diff(ys1_sym)**2+s_ys2_sym**2*B_sym.diff(ys2_sym)**2
    +2*cov_xy_sym*B_sym.diff(x_sym)*B_sym.diff(y_sym)
    +2*cov_xb1yb1_sym*B_sym.diff(xb1_sym)*B_sym.diff(yb1_sym)
    +2*cov_xb2yb2_sym*B_sym.diff(xb2_sym)*B_sym.diff(yb2_sym)
    +2*cov_xs1ys1_sym*B_sym.diff(xs1_sym)*B_sym.diff(ys1_sym)
    +2*cov_xs2ys2_sym*B_sym.diff(xs2_sym)*B_sym.diff(ys2_sym))


#Make into function
B_var_f = sym.lambdify((x_sym, xb2_sym, xb1_sym, y_sym, yb2_sym, yb1_sym, 
                        Dtb_sym, xs1_sym, ys1_sym, Dts1b_sym, xs2_sym, ys2_sym
                        ,Dts2b_sym, Dts_sym, cov_xy_sym, cov_xb1yb1_sym, 
                        cov_xb2yb2_sym, cov_xs1ys1_sym, cov_xs2ys2_sym, 
                        s_x_sym, s_y_sym, s_xb1_sym, s_xb2_sym,
                        s_yb1_sym, s_yb2_sym, s_xs1_sym, s_ys1_sym, s_xs2_sym, 
                        s_ys2_sym), B_var_sym)



#Counts per cycle for theoretical error
inttime_dict=dict(zip(allgas_df['Isotope_gas'], allgas_df['Time(Sec)']))
CPC_df=CPSmean_df.copy()
for iso in isotopes:
    CPC_df[iso]=CPSmean_df[iso]*inttime_dict[iso]





######### User Options #########################

#Assign default blank indexes based off sample names    
blkdefaults=list(batch_t['Sample Name'].str.contains('blk',
                                                     case=False).astype(int))

#Checkbox for selecting blanks
namelist=[str(i+1)+')  '+s for i, s in enumerate(list(batch_t['Sample Name']))]
blkrows=np.array([])
#Don't allow the window to close unless at least one blank is selected
while blkrows.size<1:
    blkrows=fancycheckbox(namelist, defaults=blkdefaults, 
                          title=("Check the blanks are selected"))

#Figure de-select outlier blanks based of counts
cpsblank=CPSmean_df.loc[blkrows, np.append('Elapse', isotopes)]
deblank=pickfig(cpsblank, 'Elapse', 'Click on blanks to remove outliers')
blkrows=blkrows[~np.in1d(blkrows, deblank)]




#Assign default bracket standard indexes based off sample names    
brktdefaults=list(batch_t['Sample Name'].str.contains('stgfrm',
                                                     case=False).astype(int))

#Use the most-common occurrence of 'STGFrm'
if sum(brktdefaults)>0:
    countbrkt=batch_t.loc[batch_t['Sample Name'].str.contains('stgfrm',case=False), 
            'Sample Name'].value_counts()   
    brktdefaults=batch_t['Sample Name']==countbrkt.index[0]
    brktdefaults=list(brktdefaults.astype(int))




brktrows=np.array([])
#Don't allow the window to close unless at least one brkt stnd is selected
while brktrows.size<1:
    brktrows=fancycheckbox(namelist, defaults=brktdefaults, 
                       title=("Check the bracketing standards are selected"))

#De-select outlier bracketing standards based of counts
cpsbrkt=CPSmean_df.loc[brktrows, np.append('Elapse', isotopes)]
debrkt=pickfig(cpsbrkt, 'Elapse', 
               'Click on bracketing standards to remove outliers')
brktrows=brktrows[~np.in1d(brktrows, debrkt)]



#iterate through gas modes to select each ratio element and store as dict
ratioels={}
isotopes_bygas={}
isotopes_bygas_element={}
for gas in unique(Gasmodes):
    gasels=isotopes[Gasmodes==gas]
    #Use Ca48 by default, second preference is Ca43
    ratioel_default=contains1d(gasels, 'Ca48')   
    if sum(ratioel_default)<1:
        ratioel_default=contains1d(gasels, 'Ca43')
    
    #User select the ratio isotope
    ratioel=gasels[fancycheckbox(gasels, defaults=ratioel_default, 
                                 single=True, title=("Select ratio isotope"
                                                     ))][0]
    #dict of ratio elements
    ratioels[gas]=ratioel
    #dict of measured full isotope names
    isotopes_bygas[gas]=gasels
    #dict of measured isotope names as element only (no mas or gas mode)
    #This is for referencing with the stndvals_df.
    isotopes_bygas_element[gas]=[
        s.split('_')[0].strip('1234567890') for s in gasels] 
    
#Select calibration method
calistyle_list=['Single-point', 'Calibration curve']
calistyle=calistyle_list[fancycheckbox(calistyle_list, defaults=[True, False],
                                       single=True, title=("Select calibration"
                                                           " method"))[0]]

calinames=unique(batch_t['Sample Name'][brktrows])
calirows=[]
if calistyle=='Calibration curve':
    #Select cali standards
    unique_names=unique(batch_t['Sample Name'])
    #default cali standard names
    calidefaults=contains1d(unique_names, ['stgfrm', 'stgcco', 'stglim',
                                        'stgcrl'])
    #remove dummy standard at beginning
    calidefaults[contains1d(unique_names, 'stgfrmx')]=False
    
    #Choose calibration standards
    #Make sure the user chooses at least 2
    calinamebool=np.array([])
    while calinamebool.size<2:
        calinamebool=fancycheckbox(unique_names, defaults=calidefaults, 
                                             title=("Select names of the "
                                                    "calibration standards"))
    calinames=unique_names[calinamebool]
    #Find them in the sequence and get the index
    calindx_default=batch_t['Sample Name'].isin(calinames)
    #Removes extra bracketing standards (those that aren't adjacent)
    #Only include as many bracketing standards in the calibration
    #as there are copies of each of the other calibration standards
    
    #find the most common calibrant quantity
    numcali=statistics.mode(batch_t['Sample Name'].value_counts()[calinames])
    
    
      
    calirows=[]
    
    #Find only adjacent calibration standards in the sequence
    for i, c in enumerate(calindx_default):
        if c and calindx_default[max([i-1, 0])]==False and \
            calindx_default[min([i+1, len(calindx_default)-1])]==False:
            calindx_default[i]=False
            
    #User select the cali stnds from sequence
    calindx=np.array([])
    while calindx.size<len(calinames):
        calindx=fancycheckbox(namelist, defaults=calindx_default, 
                              title=("Check that the correct calibration standards"
                                     " are selected"))
else:
    calinames=unique(Run_df.loc[brktrows, 'Sample Name'])
        
                
#load in the standard values set 
stndvals_df=pd.read_csv(stndpath)  
stndvals_df=stndvals_df.set_index('Element')
stndval_names=stndvals_df.columns[1:]

#make dict for elements and isotopes
isoel_dict=dict(zip(allgas_df['Isotope_gas'], allgas_df['Element']))

#Assign measured isotope names to the standard values dataframe
calivals_df=pd.DataFrame()

for i, iso in enumerate(isotopes):
    #Check if isotope is included in standard spreadsheet, if not then skip
    if all(stndvals_df.index!=isoel_dict[iso]):       
        continue
        
    #Create dataframe with standard values
    row_df=stndvals_df.loc[isoel_dict[iso], :].copy()
    row_df['Isotope']=iso
    row_df=pd.DataFrame(row_df).transpose().reset_index() 
    row_df.rename(columns={'index':'Element'}, inplace=True)
    row_df.set_index("Isotope", inplace=True)  
    calivals_df=pd.concat([calivals_df,row_df])
    
  
#Manually associate each bracketing or cali standard to one in stndvals.
stnd_dict={}
for cali in calinames:    
    associate_default=[x in cali for x in stndval_names]
    cal_associate=stndval_names[fancycheckbox(stndval_names, 
                                              defaults=associate_default,
                                              single=True, 
                                              title=("Link {} to the correct " 
                                              "standard name".format(cali)))]   
    stnd_dict[cali]=calivals_df[cal_associate].dropna()


#this will be a dictionary with isotopes to not be included in the calibration
#as keys, the values are the column indexes for the isotopes when all data is 
#an array
missing={}

brkt_df=stnd_dict[Run_df.loc[brktrows[0], 'Sample Name']]      
for i, iso in enumerate(isotopes):   
    if all(brkt_df.index!=iso):
        #note the missing isotopes for later
        missing[iso]=i
        print(i)

#get the calibration isotopes
sing_isos=isotopes.copy()
sing_isos=isotopes[~contains1d(isotopes, list(missing.keys()))].copy()



#Assign a column that describes the type of sample, standard or blank

#first assign all as 'Sample'
Run_df['Type']=['Sample']*len(Run_df)
#Then assign the blanks
Run_df.loc[blkrows, 'Type']=['Blank_'+str(x) 
                             for x in np.arange(len(blkrows))+1]
#Then the bracketing standards
Run_df.loc[brktrows, 'Type']=['Bracket_'+str(x) 
                             for x in np.arange(len(brktrows))+1]
#Then the calibration standards, if any. 
if calistyle=='Calibration curve':   
    for i, row in enumerate(calindx):
        if any(row==np.intersect1d(calindx, brktrows)):
            Run_df.loc[row, 'Type']=Run_df.loc[
                row, 'Type']+' & Calibrant_'+str(i+1)
        else:
            Run_df.loc[row, 'Type']='Calibrant_'+str(i+1)
        

        


#Ensure that all cali standards are using the same detector mode (P/A)
#Find the P/A of the bracketing standard, remove standards from cali curve that
#aren't the same P/A. 
PA_bracket_bad_index={}
if calistyle=='Calibration curve':
    PA_df_cali=PA_df.loc[calindx, :]
    for i, iso in enumerate(isotopes):   
        #The P/A of the bracketing standard       
        PAbracket=PA_df.loc[brktrows, iso]
        
        #if more than one P/A, then remove them from calibration
        if len(PAbracket.value_counts())>1:                       
            PA_bracket_bad_index[iso]=PAbracket.index[PAbracket!=PAbracket.value_counts().index[0]].values
            
        PA_df_cali[iso]==PAbracket.value_counts().index[0]  
        PAcounts=PA_df_cali[iso].value_counts()
        #list of sample names that have a different P/A to the bracketing stnd
        PA_outlier=PA_df_cali.loc[PA_df_cali[iso]!=PAbracket.value_counts(
            ).index[0], 'Sample Name']
        #Remove those stnds from the calibation curve
        if PA_outlier.shape[0]>0:       
            for st in PA_outlier:
                stnd_dict[st].loc[iso]=np.NaN
    
#Isotopes to be used in the calibration curve approach (possibly different
#from the single-point isotopes (sing_isos))
curve_isos=isotopes[~contains1d(isotopes, list(missing.keys()))].copy()





#################Processing ##################

#create array of Ca counts using different gases
y_df=Run_df.copy() #mean Ca cps
s_y_df=Run_df.copy() #sd Ca
repCPS_y_df=Run_df.copy() #replicate Ca cps
CPC_y_df=Run_df.copy() #for theoretical errors (Ca counts per cycle)
   
for gas in list(ratioels.keys()):
    #Create matrix of Ca cps values
    rat_mat=np.tile(np.array(CPSmean_df[ratioels[gas]]), 
                    [len(isotopes_bygas[gas]), 1])
    sd_mat=np.tile(np.array(CPSstd_df[ratioels[gas]]), 
                    [len(isotopes_bygas[gas]), 1])
    
    rep_mat=np.tile(np.array(repCPS_all_df[ratioels[gas]]), 
                    [len(isotopes_bygas[gas]), 1])
    #convert to data frame
    rat_df=pd.DataFrame(rat_mat.T, columns=isotopes_bygas[gas])
    y_df=pd.concat([y_df, rat_df], axis=1)
    
    sd_df=pd.DataFrame(sd_mat.T, columns=isotopes_bygas[gas])
    s_y_df=pd.concat([s_y_df, sd_df], axis=1)
    
    rep_df=pd.DataFrame(rep_mat.T, columns=isotopes_bygas[gas])
    repCPS_y_df=pd.concat([repCPS_y_df, rep_df], axis=1)
    
    CPC_y_df=pd.concat([CPC_y_df, rat_df*inttime_dict[ratioels[gas]]], axis=1)
    
    


#Generate covariances dataframe    
cov_df=pd.DataFrame([])
#cycle through samples with nested loop of isotopes to get covariances
for i, row in repCPS_all_df.iterrows():
    cov_array=np.array([])
    for iso in isotopes:
        #array of numerator isotopes
        rep_x_array=np.array(list(row[iso]))
        #array of denominators (Ca)
        rep_y_array=np.array(list(repCPS_y_df.loc[i, iso]))   
        #covariances
        cov_array=np.append(cov_array, 
                         np.cov(np.vstack((rep_x_array, rep_y_array)))[0, 1])
    #make into dataframe   
    cov_row=pd.DataFrame([cov_array], columns=isotopes)   
    cov_df=pd.concat([cov_df, cov_row], ignore_index=True)        

#Initialise final data frames using an array of NaN values
nanarray=np.full((len(Run_df),len(isotopes)),np.nan)
RunNaN_df=Run_df.copy()
RunNaN_df[isotopes]=nanarray

ratio_smpl_df=RunNaN_df.copy()
brkt_smpl_df=RunNaN_df.copy()
ratio_smpl_se_df=RunNaN_df.copy()
brkt_smpl_se_df=RunNaN_df.copy()
cali_sing_df=RunNaN_df.copy()
cali_sing_se_df=RunNaN_df.copy()
cali_curv_df=RunNaN_df.copy()
cali_curv_se_df=RunNaN_df.copy()
blkcorr_df=RunNaN_df.copy()
theo_R_rse_df=RunNaN_df.copy()
theo_Rbc_rse_df=RunNaN_df.copy()
theo_B_rse_df=RunNaN_df.copy()
theo_Bbc_rse_df=RunNaN_df.copy()


#Cycle through sample by sample to calculate R and B
for i, row in CPSmean_df.iterrows():
    #If a blank, skip
    if any(i==blkrows):
        continue
    
    #Number of blanks and stnds used for the corrections
    #find closest blank(s)
    blkorder=np.vstack((blkrows, np.abs(blkrows-i)))
    blkorder=np.vstack((blkorder, blkrows-i))
    blkorder = blkorder[:, np.argsort(blkorder[1,:], axis=0)]
    #If sample is before or after all blanks, use just one closest blank
    if np.all(blkrows-i>=0) or np.all(blkrows-i<=0):
        blk_r=np.array([blkorder[0, 0],blkorder[0, 0]])        
    #Otherwise use the two closest (braketing blanks)
    #If the first blank is before the sample in the run find one after
    elif blkorder[2, 0]<0:
        #get the next nearest blk that is of opposite sign direction away
        blk2=blkorder[0, np.where(blkorder[2, 1:]>0)[0][0]+1]          
        blk_r=np.array([blkorder[0, 0], blk2])
    #otherwise find a blank before the sample
    else:
        blk2=blkorder[0, np.where(blkorder[2, 1:]<0)[0][0]+1]          
        blk_r=np.array([blk2,blkorder[0, 0]])
           
    #find closest bracketing standard(s)
    #Make an array where the first row is the run positions of the closest 
    #bracketing standards
    #The second row is the absolute distance between the sample and the 
    #bracketing standard given in row 1
    brktorder=np.vstack((brktrows, np.abs(brktrows-i)))
    #The third row is the distance between the sample and standard with the
    #sign maintained to help determine whether they are 'bracketed'
    brktorder=np.vstack((brktorder, brktrows-i))
    #order the columns w.r.t the absolute distance
    brktorder = brktorder[:, np.argsort(brktorder[1,:], axis=0)]
    if np.all(brktrows-i>=0) or np.all(brktrows-i<=0) or any(brktrows-i==0):
        brkt_r=np.array([brktorder[0, 0],brktorder[0, 0]])
    #Otherwise use the two closest (braketing standards)
    #If the first stnd is before the sample in the run find one after
    elif brktorder[2, 0]<0:
        #get the next nearest stnd that is of opposite sign direction away
        brk2=brktorder[0, np.where(brktorder[2, 1:]>0)[0][0]+1]          
        brkt_r=np.array([brktorder[0, 0], brk2])
    #otherwise find a stnd before the sample
    else:
        brk2=brktorder[0, np.where(brktorder[2, 1:]<0)[0][0]+1]          
        brkt_r=np.array([brk2,brktorder[0, 0]])
        
        

    
          
    #Assign components of processing
    x=np.array(row[isotopes]) #TE sample
    y=np.array(y_df.loc[i, isotopes]) #Ca sample
    xb1=np.array(CPSmean_df.loc[blk_r[0], isotopes]) #TE blank 1
    yb1=np.array(y_df.loc[blk_r[0], isotopes])#Ca blank 1
    xb2=np.array(CPSmean_df.loc[blk_r[1], isotopes])#TE blank 2
    yb2=np.array(y_df.loc[blk_r[1], isotopes])#Ca blank 2
    
    xs1=np.array(CPSmean_df.loc[brkt_r[0], isotopes])#TE stnd 1
    ys1=np.array(y_df.loc[brkt_r[0], isotopes])#Ca stnd 1
    xs2=np.array(CPSmean_df.loc[brkt_r[1], isotopes])#TE stnd 2
    ys2=np.array(y_df.loc[brkt_r[1], isotopes])#Ca stnd 2
    
    #Assign fractional distance between two blanks
    if blk_r[0]==blk_r[1]:
        #If not between two blanks, then distance is 0
        Dtb=0
        Dts1b=0
        Dts2b=0
    else:
        #Sample
        Dtb=(row['Elapse']-Run_df.loc[blk_r[0], 'Elapse'])/(
            Run_df.loc[blk_r[1], 'Elapse']-Run_df.loc[blk_r[0], 'Elapse'])
        #Bracketing standard 1
        Dts1b=(Run_df.loc[brkt_r[0], 'Elapse']
               -Run_df.loc[blk_r[0], 'Elapse'])/(
                   Run_df.loc[blk_r[1], 'Elapse']
                   -Run_df.loc[blk_r[0], 'Elapse'])
        #Bracketing standard 2
        Dts2b=(Run_df.loc[brkt_r[1], 'Elapse']
               -Run_df.loc[blk_r[0], 'Elapse'])/(
                   Run_df.loc[blk_r[1], 'Elapse']
                   -Run_df.loc[blk_r[0], 'Elapse'])   
    
    #Assign fractional distance between bracketing standards
    if brkt_r[0]==brkt_r[1]:
        Dts=0
    else:
        Dts=(row['Elapse']-Run_df.loc[brkt_r[0], 'Elapse'])/(
            Run_df.loc[brkt_r[1], 'Elapse']-Run_df.loc[brkt_r[0], 'Elapse'])  
        
               
    #Find the blank-corrected values. Only necessary for LoD calulcation
    blkcorr=(row[isotopes]-Dtb*CPSmean_df.loc[blk_r[0], isotopes]
     +CPSmean_df.loc[blk_r[0], isotopes]*(Dtb-1)) 
    blkcorr_df.loc[i, isotopes]=blkcorr
    
    #Assign errors   
    s_x=np.array(CPSstd_df.loc[i, isotopes])
    s_y=np.array(s_y_df.loc[i, isotopes])
    s_xb1=np.array(CPSstd_df.loc[blk_r[0], isotopes])
    s_yb1=np.array(s_y_df.loc[blk_r[0], isotopes])
    s_xb2=np.array(CPSstd_df.loc[blk_r[1], isotopes])
    s_yb2=np.array(s_y_df.loc[blk_r[1], isotopes])
    s_xs1=np.array(CPSstd_df.loc[brkt_r[0], isotopes])
    s_ys1=np.array(s_y_df.loc[brkt_r[0], isotopes])
    s_xs2=np.array(CPSstd_df.loc[brkt_r[1], isotopes])
    s_ys2=np.array(s_y_df.loc[brkt_r[1], isotopes])
    
    #Assign covariances        
    cov_xy=np.array(cov_df.loc[i])
    cov_xb1yb1=np.array(cov_df.loc[blk_r[0]])
    cov_xb2yb2=np.array(cov_df.loc[blk_r[1]])
    cov_xs1ys1=np.array(cov_df.loc[brkt_r[0]])
    cov_xs2ys2=np.array(cov_df.loc[brkt_r[1]])
    
    
    
    
    
    
    
    
    
    
    
    
    
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        #TE count ratio and variance
        ratio_smpl=R_f(x, xb2, xb1, y, yb2, yb1, Dtb)
        ratio_smpl_var=R_var_f(x, xb2, xb1, y, yb2, yb1, Dtb, cov_xy, 
                               cov_xb1yb1, cov_xb2yb2, s_x, s_y, s_xb1, s_xb2, 
                               s_yb1, s_yb2)
        #Bracketed count ratio and variance
        brkt_smpl = B_f(x, xb2, xb1, y, yb2, yb1, Dtb, xs1, ys1, Dts1b, xs2, 
                        ys2, Dts2b, Dts)
        brkt_smpl_var=B_var_f(x, xb2, xb1, y, yb2, yb1, Dtb, xs1, ys1, Dts1b, 
                              xs2, ys2, Dts2b, Dts, cov_xy, cov_xb1yb1, 
                              cov_xb2yb2, cov_xs1ys1, cov_xs2ys2, s_x, s_y,
                              s_xb1, s_xb2, s_yb1, s_yb2, s_xs1, s_ys1, s_xs2, 
                              s_ys2)
        
    
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
    
        #c4 function for adjusting SE for low number of measurements
        c4=math.gamma(numrepeats/2)/math.gamma((numrepeats-1)/2)*(
            2/(numrepeats-1))**0.5;
        #convert variance into standard deviation
        ratio_smpl_se=ratio_smpl_var**0.5/c4/numrepeats**0.5
        brkt_smpl_se=brkt_smpl_var**0.5/c4/numrepeats**0.5
    
        #put into dataframes
        ratio_smpl_df.loc[i, isotopes]=ratio_smpl
        brkt_smpl_df.loc[i, isotopes]=brkt_smpl
        ratio_smpl_se_df.loc[i, isotopes]=ratio_smpl_se
        brkt_smpl_se_df.loc[i, isotopes]=brkt_smpl_se
    
         
        #calibration (single point)
        #delete the elements missing from the cali standard list
        b1=np.delete(brkt_smpl, list(missing.values()))
        b1_se=np.delete(brkt_smpl_se, list(missing.values()))  
         
        #make standard array based on the bracketing standard
        #Note, this does mean that different bracketing standards can be used
        #throughout the run
        cali_array=np.array(stnd_dict[Run_df.loc[brkt_r[0], 'Sample Name']])
        
        #calibrate sample to known standard values by single-point calibration
        cali_sing=b1*np.squeeze(cali_array)
        cali_sing_se=(b1_se/b1)*cali_sing
        cali_sing_df.loc[i, sing_isos]=cali_sing
        cali_sing_se_df.loc[i, sing_isos]=cali_sing_se
        
        
        
        ############Theoretical error    
        
        #Sample R
        neff=((CPC_df.loc[i, isotopes]*CPC_y_df.loc[i, isotopes])
              / (CPC_df.loc[i, isotopes]+CPC_y_df.loc[i, isotopes]))
        
        
        interp_blank_cpc=(CPC_df.loc[blk_r[0], isotopes]*(1-Dtb)
                          +CPC_df.loc[blk_r[1], isotopes]*Dtb)
        interp_blank_cpc_y=(CPC_y_df.loc[blk_r[0], isotopes]*(1-Dtb)
                          +CPC_y_df.loc[blk_r[1], isotopes]*Dtb)
        
        neffbc=(((CPC_df.loc[i, isotopes]-interp_blank_cpc)
                 *(CPC_y_df.loc[i, isotopes]-interp_blank_cpc_y))
              / ((CPC_df.loc[i, isotopes]-interp_blank_cpc)
                       +(CPC_y_df.loc[i, isotopes]-interp_blank_cpc_y)))
        
        neff_rsd=neff**-0.5
        neffbc_rsd=neffbc**-0.5
        
        theo_R_rsd=(neff_rsd**2+flick**2)**0.5
        theo_Rbc_rsd=(neffbc_rsd**2+flick**2)**0.5
        theo_R_rse=theo_R_rsd/c4/numrepeats**0.5
        theo_Rbc_rse=theo_Rbc_rsd/c4/numrepeats**0.5
        
        
        
        #Brkt 1 R    
        neff=((CPC_df.loc[brkt_r[0], isotopes]*CPC_y_df.loc[brkt_r[0], isotopes])
              / (CPC_df.loc[brkt_r[0], isotopes]+CPC_y_df.loc[brkt_r[0], isotopes]))
           
        interp_blank_cpc=(CPC_df.loc[blk_r[0], isotopes]*(1-Dts1b)
                          +CPC_df.loc[blk_r[1], isotopes]*Dts1b)
        interp_blank_cpc_y=(CPC_y_df.loc[blk_r[0], isotopes]*(1-Dts1b)
                          +CPC_y_df.loc[blk_r[1], isotopes]*Dts1b)    
        
        neffbc=(((CPC_df.loc[brkt_r[0], isotopes]-interp_blank_cpc)
                 *(CPC_y_df.loc[brkt_r[0], isotopes]-interp_blank_cpc_y))
              / ((CPC_df.loc[brkt_r[0], isotopes]-interp_blank_cpc)
                       +(CPC_y_df.loc[brkt_r[0], isotopes]-interp_blank_cpc_y)))
            
        neff_rsd_s1=neff**-0.5
        neffbc_rsd_s1=neffbc**-0.5
        
        theo_R_rsd_s1=(neff_rsd**2+flick**2)**0.5
        theo_Rbc_rsd_s1=(neffbc_rsd**2+flick**2)**0.5
        
        
        
        
        
        
        
        #Brkt 2 R   
        neff=((CPC_df.loc[brkt_r[1], isotopes]*CPC_y_df.loc[brkt_r[1], isotopes])
              / (CPC_df.loc[brkt_r[1], isotopes]+CPC_y_df.loc[brkt_r[1], isotopes]))
            
        interp_blank_cpc=(CPC_df.loc[blk_r[0], isotopes]*(1-Dts2b)
                          +CPC_df.loc[blk_r[1], isotopes]*Dts2b)
        interp_blank_cpc_y=(CPC_y_df.loc[blk_r[0], isotopes]*(1-Dts2b)
                          +CPC_y_df.loc[blk_r[1], isotopes]*Dts2b)
           
        neffbc=(((CPC_df.loc[brkt_r[1], isotopes]-interp_blank_cpc)
                 *(CPC_y_df.loc[brkt_r[1], isotopes]-interp_blank_cpc_y))
              / ((CPC_df.loc[brkt_r[1], isotopes]-interp_blank_cpc)
                       +(CPC_y_df.loc[brkt_r[1], isotopes]-interp_blank_cpc_y)))   
        
        neff_rsd_s2=neff**-0.5
        neffbc_rsd_s2=neffbc**-0.5
        
        theo_R_rsd_s2=(neff_rsd**2+flick**2)**0.5
        theo_Rbc_rsd_s2=(neffbc_rsd**2+flick**2)**0.5
          
        
        theo_B_rsd=(theo_R_rsd**2
                    +(Dts*theo_R_rsd_s2)**2
                    +((Dts-1)*theo_R_rsd_s1)**2)**0.5
        
        theo_Bbc_rsd=(theo_Rbc_rsd**2
                    +(Dts*theo_Rbc_rsd_s2)**2
                    +((Dts-1)*theo_Rbc_rsd_s1)**2)**0.5
        
        theo_B_rse=theo_B_rsd/c4/numrepeats**0.5
        theo_Bbc_rse=theo_Bbc_rsd/c4/numrepeats**0.5
        
    
        theo_R_rse_df.loc[i, sing_isos]=theo_R_rse[sing_isos]
        theo_Rbc_rse_df.loc[i, sing_isos]=theo_Rbc_rse[sing_isos]
        theo_B_rse_df.loc[i, sing_isos]=theo_B_rse[sing_isos]
        theo_Bbc_rse_df.loc[i, sing_isos]=theo_Bbc_rse[sing_isos]
        
        
        
        
        
        
        
        
    
#calibration (cali curve)   
if calistyle=='Calibration curve':
    #make a df of known standard values
    stnd_array=np.empty((0, len(curve_isos)))  
    stnd_df=Run_df.loc[calindx]
    for c in calindx:
        s_array=np.array(stnd_dict[Run_df.loc[c, 'Sample Name']]).T
        stnd_array=np.append(stnd_array, s_array, axis=0)    
    stnd_df[curve_isos]=stnd_array
    
    
    #Remove bracketing standards that exhibit different PA
    
    for iso in PA_bracket_bad_index.keys():
        idx=np.intersect1d(stnd_df.index.values, PA_bracket_bad_index[iso])
        if len(idx)>0:
            stnd_df.loc[idx, iso]=np.nan
    
    
    #make dataframes containing information from the calibration curve fit
    #including: x values, y values, r_sq, fit parameters
    caliy=stnd_df.copy()
    
    params_df=pd.DataFrame(np.full((len(brkt_smpl_df)*3+5,
                                    brkt_smpl_df.shape[1]),np.nan), 
                           columns=[brkt_smpl_df.columns])
    
    
    
    caliy=['Calibrant_y_'+str(x) for x in np.arange(len(stnd_df))+1]
    calix=['Calibrant_x_'+str(x)  for x in np.arange(len(stnd_df))+1]
    weightx=['Weight_x_'+str(x)  for x in np.arange(len(stnd_df))+1]
    paramnames=['r_sq', 'beta0', 'beta0_1se' , 'beta1', 'beta1_1se']
        
    #collect the fit params and variables in one df
    params_df=params_df.reindex(caliy+calix+weightx+paramnames)   
    params_df.loc[caliy, stnd_df.columns]=np.array(stnd_df)
    params_df.loc[calix, stnd_df.columns]=np.array(
        brkt_smpl_df.loc[calindx, stnd_df.columns])
    params_df.loc[weightx, Run_df.columns]=np.array(Run_df.loc[calindx])
    
    brkt_cali_df=brkt_smpl_df.loc[calindx]
    
    nanarray=np.full((len(calindx),len(curve_isos)),np.nan)
    fitted_df=pd.DataFrame(nanarray, columns=curve_isos)
    
    #perform the cali curve
    for i, iso in enumerate(curve_isos):
       #get the bracketed values of the calibration standards
        brktiso_arr=np.array(brkt_smpl_df.loc[calindx, iso])
        #and their SEs
        brktiso_se_arr=np.array(brkt_smpl_se_df.loc[calindx, iso], 
                                dtype=np.float64)
        
        #assign the true values to an array
        stndiso_arr=np.array(stnd_df[iso])
        
        #determine weights based on SE
        w=1/brktiso_se_arr**2
        
        #Reshape and add intercept to bracketed values
        X=brktiso_arr
        Xwint=np.empty(shape=(len(X), 2), dtype=np.float64)
        Xwint[:,0]=1
        Xwint[:, 1]=X
        
        
        #reshape true values
        Y=stndiso_arr.reshape(-1, 1)
        
        #put the weights into the df for storage
        params_df.loc[weightx, iso]=w
        
        #boolean array indicating what standards are missing
        missindx=~pd.isna(Y).flatten()
        #Remove any NaN's from the two variables
        Xwint=Xwint[missindx]
        w=w[missindx]
        
        Y=Y[missindx]
        
        
        #Perform weighted least squares
        mdl = sm.WLS(Y, Xwint, weights=w)
        res_wls = mdl.fit()
        
        #get R-squared of WLS
        r_sq = res_wls.rsquared
        #get parameters and their SEs of WLS (0 = intercept, 1 = slope)
        params=res_wls.params 
        params_se=res_wls.bse 
        
  
        #put the fit params into the df for storage
        params_df.loc[paramnames, iso]=[
            r_sq, params[0], params_se[0], params[1], params_se[1]]
        
        
        fitted_df.loc[missindx, iso]=res_wls.fittedvalues
        
        #Apply regression to samples.
        cali_curv_df[iso]=brkt_smpl_df[iso]*params[1]+params[0]
        #propagate uncertainty
        cali_curv_se_df[iso]=(((brkt_smpl_se_df[iso]/brkt_smpl_df[iso])**2 
            + (params_se[1]/params[1])**2)*cali_curv_df[iso]**2
                              +params_se[0]**2)**0.5
        
      
    #User remove data points from the calibration curves    
    decali=pickfig_cross(stnd_df, brkt_cali_df, curve_isos, 
                         title='Remove outliers', fitted=fitted_df)
    
    #If any data points were clicked, perform the calibration again
    if any(np.array([True for k in decali.keys() if decali[k].size>0])):
                       
       #perform the cali curve
       for i, iso in enumerate(curve_isos):
           
           stnd_df.loc[decali[iso], iso]=np.nan
           
           
          #get the bracketed values of the calibration standards
           brktiso_arr=np.array(brkt_smpl_df.loc[calindx, iso])
           #and their SEs
           brktiso_se_arr=np.array(brkt_smpl_se_df.loc[calindx, iso], 
                                   dtype=np.float64)
           
           #assign the true values to an array
           stndiso_arr=np.array(stnd_df[iso])
           
           #determine weights based on SE
           w=1/brktiso_se_arr**2
           
           #Reshape and add intercept to bracketed values
           X=brktiso_arr
           Xwint=np.empty(shape=(len(X), 2), dtype=np.float64)
           Xwint[:,0]=1
           Xwint[:, 1]=X
           
           
           #reshape true values
           Y=stndiso_arr.reshape(-1, 1)
           
           #put the weights into the df for storage
           params_df.loc[weightx, iso]=w
           
           #boolean array indicating what standards are missing
           missindx=~pd.isna(Y).flatten()
           #Remove any NaN's from the two variables and weights
           Xwint=Xwint[missindx]
           w=w[missindx]          
           Y=Y[missindx]
           
           
           #Perform weighted least squares
           mdl = sm.WLS(Y, Xwint, weights=w)
           res_wls = mdl.fit()
           
           #get R-squared of WLS
           r_sq = res_wls.rsquared
           #get parameters and their SEs of WLS (0 = intercept, 1 = slope)
           params=res_wls.params 
           params_se=res_wls.bse 
           
     
           #put the fit params into the df for storage
           params_df.loc[paramnames, iso]=[
               r_sq, params[0], params_se[0], params[1], params_se[1]]
           
           
           fitted_df.loc[missindx, iso]=res_wls.fittedvalues
           
           #Apply regression to samples.
           cali_curv_df[iso]=brkt_smpl_df[iso]*params[1]+params[0]
           #propagate uncertainty
           cali_curv_se_df[iso]=(((brkt_smpl_se_df[iso]/brkt_smpl_df[iso])**2 
               + (params_se[1]/params[1])**2)*cali_curv_df[iso]**2
                                 +params_se[0]**2)**0.5 
           
           
           
           

    
#calculate the LoD using each blank (Blank equivalent concentration)
#blank CPS + 3*blankCPS_1sd as a fraction of the bracketing standard CPS
beclist=[]       
for blk in blkrows:
       
    blankcps=CPSmean_df.loc[blk, isotopes]
    
    
    #find closest bracketing standard(s)
    #Make an array where the first row is the run positions of the closest 
    #bracketing standards
    #The second row is the absolute distance between the sample and the 
    #bracketing standard given in row 1
    brktorder=np.vstack((brktrows, np.abs(brktrows-blk)))
    #The third row is the distance between the sample and standard with the
    #sign maintained to help determine whether they are 'bracketed'
    brktorder=np.vstack((brktorder, brktrows-blk))
    #order the columns w.r.t the absolute distance
    brktorder = brktorder[:, np.argsort(brktorder[1,:], axis=0)]
    #If sample is before or after all stnds, use just one closest stnd
    if np.all(brktrows-blk>=0) or np.all(brktrows-blk<=0) or any(brktrows-blk==0):
        brkt_r=np.array([brktorder[0, 0],brktorder[0, 0]])
    #Otherwise use the two closest (braketing standards)
    #If the first stnd is before the sample in the run find one after
    elif brktorder[2, 0]<0:
        #get the next nearest stnd that is of opposite sign direction away
        brk2=brktorder[0, np.where(brktorder[2, 1:]>0)[0][0]+1]          
        brkt_r=np.array([brktorder[0, 0], brk2])
    #otherwise find a stnd before the sample
    else:
        brk2=brktorder[0, np.where(brktorder[2, 1:]<0)[0][0]+1]          
        brkt_r=np.array([brk2,brktorder[0, 0]])
    
    
    #Assign fractional distance between bracketing standards
    if brkt_r[0]==brkt_r[1]:
        Dts=0
    else:
        Dts=(Run_df.loc[blk, 'Elapse']-Run_df.loc[brkt_r[0], 'Elapse'])/(
            Run_df.loc[brkt_r[1], 'Elapse']-Run_df.loc[brkt_r[0], 'Elapse'])    
    

    #determine the interpolated standard value
    s1=blkcorr_df.loc[brkt_r[0], isotopes]
    s2=blkcorr_df.loc[brkt_r[1], isotopes]
    s_brkt=s2*Dts+s1*(1-Dts)  
    
    #blank equivalent concentration
    bec=(blankcps[contains1d(isotopes, sing_isos)]/s_brkt[contains1d(isotopes, sing_isos)]
             *np.squeeze(cali_array))
    
    beclist.append(bec)
    
    
#Calculate the LoD    
becarray=np.array(beclist, dtype=float)
LoDlist=[]
for col in becarray.T:
    outs=outsbool(col)
    outs=np.isnan(col) | outs
    LoDlist.append(col[np.where(~outs)].mean()+3*col[np.where(~outs)].std())

LoD_sing=np.array(LoDlist)        



#Calculate LoD relative to bracketing standard(s)
LoDstack=LoD_sing.copy()
for brkt in unique(Run_df.loc[brktrows, 'Sample Name']):
    brkt_pcntLoD=LoD_sing/np.array(stnd_dict[brkt]).flatten()*100
    LoDstack=np.vstack((LoDstack, brkt_pcntLoD))

LoDnames='mean LoD'
LoDnames=[[LoDnames]+['% of '+name] for name in unique(Run_df.loc[brktrows, 
                                                           'Sample Name'])][0]  
    
#make the LoD dataframe
LoD_df=pd.DataFrame()
LoD_df['Type']=LoDnames

nanarray=np.full((len(LoDstack),len(isotopes)),np.nan)
LoD_df[isotopes]=nanarray
LoD_df[sing_isos]=LoDstack    



    

#make the covariance dataframe
cov_run_df=pd.concat([Run_df, cov_df], axis=1)   

#Expand the replicates so that can be viewable in an excel file (one cell per
# rep)
reps_expand_df=Run_df.copy()
#cycle through elements
for col in repCPS_all_df.columns[5:]:
    #convert element column of reps into matrix of reps and samples
    elarray=np.array(list(repCPS_all_df[col]))    
    #create new column names for the replicate columns
    colnames=[m+'_rep'+str(n) for m,n in zip([col]*5,np.arange(numrepeats)+1)]
    #build into dataframe
    eldf=pd.DataFrame(elarray, columns=colnames)
    reps_expand_df=pd.concat([reps_expand_df, eldf], axis=1)   
    

    



#############Long-term precision#############

#User choose which standards to get long-term precision data for
stndnamearray=np.array(stndval_names)
stndbool=np.array([])
while stndbool.size<1:
    stndbool=fancycheckbox(
        stndnamearray, title=("Include long-term precision data?"))
stndlistchoice=stndnamearray[stndbool]


#Get the name of the bracketing standard
commonbrkt=Run_df.loc[brktrows, 'Sample Name'].value_counts().index[0]
brktname=stnd_dict[commonbrkt].columns[0]


#get the archive data from chosen stnds that uses the same brkt stnd 
cs_all_df=archive_df.loc[(contains1d(archive_df['Sample Name'], stndlistchoice))
                         & (archive_df['BrktStnd']==brktname)] 
#Compile the long-term data from the archive.
ltp_df=pd.DataFrame()

#Need to cycle through elements and standards to remove outliers
for iso in sing_isos:  
    iso_df=cs_all_df.loc[cs_all_df['Isotope gas']==iso]
    for cs in stndlistchoice:
                
        cs_df=iso_df.loc[iso_df['Sample Name'].str.contains(cs, case=False)]                                  
        cs_sing=cs_df['Cali_single']
        cs_curv=cs_df['Cali_curve']
        
        if len(cs_sing)<2:
            continue
        
        #Remove outliers
        sing_outs=outsbool(np.array(cs_sing))
        sing_std=cs_sing[~sing_outs].std()*2
        sing_m=cs_sing[~sing_outs].mean()
        sing_rsd=sing_std/sing_m*100
        sing_n=sum(~np.isnan(cs_sing[~sing_outs]))
        
        curv_std=np.nan
        curv_m=np.nan
        curv_rsd=np.nan
        curv_n=sum(~np.isnan(cs_curv))
        if curv_n>2:            
            curv_outs=outsbool(np.array(cs_curv))
            curv_std=cs_curv[~curv_outs].std()*2
            curv_m=cs_curv[~curv_outs].mean()
            curv_rsd=curv_std/curv_m*100
            curv_n=sum(~np.isnan(cs_curv[~curv_outs]))
        
        #Add in the expected values from the stnd_vals.csv
        expect=calivals_df.loc[iso, cs]
            
        #Within-run data
        
        #Find the stnd in the run
        sing_run=cali_sing_df.loc[contains1d(Run_df['Sample Name'], 
                                             cs), iso].values
        sing_run_m=sing_run.mean()
        sing_run_1se=cali_sing_se_df.loc[contains1d(Run_df['Sample Name'], 
                                             cs), iso].values
        sing_run_2se_m=sing_run_1se.mean()*2
        sing_run_std=np.nan
        if len(sing_run)>2:
            outs=outsbool(sing_run)
            sing_run_std=sing_run[~outs].std()*2
            sing_run_m=sing_run[~outs].mean()
            sing_run_2se_m=sing_run_1se[~outs].mean()
        
        
        if calistyle=='Calibration curve':
            curv_run=cali_curv_df.loc[contains1d(Run_df['Sample Name'], 
                                                 cs), iso].values
            curv_run_m=sing_run.mean()
            curv_run_1se=cali_curv_se_df.loc[contains1d(Run_df['Sample Name'], 
                                                 cs), iso].values
            curv_run_2se_m=curv_run_1se.mean()*2
            curv_run_std=np.nan
            if sum(~np.isnan(curv_run))>2:
                outs=outsbool(curv_run)
                curv_run_std=curv_run[~outs].std()*2
                curv_run_m=curv_run[~outs].mean()
                curv_run_2se_m=curv_run_1se[~outs].mean()*2
        else:
            curv_run_m=np.nan
            curv_run_2se_m=np.nan
            curv_run_std=np.nan
            
        
        
        
        #Put all the data together
        cols=['Stnd', 'Isotope gas', 'units', 'Expected', 'Archive S-P mean', 
                  'Archive S-P 2sd', 'Archive S-P %2rsd', 'Archive S-P n',
                  'Run S-P mean', 'Run S-P 2se (mean)', 'Run S-P 2sd',                
                  'Archive curve mean', 'Archive curve 2sd' , 
                  'Archive curve %2rsd', 'Archive curve n', 
                  'Run curve mean', 'Run curve 2se (mean)', 'Run curve 2sd',]   
        var_list=[cs, iso, cs_df['units'].iloc[0], expect, sing_m, sing_std, 
                  sing_rsd, sing_n, 
                  sing_run_m, sing_run_2se_m, sing_run_std,
                  curv_m, curv_std, curv_rsd,curv_n, 
                  curv_run_m, curv_run_2se_m, curv_run_std]
        
               
        temp_dict=dict(zip(cols, var_list))    
                
        ltp_df=pd.concat([ltp_df, pd.DataFrame(temp_dict, index=[0])])      
    

ltp_df=ltp_df.reset_index(drop=True)






#make units for the headings of the excel output
unit_dict={}
for iso in sing_isos:    
    unit_dict[iso]=iso+' ('+calivals_df.loc[iso, 'Units']+')'



############# Export data ###############
   
savepath=folder_select+'/Pygilent_out/'
isExist = os.path.exists(savepath)

if not isExist:
    os.makedirs(savepath)
    
savename=textinputbox()
#add a timestamp to the filename to reduce risk of accidental data overwrite
tstamp=str(round(time.time()))


#Write short output 
with pd.ExcelWriter(savepath+savename +'_short_'+ tstamp +'.xlsx') as writer:
    reps_expand_df.to_excel(writer, sheet_name='Reps')
    CPSmean_df.to_excel(writer, sheet_name='CPS')
    CPSstd_df.to_excel(writer, sheet_name='CPS_1sd')    

    if calistyle=='Calibration curve':
        #change column names to include units
        cali_curv_df_wunits=cali_curv_df.rename(unit_dict, axis=1)
        cali_curv_se_df_wunits=cali_curv_se_df.rename(unit_dict, axis=1)
        #export
        cali_curv_df_wunits.to_excel(writer, sheet_name='Cali')
        cali_curv_se_df_wunits.to_excel(writer, sheet_name='Cali_1se')
    else:
        #change column names to include units
        cali_sing_df_wunits=cali_sing_df.rename(unit_dict, axis=1)
        cali_sing_se_df_wunits=cali_sing_se_df.rename(unit_dict, axis=1)
        #export
        cali_sing_df_wunits.to_excel(writer, sheet_name='Cali')
        cali_sing_se_df_wunits.to_excel(writer, sheet_name='Cali_1se')
        
#Write long output      
with pd.ExcelWriter(savepath+savename +'_full_'+ tstamp +'.xlsx') as writer:
    reps_expand_df.to_excel(writer, sheet_name='Reps')
    CPSmean_df.to_excel(writer, sheet_name='CPS')
    CPSstd_df.to_excel(writer, sheet_name='CPS 1sd')
    PA_df.to_excel(writer, sheet_name='PA')
    cov_run_df.to_excel(writer, sheet_name='Covar')  
    ratio_smpl_df.to_excel(writer, sheet_name='R')  
    ratio_smpl_se_df.to_excel(writer, sheet_name='R 1se')  
    brkt_smpl_df.to_excel(writer, sheet_name='Bracket')  
    brkt_smpl_se_df.to_excel(writer, sheet_name='Bracket 1se')  
    
    #change column names to include units
    cali_sing_df_wunits=cali_sing_df.rename(unit_dict, axis=1)
    cali_sing_se_df_wunits=cali_sing_se_df.rename(unit_dict, axis=1)
    LoD_df_wunits=LoD_df.rename(unit_dict, axis=1)
    #export
    cali_sing_df_wunits.to_excel(writer, sheet_name='S-P cali')
    cali_sing_se_df_wunits.to_excel(writer, sheet_name='S-P cali 1se')
    
    if calistyle=='Calibration curve':
        #change column names to include units
        cali_curv_df_wunits=cali_curv_df.rename(unit_dict, axis=1)
        cali_curv_se_df_wunits=cali_curv_se_df.rename(unit_dict, axis=1)
        #export
        cali_curv_df_wunits.to_excel(writer, sheet_name='Curve cali')
        cali_curv_se_df_wunits.to_excel(writer, sheet_name='Curve cali 1se')
        params_df.to_excel(writer, sheet_name='Curve params')
    LoD_df.to_excel(writer, sheet_name='LoD')
    ltp_df.to_excel(writer, sheet_name='Long-term precision')
    
    theo_R_rse_df.to_excel(writer, sheet_name='theo R rse')
    theo_Rbc_rse_df.to_excel(writer, sheet_name='theo Rbc rse')
    theo_B_rse_df.to_excel(writer, sheet_name='theo B rse')
    theo_Bbc_rse_df.to_excel(writer, sheet_name='theo Bbc rse')
    
            







################## Format (melt) data for archiving#############


repCPS_all_df['Type']=Run_df['Type']
repCPS_all_df['Runorder']=np.arange(len(Run_df))+1
Run_df['Runorder']=np.arange(len(Run_df))+1


#Melt all the data into a single dataframe
idcols=Run_df.columns

Melt_df=repCPS_all_df.melt(id_vars=idcols, value_vars=isotopes, var_name='Isotope gas', 
                            value_name='CPS reps')
Melt_df[['Isotope gas', 'CPS mean']]=CPSmean_df.melt(
    value_vars=isotopes, var_name='Isotope gas', value_name='CPS mean')
Melt_df[['Isotope gas', 'CPS SD']]=CPSstd_df.melt(
    value_vars=isotopes, var_name='Isotope gas', value_name='CPS SD')
Melt_df[['Isotope gas', 'Ratio']]=ratio_smpl_df.melt(
    value_vars=isotopes, var_name='Isotope gas', value_name='Ratio')
Melt_df[['Isotope gas', 'Ratio se']]=ratio_smpl_se_df.melt(
    value_vars=isotopes, var_name='Isotope gas', value_name='Ratio se')
Melt_df[['Isotope gas', 'Brkted']]=brkt_smpl_df.melt(
    value_vars=isotopes, var_name='Isotope gas', value_name='Brkted')
Melt_df[['Isotope gas', 'Brkted se']]=brkt_smpl_se_df.melt(
    value_vars=isotopes, var_name='Isotope gas', value_name='Brkted se')
Melt_df[['Isotope gas', 'Cali_single']]=cali_sing_df.melt(
    value_vars=isotopes, var_name='Isotope gas', value_name='Cali_single')
Melt_df[['Isotope gas', 'Cali_single_se']]=cali_sing_se_df.melt(
    value_vars=isotopes, var_name='Isotope gas', value_name='Cali_single_se')
Melt_df[['Isotope gas', 'PA']]=PA_df.melt(
    value_vars=isotopes, var_name='Isotope gas', value_name='PA')

Melt_df['BrktStnd']=brktname


#create a dict of integration times and gas modes 
#so they can be added to the final data
gasmode_dict=dict(zip(isotopes, Gasmodes))  
for iso in isotopes:
    Melt_df.loc[Melt_df['Isotope gas']==iso,'LoD']=float(
        LoD_df.loc[0,iso])
    Melt_df.loc[Melt_df['Isotope gas']==iso,'Gas mode']=gasmode_dict[iso]
    Melt_df.loc[Melt_df['Isotope gas']==iso,'intTime']=inttime_dict[iso]

for k in ratioels.keys():
    Melt_df.loc[Melt_df['Gas mode']==k,'Ratio iso']=ratioels[k]

for iso in calivals_df.index:
    Melt_df.loc[Melt_df['Isotope gas']==iso,'units'
                   ]=calivals_df.loc[iso, 'Units']
    


#Included number of reps (N)
for i in np.array(Melt_df.index):
    Melt_df.loc[i, 'N']=len(Melt_df.loc[i, 'CPS reps'])


if calistyle=='Calibration curve':
    Melt_df[['Isotope gas', 'Cali_curve']]=cali_curv_df.melt(
        value_vars=isotopes, var_name='Isotope gas', value_name='Cali_curve')
    Melt_df[['Isotope gas', 'Cali_curve_se']]=cali_curv_se_df.melt(
        value_vars=isotopes, var_name='Isotope gas', value_name='Cali_curve_se')     
    for iso in isotopes:
        Melt_df.loc[Melt_df['Isotope gas']==iso,'r_sq']=float(
            params_df.loc['r_sq', iso])
        Melt_df.loc[Melt_df['Isotope gas']==iso,'beta0']=float(
            params_df.loc['beta0', iso])
        Melt_df.loc[Melt_df['Isotope gas']==iso,'beta0_se']=float(
            params_df.loc['beta0_1se', iso])
        Melt_df.loc[Melt_df['Isotope gas']==iso,'beta1']=float(
            params_df.loc['beta1', iso])
        Melt_df.loc[Melt_df['Isotope gas']==iso,'beta1_se']=float(
            params_df.loc['beta1_1se', iso])











###################Figures###########

answer = tk.messagebox.askyesno(title=None, message='Make figures?')

if answer:
    
    figlist=np.array(['Blanks CPS'] + list(stndval_names))
    figlistchoice=figlist[fancycheckbox(figlist, 
                                        title=("Select figures to draw"))]
    
    figpath=savepath+'/figures'
    isExist = os.path.exists(figpath)
    
    if not isExist:
        os.makedirs(figpath)
    
    
    for f in figlistchoice:    
        if f == 'Blanks CPS':
            df1=archive_df.loc[contains1d(archive_df['Type'], 'blank')]
            df2=Melt_df[contains1d(Melt_df['Type'], 'blank')]
            blankfigsaver(df1, df2, isotopes)
        else:
            df1=archive_df.loc[contains1d(archive_df['Sample Name'], str(f))]
            df2=Melt_df[contains1d(Melt_df['Sample Name'], str(f))]
            expected=calivals_df[f]  
                
            stdfigsaver(df1, df2, f, sing_isos, expected)        
    




    
#Is the run already present in the archive data? 
#If yes, ask whether the user wants to replace the existing data. 
#If no, the data is not saved
if any(archive_df['Run Name']==Melt_df['Run Name'][0]):
    answer = tk.messagebox.askyesno(title=None, 
                                    message='Overwrite data in archive?')
    if answer:
        archive_df=archive_df.loc[archive_df['Run Name']!=Melt_df['Run Name'][0]]
        archive_df=pd.concat([archive_df, Melt_df], ignore_index=True)
        archive_df.to_csv(archivepath)
else:
    archive_df=pd.concat([archive_df, Melt_df], ignore_index=True)
    archive_df.to_csv(archivepath)
    
  



#Finished message box
tk.messagebox.showinfo("", "Processing complete")




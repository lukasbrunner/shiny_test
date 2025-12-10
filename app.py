from shiny import render, ui
from shiny.express import input

import numpy as np
import matplotlib.pyplot as plt
import cartopy.crs as ccrs

from io_functions import load_data  # ultimately replace this by something simpler
from core_functions import aggregate_members, mask_domain, cut_region, get_representative_member
from mapplot_functions import plot_map_base
from boxplot_functions import plot_box_base

ui.panel_title("Shiny test suit for ETCCDI - LE paper")

@render.text()
def text():
    return "Source code: https://github.com/lukasbrunner/shiny_test"

ui.input_select(  
    "index",  
    "Select an index below:", 
    {"txx": "TXx", 
     "tx90p": "TX90p", 
     "rx1day": "Rx1day"
     },  
) 

ui.input_select(  
    "aggregation",  
    "Select an aggregation:", 
    {"mean": "Mean", 
     "median": "Median", 
     "max": "Maximum",
     "min": "Minimum",
     "std": "Standard deviation",
     "cv": "Coefficient of Determination"
     },  
) 

ui.input_slider(
    "lon_range", 
    "Select longitude range", min=-180, max=360, 
    value=[-180, 180],
    )  

ui.input_slider(
    "lat_range", 
    "Select latitude range", min=-90, max=90, 
    value=[-90, 90],
    ) 

ui.input_checkbox(
    "mask_ocean", 
    "Apply ocean mask", 
    False,
    )  

ui.input_switch(
    "mask_land", 
    "Apply land mask", 
    False,
    )  


@render.plot(alt="A map")  
def plot():
    da = load_data(input.index())
    tmp = aggregate_members(da, input.aggregation())  # defaults to member mean
    tmp = cut_region(tmp, lat_bounds=input.lat_range(), lon_bounds=input.lon_range())
    if input.mask_ocean():
        tmp = mask_domain(tmp)
    if input.mask_land():
        tmp = mask_domain(tmp, 'land')
    fig, _, _ = plot_map_base(tmp)

    return fig
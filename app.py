from shiny import render, reactive
from shiny.express import input, ui

import io
import numpy as np
import matplotlib.pyplot as plt
import cartopy.crs as ccrs

from io_functions import load_data  # ultimately replace this by something simpler
from core_functions import aggregate_members, mask_domain, cut_region, get_representative_member
from mapplot_functions import plot_map_base
from boxplot_functions import plot_box_base
from utils import index_acronym_map

ui.panel_title("Shiny test suit for ETCCDI - LE paper")

# Add a bit of inner horizontal spacing for card contents
ui.tags.style('''
.bslib-card {
    padding-left: 1rem;
    padding-right: 1rem;
    padding-top: 0.5rem;
}
''')

ui.input_switch("advanced", "Advanced options", False) 

with ui.layout_column_wrap(width=.5):
    with ui.card():
        ui.input_select(  
            "index",  
            "Extreme index:", 
            index_acronym_map,
            # {"txx": "TXx", 
            # "tx90p": "TX90p", 
            # "rx1day": "Rx1day"
            # },  
        ) 
        ui.input_select(  
            "aggregation",  
            "Member aggregation:", 
            {"mean": "Mean", 
            "median": "Median", 
            "max": "Maximum",
            "min": "Minimum",
            "std": "Standard deviation",
            "cv": "Coefficient of Determination"
            },  
        ) 

        ui.input_switch(
            "mask_ocean", 
            "Mask ocean", 
            False,
        ) 
    with ui.card():

        ui.input_slider(
            "lon_range", 
            "Longitude range", min=-180, max=360, 
            value=[-180, 180],
            )  

        ui.input_slider(
            "lat_range", 
            "Latitude range", min=-90, max=90, 
            value=[-90, 90],
            ) 
        
# nr_members = 50
# with ui.panel_conditional("input.advanced"):
#     # if input.advanced():
#     with ui.layout_column_wrap(width=1):
#         with ui.card():
#             ui.input_slider(
#             "nr_members", 
#             "Number of members", min=1, max=50, 
#             value=nr_members,
#             )
#         nr_members = input.nr_members()


with ui.sidebar():  
    ui.HTML("<b>Data and Methods</b>")
    ui.HTML("Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat, sed diam voluptua. At vero eos et accusam et justo duo dolores et ea rebum. Stet clita kasd gubergren, no sea takimata sanctus est Lorem ipsum dolor sit amet. Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat, sed diam voluptua. At vero eos et accusam et justo duo dolores et ea rebum. Stet clita kasd gubergren, no sea takimata sanctus est Lorem ipsum dolor sit amet.")




@render.download(filename="file.nc")
def download2():
    """
    Another way to implement a file download is by yielding bytes; either all at
    once, like in this case, or by yielding multiple times. When using this
    approach, you should pass a filename argument to @render.download, which
    determines what the browser will name the downloaded file.
    """

    da = load_data(input.index())
    tmp = aggregate_members(da, input.aggregation())  # defaults to member mean
    tmp = cut_region(tmp, lat_bounds=input.lat_range(), lon_bounds=input.lon_range())
    if input.mask_ocean():
        tmp = mask_domain(tmp)
    with io.BytesIO() as buf:
        tmp.to_netcdf(buf)
        yield buf.getvalue()



@render.plot(alt="A map")  
def plot():
    da = load_data(input.index())
    tmp = aggregate_members(da, input.aggregation())  # defaults to member mean
    tmp = cut_region(tmp, lat_bounds=input.lat_range(), lon_bounds=input.lon_range())
    if input.mask_ocean():
        tmp = mask_domain(tmp)
    fig, _, _ = plot_map_base(tmp)
    return fig

def url_git():
    url = "https://github.com/lukasbrunner/shiny_test"
    return ui.tags.a("GitHub", href=url, target='_blank')

def url_by():
    url = "https://creativecommons.org/licenses/by/4.0/"
    return ui.tags.a("CC BY", href=url, target='_blank')

@render.ui
def text(): 
    return ui.div(
        url_by(), 
        " Lukas Brunner; Source code on ", 
        url_git()
        )

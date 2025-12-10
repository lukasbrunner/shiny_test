import os
import numpy as np
import xarray as xr
from natsort import natsorted
from glob import glob
from datetime import datetime, timedelta

from utils import index_unit_map, index_acronym_map, index_longname_map

time_coder = xr.coders.CFDatetimeCoder(use_cftime=True)


startyear = 1995
endyear = 2014
scenario = 'historical'
base_path = 'none'
temp_path = 'data'


def aggregations(index):
    if index in ['cdd', 'cwd', 'csdi', 'wsdi', 'gsl', 'prcptot', 'r10mm', 'r20mm', 'r95p', 'r99p', 'sdii', 'wsdi']:
        return 'none'
    elif index in ['dtr', 'tn10p', 'tn90p', 'tx10p', 'tx90p']:
        return 'mean'
    elif index in ['fd', 'id', 'su', 'tr']:
        return 'sum'
    elif index in ['rx1day', 'rx5day', 'tnx', 'txx']:
        return 'max'
    elif index in ['tnn', 'txn']:
        return 'min'


def aggregate_period(da, index):
    aggregation = aggregations(index)
    if aggregation == 'none':
        da = da.rename({'time': 'year'})
    elif aggregation == 'mean':  # redundant, could just calculate period mean
        da = da.groupby('time.year').mean()  
    elif aggregation == 'sum':
        da = da.groupby('time.year').sum()
    elif aggregation == 'max':
        da = da.groupby('time.year').max()
    elif aggregation == 'min':
        da = da.groupby('time.year').min()
    return da.mean('year') 


def load_data(index, startyear=startyear, endyear=endyear, overwrite=False):
    print(f'Load {index=}')
    fn_save = f'{index}_{startyear}-{endyear}.nc'
    if os.path.isfile(os.path.join(temp_path, fn_save)) and not overwrite:
        da = xr.open_dataset(os.path.join(temp_path, fn_save))[f'{index}']
        return da.copy()  # DEBUG: kernel keeps dying, does this help?
        
    files = natsorted(glob(os.path.join(base_path, index, scenario, '*.nc')))
    da_list = []
    for fn in files:
        member = os.path.basename(fn).split('_')[4]
        da = xr.open_dataset(fn, decode_timedelta=False, decode_times=time_coder)[f'{index}ETCCDI']
        
        # if np.any(np.isnan(da)):
        #     print(f'nan found in {index=}, {member=}')
        if da['time.month'][0].item() == 2:
            if index in ['tx90p', 'tx10p', 'tn90p', 'tn10p']:
                da = da.assign_coords(time=da['time'] - timedelta(days=31))  # fix time shift
                # print(f'Fixed time shift for {index}')
            else:
                raise ValueError('File does not start in January')
                
        da = aggregate_period(da.sel(time=slice(str(startyear), str(endyear))), index)
        da = da.expand_dims({'member': [member]})
        da_list.append(da)
    
    da = xr.concat(da_list, dim='member') 
    da.attrs = dict(
        units = index_unit_map[index],
        long_name = index_acronym_map[index],
        description = index_longname_map[index],
    )
    da.to_dataset(name=index).to_netcdf(os.path.join(temp_path, fn_save))
    return da

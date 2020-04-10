#!/bin/env python3

import os
import sys

import ecdc_csv.ecdc_csv_update as ecdc_csv
import jhu_gis.jhu_gis_update as jhu_gis
import worldometer.worldometer_update as worldometer
import gdrive_api as gdrive


def call_module_func(func):
    base_path = os.path.abspath(os.getcwd())

    try:
        func_path = sys.modules[func.__module__].__file__
        module_path = os.path.dirname(func_path)
    except:
        return None

    os.chdir(module_path)
    result = func()

    os.chdir(base_path)
    return result


print('Updating data files')
print('--------------------')

call_module_func(worldometer.main)
call_module_func(ecdc_csv.main)
call_module_func(jhu_gis.main)

print('\nPushing updates to Google Drive')
print('--------------------------------')

gdrive.main()

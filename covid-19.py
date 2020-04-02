#!/bin/env python3

import os
import sys

import ecdc_csv.ecdc_csv_update as ecdc_csv


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


call_module_func(ecdc_csv.main)

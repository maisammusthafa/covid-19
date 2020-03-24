#!/bin/env python3

import pandas
from arcgis.gis import GIS
from arcgis.features import FeatureLayer
from datetime import datetime

layer_global = FeatureLayer('https://services1.arcgis.com/0MSEUqKaxRlEPj5g/arcgis/rest/services/ncov_cases/FeatureServer/2')
query_global = layer_global.query(where='1=1', out_fields='Country_Region, Confirmed, Deaths, Recovered, Active')
df_global = query_global.sdf.drop(columns=['OBJECTID', 'SHAPE']).sort_values(by=['Country_Region'])

today = datetime.today().strftime('%Y-%m-%d')
categories = ['Confirmed', 'Deaths', 'Recovered', 'Active']

def write_to_excel(file_name, data_frame, single_sheet=False):
    with pandas.ExcelWriter(file_name, engine='xlsxwriter') as writer:
        if single_sheet:
            data_frame.to_excel(writer, sheet_name=today, index=False)
        else:
            for category in categories:
                data_frame[category].to_excel(writer, sheet_name=category, index=False)

        for sheet in writer.sheets.values():
            sheet.set_column('A:A', 28)
            sheet.set_column('B:Z', 10)
            sheet.freeze_panes(1, 1)

    writer.save()

df = {}
df_new = {}

for category in categories:
    df[category] = pandas.read_excel('data/jhu_gis_total.xlsx', sheet_name=category).drop(columns=[today], errors='ignore')
    df_new[category] = df_global[['Country_Region', category]].rename(columns={category: today})

    df[category] = pandas.merge(df[category], df_new[category], on='Country_Region', how='outer', validate='one_to_one')
    df[category] = df[category].sort_values(by=['Country_Region'])
    # df[category] = df[category].reset_index()
    # df[category] = df[category].set_index('Country_Region').T.rename_axis('Date').reset_index()

write_to_excel('data/jhu_gis_total.xlsx', df)

for category in categories:
    df[category] = df[category].set_index('Country_Region').diff(axis=1).reset_index()

write_to_excel('data/jhu_gis_diff.xlsx', df)

write_to_excel('data/daily_totals/{0}_jhu_gis_total.xlsx'.format(today), df_global, single_sheet=True)

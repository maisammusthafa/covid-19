#!/bin/env python3

import pandas
import numpy as np
from datetime import date, timedelta
from subprocess import call

return_code = call(['node', '--unhandled-rejections=strict', 'worldometer-api/index.js'])

if (return_code != 0):
    exit()

df_main = pandas.read_json('source_data.json')

column_desc = {
    'Country': 'Country',
    'TotalCases': 'Total Cases',
    'NewCases': 'New Cases',
    'TotalDeaths': 'Total Deaths',
    'NewDeaths': 'New Deaths',
    'TotalRecovered': 'Total Recovered',
    'ActiveCases': 'Active Cases',
    'Serious_Critical': 'Serious Critical',
    'TotCases_1M_Pop': 'Total Cases / 1M Pop',
    'Deaths/1M pop': 'Deaths / 1M Pop',
    '1stcase': 'First Case',
}

column_names = [name for name, desc in column_desc.items()]

today = date.today().strftime('%Y-%m-%d')
yesterday = (date.today() - timedelta(days=1)).strftime('%Y-%m-%d')

days = ['today', 'yesterday']
dfs = {}

for index, day in enumerate(days):
    dfs[day] = pandas.DataFrame(df_main['table'][0][index])
    dfs[day] = dfs[day][column_names].replace(r'^\s*$', np.nan, regex=True)
    dfs[day]['1stcase'] = '2020 ' + dfs[day]['1stcase']
    dfs[day]['1stcase'] = pandas.to_datetime(dfs[day]['1stcase'], format='%Y %b %d').dt.strftime('%Y-%m-%d')

    for column in column_names[1:-1]:
        dfs[day][column] = dfs[day][column].replace('\+|-|,', '', regex=True).astype(float)

    world_index = dfs[day].Country == 'Total:'
    dfs[day].loc[(world_index, 'Country')] = 'World'
    dfs[day] = dfs[day].sort_values(by=['Country'])

    dfs[day]['tmp'] = range(1, len(dfs[day]) + 1)
    dfs[day].loc[world_index, 'tmp'] = 0
    dfs[day] = dfs[day].sort_values(by=['tmp']).drop('tmp', axis=1)

    dfs[day].rename(columns=column_desc, inplace=True)

file_name = 'data/{}_worldometer_covid.xlsx'.format(yesterday)

with pandas.ExcelWriter(file_name, engine='xlsxwriter') as writer:
    dfs['yesterday'].to_excel(writer, sheet_name=yesterday, index=False)
    dfs['today'].to_excel(writer, sheet_name='{} (7 pm)'.format(today), index=False)

    for sheet in writer.sheets.values():
        sheet.set_column('A:A', 22)
        sheet.set_column('B:E', 12)
        sheet.set_column('F:H', 15)
        sheet.set_column('I:J', 19)
        sheet.set_column('K:K', 12)
        sheet.freeze_panes(1, 1)

writer.save()

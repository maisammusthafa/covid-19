#!/bin/env python3

import pandas
import numpy as np
from datetime import date, timedelta
from subprocess import call

dfs = {}


def download_source_data():
    return_code = call(['node', '--unhandled-rejections=strict', 'worldometer-api/index.js'])

    if (return_code != 0):
        exit()


def process_data():
    column_desc = {
        'Country': 'Country',
        'TotalCases': 'Total Cases',
        'NewCases': 'New Cases',
        'TotalDeaths': 'Total Deaths',
        'NewDeaths': 'New Deaths',
        'TotalRecovered': 'Total Recovered',
        'ActiveCases': 'Active Cases',
        'Serious_Critical': 'Serious, Critical',
        'TotCases_1M_Pop': 'Total Cases / 1M Pop',
        'Deaths/1M pop': 'Deaths / 1M Pop',
    }

    column_names = [name for name, desc in column_desc.items()]
    days = ['today', 'yesterday']

    df_main = pandas.read_json('source_data.json')

    for index, day in enumerate(days):
        dfs[day] = pandas.DataFrame(df_main['table'][0][index])
        dfs[day] = dfs[day][column_names].replace(r'^\s*$', np.nan, regex=True)

        for column in column_names[1:]:
            dfs[day][column] = dfs[day][column].replace('\+|-|,', '', regex=True).astype(float)

        world_index = dfs[day].Country == 'Total:'
        dfs[day].loc[(world_index, 'Country')] = 'World'
        dfs[day] = dfs[day].sort_values(by=['Country'])

        dfs[day]['tmp'] = range(1, len(dfs[day]) + 1)
        dfs[day].loc[world_index, 'tmp'] = 0
        dfs[day] = dfs[day].sort_values(by=['tmp']).drop('tmp', axis=1)

        dfs[day].rename(columns=column_desc, inplace=True)


def write_to_excel():
    today = date.today().strftime('%Y-%m-%d')
    yesterday = (date.today() - timedelta(days=1)).strftime('%Y-%m-%d')
    file_name = 'data/{}_worldometer_covid.xlsx'.format(yesterday)

    with pandas.ExcelWriter(file_name, engine='xlsxwriter') as writer:
        dfs['yesterday'].to_excel(writer, sheet_name=yesterday, index=False)
        dfs['today'].to_excel(writer, sheet_name='{} (7 pm)'.format(today), index=False)

        for sheet in writer.sheets.values():
            sheet.set_column('A:A', 22)
            sheet.set_column('B:E', 12)
            sheet.set_column('F:H', 15)
            sheet.set_column('I:J', 19)
            sheet.freeze_panes(1, 1)

    writer.save()


def main():
    print('Worldometer: Retrieving source data')
    download_source_data()

    print('Worldometer: Processing and writing to excel')
    process_data()
    write_to_excel()


if __name__ == '__main__':
    main()

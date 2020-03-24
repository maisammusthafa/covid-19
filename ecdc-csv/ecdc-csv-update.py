#!/bin/env python3

import pandas
import urllib.request

source_data_url = 'https://covid.ourworldindata.org/data/ecdc/full_data.csv'
urllib.request.urlretrieve(source_data_url, 'source_data.csv')

df_source = pandas.read_csv('source_data.csv')

categories = {
        'new_cases': 'Confirmed',
        'new_deaths': 'Deaths',
        'total_cases': 'Confirmed',
        'total_deaths': 'Deaths'
        }

dfs = {}

for category in categories:
    dfs[category] = df_source[['date', 'location', category]]
    dfs[category] = dfs[category].pivot(index='date', columns='location', values=category)
    dfs[category] = pandas.DataFrame(dfs[category].to_records()).rename(columns={'date': 'Date'})

def write_to_excel(file_name, data_categories):
    with pandas.ExcelWriter(file_name, engine='xlsxwriter') as writer:
        for category in data_categories:
            dfs[category].to_excel(writer, sheet_name=categories[category], index=False)

        for sheet in writer.sheets.values():
            sheet.set_column('A:A', 12)
            sheet.freeze_panes(1, 1)

write_to_excel('data/ecdc_csv_total.xlsx', ['total_cases', 'total_deaths'])
write_to_excel('data/ecdc_csv_diff.xlsx', ['new_cases', 'new_deaths'])

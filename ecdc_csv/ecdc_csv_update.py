#!/bin/env python3

import pandas
import urllib.request

dfs = {}


def download_source_data():
    source_data_url = 'https://opendata.ecdc.europa.eu/covid19/casedistribution/csv'
    urllib.request.urlretrieve(source_data_url, 'source_data.csv')


def process_data():
    df_source = pandas.read_csv('source_data.csv', encoding='utf-8')

    for category in ['cases', 'deaths']:
        dfs[category] = df_source[['dateRep', 'countriesAndTerritories', category]]
        dfs[category] = dfs[category].pivot(index='dateRep', columns='countriesAndTerritories', values=category)

        dfs[category] = pandas.DataFrame(dfs[category].to_records()).rename(columns={'dateRep': 'Date'})
        dfs[category]['Date'] = pandas.to_datetime(dfs[category]['Date'], format='%d/%m/%Y').dt.strftime('%Y-%m-%d')
        dfs[category] = dfs[category].sort_values(by=['Date'])

        dfs[category].columns = dfs[category].columns.str.replace('_', ' ')

    dfs['new_cases'] = dfs['cases']
    dfs['new_deaths'] = dfs['deaths']
    dfs['total_cases'] = dfs['cases'].set_index('Date').cumsum().reset_index()
    dfs['total_deaths'] = dfs['deaths'].set_index('Date').cumsum().reset_index()


def write_to_excel(file_name, data_categories):
    with pandas.ExcelWriter(file_name, engine='xlsxwriter') as writer:
        for category, name in data_categories.items():
            dfs[category].to_excel(writer, sheet_name=name, index=False)

        for sheet in writer.sheets.values():
            sheet.set_column('A:A', 12)
            sheet.freeze_panes(1, 1)


def main():
    download_source_data()
    process_data()

    write_to_excel('data/ecdc_csv_total.xlsx', {'total_cases': 'Confirmed', 'total_deaths': 'Deaths'})
    write_to_excel('data/ecdc_csv_diff.xlsx', {'new_cases': 'Confirmed', 'new_deaths': 'Deaths'})


if __name__ == '__main__':
    main()

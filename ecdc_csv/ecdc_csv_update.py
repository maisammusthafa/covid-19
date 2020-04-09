#!/bin/env python3

import pandas as pd
import urllib.request


def download_source_data():
    source_data_url = 'https://opendata.ecdc.europa.eu/covid19/casedistribution/csv'
    urllib.request.urlretrieve(source_data_url, 'source_data.csv')


def process_data():
    df_source = pd.read_csv('source_data.csv', encoding='utf-8')
    dfs = {}

    for category in ['cases', 'deaths']:
        df = df_source[['dateRep', 'countriesAndTerritories', category]]
        df = df.pivot(index='dateRep', columns='countriesAndTerritories', values=category)

        df = pd.DataFrame(df.to_records()).rename(columns={'dateRep': 'Date'})
        df['Date'] = pd.to_datetime(df['Date'], format='%d/%m/%Y')
        df = df.sort_values(by=['Date']).set_index('Date')

        df.columns = df.columns.str.replace('_', ' ')
        dfs[category] = df

    dfs['new_cases'] = dfs.pop('cases')
    dfs['new_deaths'] = dfs.pop('deaths')
    dfs['total_cases'] = dfs['new_cases'].cumsum()
    dfs['total_deaths'] = dfs['new_deaths'].cumsum()

    return dfs


def write_to_excel(file_name, data_categories, dfs):
    with pd.ExcelWriter(file_name, engine='xlsxwriter') as writer:
        for category, name in data_categories.items():
            df = dfs[category]
            df.index = df.index.date
            df.reset_index(inplace=True)
            df.to_excel(writer, sheet_name=name, index=False)

        for sheet in writer.sheets.values():
            sheet.set_column('A:A', 12)
            sheet.freeze_panes(1, 1)

    writer.save()


def main():
    print('ECDC-CSV: Retrieving source data')
    download_source_data()

    print('ECDC-CSV: Processing and writing to excel')
    dfs = process_data()

    total = {
        'file_name': 'data/ecdc_csv_total.xlsx',
        'types': {'total_cases': 'Confirmed', 'total_deaths': 'Deaths'}
    }

    diff = {
        'file_name': 'data/ecdc_csv_diff.xlsx',
        'types': {'new_cases': 'Confirmed', 'new_deaths': 'Deaths'}
    }

    write_to_excel(total['file_name'], total['types'], dfs)
    write_to_excel(diff['file_name'], diff['types'], dfs)


if __name__ == '__main__':
    main()

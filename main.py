import pandas as pd
import tkinter as tk
import matplot as mp
import json
import matplotlib as mpl
import matplotlib.pyplot as plt
import pycountry_convert as cc
import user_agents as ua

entryList = []
df = pd.DataFrame(columns=[
                  'ts', 'doc_UUID', 'visitor_country', 'browser', 'visitor_uuid', 'readtime'])
df['readtime'] = df['readtime'].astype(int)


def load_data():
    for i in range(0, len(entryList)):
        if "env_doc_id" not in entryList[i]:
            entryList[i]["env_doc_id"] = "null"
        if "event_readtime" not in entryList[i]:
            entryList[i]["event_readtime"] = 0
        df.loc[i] = [entryList[i]["ts"], entryList[i]
                     ["env_doc_id"], entryList[i]['visitor_country'], entryList[i]['visitor_useragent'], entryList[i]['visitor_uuid'], entryList[i]['event_readtime']]


def read_from_file():
    try:
        filename = input('Please enter filename:')
        with open(filename) as file:
            for entryObject in file:
                entryDict = json.loads(entryObject)
                entryList.append(entryDict)
    except FileNotFoundError:
        print('File not found')
        read_from_file()
    finally:
        load_data()


def plot_data_country():
    try:
        doc_id = input('Please enter doc_UUID:')
        df.loc[df['doc_UUID'] == doc_id].groupby(
            'visitor_country').size().plot(kind='bar', title='Countries that visited ' + doc_id)
        plt.show()
    except KeyError:
        print('doc_UUID not found. Please try again.')
    except IndexError:
        print('doc_UUID not found. Please try again.')


def plot_data_continent():
    continentdict = {
        'EU': 'Europe',
        'AF': 'Africa',
        'AN': 'Antarctica',
        'AS': 'Asia',
        'NA': 'North America',
        'OC': 'Oceania',
        'SA': 'South America'
    }
    try:
        doc_id = input('Please enter doc_UUID:')
        copy_df = df.loc[df['doc_UUID'] == doc_id]
        for i in range(0, len(copy_df)):
            copy_df.iloc[i, 2] = continentdict.get(cc.country_alpha2_to_continent_code(
                copy_df.iloc[i, 2]))
        copy_df.groupby('visitor_country').size().plot(
            kind='bar', title='Continents that visited ' + doc_id)
        plt.show()
    except KeyError:
        print('doc_UUID not found. Please try again.')
    except IndexError:
        print('doc_UUID not found. Please try again.')


def plot_data_useragent():
    df['browser'].value_counts().plot(kind='bar', title='Popular Useragents')
    plt.show()


def plot_data_browser():
    copy_df = df
    for i in range(0, len(copy_df)):
        copy_df.iloc[i, 3] = ua.parse(copy_df.iloc[i, 3]).browser.family
    copy_df.groupby('browser').size().plot(
        kind='bar', title='Popular Browsers')
    plt.show()


def determine_readership():


def main():
    read_from_file()
    print(df.head())
    plot_data_useragent()


main()

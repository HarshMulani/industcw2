import pandas as pd
import tkinter as tk
import tkinter.ttk as ttk
import matplot as mp
import json
import matplotlib as mpl
import matplotlib.pyplot as plt
import pycountry_convert as cc
import user_agents as ua
import numpy
from collections import OrderedDict


def load_data(entryList):
    df = pd.DataFrame(columns=[
        'ts', 'doc_UUID', 'visitor_country', 'browser', 'visitor_uuid', 'readtime'])
    df['readtime'] = df['readtime'].astype(int)
    for i in range(0, len(entryList)):
        if "env_doc_id" not in entryList[i]:
            entryList[i]["env_doc_id"] = "null"
        if "event_readtime" not in entryList[i]:
            entryList[i]["event_readtime"] = -1
        df.loc[i] = [entryList[i]["ts"], entryList[i]
                     ["env_doc_id"], entryList[i]['visitor_country'], entryList[i]['visitor_useragent'], entryList[i]['visitor_uuid'], entryList[i]['event_readtime']]
    return df

def read_from_file():
    entryList = []
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
        df = load_data(entryList)
        return df


def plot_data_country(df):
    try:
        doc_id = input('Please enter doc_UUID:')
        df.loc[df['doc_UUID'] == doc_id].groupby(
            'visitor_country').size().plot(kind='bar', title='Countries that visited ' + doc_id)
        plt.show()
    except KeyError:
        print('doc_UUID not found. Please try again.')
    except IndexError:
        print('doc_UUID not found. Please try again.')


def plot_data_continent(df):
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


def plot_data_useragent(df):
    df['browser'].value_counts().plot(kind='bar', title='Popular Useragents')
    plt.show()


def plot_data_browser(df):
    copy_df = df
    for i in range(0, len(copy_df)):
        copy_df.iloc[i, 3] = ua.parse(copy_df.iloc[i, 3]).browser.family
    copy_df.groupby('browser').size().plot(
        kind='bar', title='Popular Browsers')
    plt.show()

# Determines the readership profiles for users, constructing an object of the user-id and their reading time, prints out the top ten readers
def determine_readership(df):
    resultdict = {}
    templist = []
    for i in range(0, len(df)):
        if df.iloc[i, 5] > -1:
            temp_entry = (df.iloc[i, 4], df.iloc[i, 5])
            templist.append(temp_entry)
    for each in templist:
        if each[0] in resultdict:
            resultdict[each[0]] += each[1]
        resultdict.update([(each[0], each[1])])

    # Separetes the keys and values into their own respective lists
    keys = list(resultdict.keys())
    values = list(resultdict.values())
    # Create a sorted index of the values from the previously gatehred values
    sorted_index = numpy.argsort(values)
    # Using dictionary comprehension we assign the keys by the sorted index values
    sorted_dict = {keys[x]: values[x] for x in sorted_index}

    # Convert the dictionary of all values into a list of items, grab the first ten and then reconvert back into a dictionary using list slicing
    size = len(list(sorted_dict))
    top_ten = dict(list(sorted_dict.items())[size - 11: size - 1])
    # Using the OrderedDict package, we reverse the top ten to properly rank them
    top_ten_reverse = OrderedDict(reversed(list(top_ten.items())))

    # Returns the entire sorted dictionary, and the top ten ranked from highest to lowers.
    return OrderedDict(reversed(list(sorted_dict.items()))), top_ten_reverse

# Retrieves through the determine_readership function the readership values and then processes them accordingly.


def get_readership(file_data):
    ordered_readership, top_ten = determine_readership(file_data)
    if top_ten:
        print("Top ten readers by read time:")
        for value in top_ten:
            print(value, top_ten[value])

# Provides an object


def get_doc_reader_list(doc, df):
    # Initialise user list
    user_list = {

    }
    # Iterate through all entries of the data frame -> This is designed for extensibility, the userlist could be indexed for each document on a system that was
    # connected to a database, allowing for more efficient calls to this in the future
    for i in range(0, len(df)):
        # Check if the document id is the same as the provided one
        if df.iloc[i, 1] == doc:
            # Check if the user is already in the user list, if so incremene the key by one
            if df.iloc[i, 4] in user_list:
                user_list[df.iloc[i, 4]] = user_list[df.iloc[i, 4]] + 1
            # Increment the amount of reads for this document by one
            else:
                user_list[df.iloc[i, 4]] = 1
    return user_list


def get_readers_doc_list(reader_list, df):
    return_dict = {

    }
    for i in range(0, len(df)):
        # Check if the document id is the same as the provided one
        if df.iloc[i, 4] in reader_list:
            # Check if the user is already in the user list, if so incremene the key by one
            if df.iloc[i, 1] in return_dict:
                return_dict[df.iloc[i, 1]] = return_dict[df.iloc[i, 1]] + 1

            # Increment the amount of reads for this document by one
            else:
                return_dict[df.iloc[i, 1]] = 1
    print(return_dict)
    return return_dict

def get_also_likes(df, doc):
    # call the reader_list and user_list funcitons to compile the also_liked list.
    users = get_doc_reader_list(doc, df)
    also_liked = get_readers_doc_list(users, df)

     # Separetes the keys and values into their own respective lists
    keys = list(also_liked.keys())
    values = list(also_liked.values())
    # Create a sorted index of the values from the previously gatehred values
    sorted_index = numpy.argsort(values)
    # Using dictionary comprehension we assign the keys by the sorted index values
    sorted_dict = {keys[x]: values[x] for x in sorted_index}
    # Convert the dictionary of all values into a list of items, grab the first ten and then reconvert back into a dictionary using list slicing
    size = len(list(sorted_dict))

    # If the size is less than ten, then it means that we need to simply plot what values we do have
    if size > 10:
        top_ten = dict(list(sorted_dict.items())[size - 11: size - 1])
    else:
        top_ten = dict(list(sorted_dict.items()))
    # Using the OrderedDict package, we reverse the top ten to properly rank them
    # We then plot the values derived and return the list
    top_ten_reverse = OrderedDict(reversed(list(top_ten.items())))
    plot_also_likes(top_ten_reverse, doc)
    return top_ten_reverse

def plot_also_likes(also_liked, doc):
    
    # Separate the keys and values in order to get them in a list format to use in the plot
    keys = also_liked.keys()
    values = also_liked.values()
    # Plot the keys and values, with a width of .08
    plt.bar(keys, values, width=.08)
    # Set the name for x and the y values to show they are the documents and the read count, additionally gives the name
    plt.xlabel("Documents")
    plt.ylabel("Read count")
    plt.title("Documents also liked for " + doc)
    # Finally show the plot
    plt.show()

def main():
    file_data = read_from_file()
    print(file_data.head())
    # get_readership(file_data)
    increment = 0
    # for i in range(0, len(file_data)):
    #     liked = get_also_likes(file_data, file_data.iloc[i, 1])
    #     if liked > 1:
    #         increment = increment + 1
    # print(increment)
    get_also_likes(file_data, "140224132818-2a89379e80cb7340d8504ad002fab76d")


# Set the default state of the program to check what is being requested and run default operations accordingly
if __name__ == "__main__":
    # Run the main function
    main()

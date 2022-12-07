import os
import tkinter.filedialog as fd
import tkinter.scrolledtext as st
import tkinter.ttk as ttk
import tkinter as tk
import pandas as pd
# import tkinter as tk
# import tkinter.ttk as ttk
import matplot as mp
import json
import matplotlib as mpl
import matplotlib.pyplot as plt
import pycountry_convert as cc
import user_agents as ua
import numpy
import argparse
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


def read_from_file(file):
    entryList = []
    try:
        filename = file
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


def plot_data_country(df, udid):
    try:
        doc_id = udid
        df.loc[df['doc_UUID'] == doc_id].groupby(
            'visitor_country').size().plot(kind='bar', title='Countries that visited ' + doc_id)
        plt.show()
    except KeyError:
        print('doc_UUID not found. Please try again.')
    except IndexError:
        print('doc_UUID not found. Please try again.')


def plot_data_continent(df, udid):
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
        doc_id = udid
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


def gui():
    root_window = tk.Tk()
    root_window.title("Team 11's Issuu Data Analysis Application")
    root_window.geometry("900x400")
    root_window.maxsize(900, 400)
    root_window.minsize(900, 400)
    root_window.configure(bg="#FCF1EB")
    label1 = ttk.Label(root_window, text="Task Results", font=(
        "Calibri", 12), background="#FCF1EB")
    label1.grid(row=0, column=2, padx=10, pady=5)

    result_text_area = st.ScrolledText(
        root_window, width=30, height=20)
    result_text_area.grid(column=2, pady=5, padx=5, rowspan=10)
    result_text_area.configure(state="disabled")

    label_dataset = ttk.Label(root_window, text="Dataset: ", font=(
        "Calibri", 12), background="#FCF1EB")
    label_dataset.grid(row=1, column=3, padx=10, pady=5)

    global dataset_input
    dataset_input = ttk.Entry(root_window, width=55)
    dataset_input.grid(row=1, column=4, padx=5, pady=5, columnspan=2)
    dataset_input.configure(state="readonly")

    file_button = ttk.Button(
        root_window, text="Select JSON", command=open_file)
    file_button.grid(row=1, column=6, padx=5, pady=5)

    label_document = ttk.Label(root_window, text="Document UUID: ", font=(
        "Calibri", 12), background="#FCF1EB")
    label_document.grid(row=2, column=3, padx=5, pady=5)
    document_input = ttk.Entry(root_window, width=55)
    document_input.grid(row=2, column=4, padx=5, pady=5, columnspan=1)
    document_input.configure(state="normal")

    label_user = ttk.Label(root_window, text="User UUID: ", font=(
        "Calibri", 12), background="#FCF1EB")
    label_user.grid(row=3, column=3, padx=5, pady=5)
    user_input = ttk.Entry(root_window, width=55)
    user_input.grid(row=3, column=4, padx=5, pady=5, columnspan=1)
    user_input.configure(state="normal")

    btn_2a = ttk.Button(root_window, text="2a. Views by Country")
    btn_2a.grid(row=4, column=3, padx=5, pady=5)

    btn_2b = ttk.Button(root_window, text="2b. Views by Continent")
    btn_2b.grid(row=5, column=3, padx=5, pady=5)

    btn_3a = ttk.Button(root_window, text="3a. Useragent Data")
    btn_3a.grid(row=4, column=4, padx=5, pady=5)

    btn_3b = ttk.Button(root_window, text="3b. Views by Browser")
    btn_3b.grid(row=5, column=4, padx=5, pady=5)

    btn_4 = ttk.Button(root_window, text="4. View Frequent Readers")
    btn_4.grid(row=6, column=4, padx=5, pady=5)

    btn_5 = ttk.Button(root_window, text="5. Also-Likes")
    btn_5.grid(row=4, column=6, padx=5, pady=5)

    btn_5 = ttk.Button(root_window, text="6. Also-Likes Graph")
    btn_5.grid(row=5, column=6, padx=5, pady=5)

    root_window.mainloop()


def open_file():
    file_name = fd.askopenfile(mode='r',
                               initialdir="/", title="Please select JSON File.", filetypes=(("JSON", "*.json"), ("JSON", "*.json")))
    if file_name:
        filepath = os.path.abspath(file_name.name)
        dataset_input.configure(state="normal")
        dataset_input.insert(0, filepath)
        return filepath


def main():
    # Initialise the parser using the argparser library to simplify the calling
    parser = argparse.ArgumentParser()
    # Set the arguments that can be accepted
    parser.add_argument("-u", "--uuid", help="Unique User ID")
    parser.add_argument("-d", "--udid", help="Unique Doc ID")
    parser.add_argument("-t", "--task", help="Task Number")
    parser.add_argument("-f", "--file", help="File Name")

    # Get the arguments from the command line
    args = parser.parse_args()

    # If no file is provided throw and error and return, otherwise read the provided file
    if args.file == None:
        print("You must specify a file that will provide the sample data in question to use this program. Add a -f, or --file flag and the path to denote this")
        return
    else:
        file_data = read_from_file(args.file)

    # Get the task from the arguments and check which task is being called, based on the task determine if it needs another flag and then throw an issue if none is provided
    task = args.task
    if args.task == '2a':
        if args.udid:
            plot_data_country(file_data, args.udid)
        else:
            print("To execute the histogram of document views by country, please add this after the -d or -udid flag")
    elif args.task == '2b':
        if args.udid:
            plot_data_continent(file_data, args.udid)
        else:
            print("To execute the histogram of document views by continent, please add this after the -d or -udid flag")
    elif args.task == '3a':
        plot_data_browser(file_data)
    elif args.task == '3b':
        plot_data_useragent(file_data)
    elif args.task == '4':
        get_readership(file_data=file_data)
    elif args.task == '5d':
        if args.udid:
            top_ten = get_also_likes(file_data, args.udid)
            print("Top ten related docs are: ")
            for entry in top_ten:
                print(entry)
        else:
            print("A unique document id is required to run this function, please provide that after the -u tag or --udid tag")
    elif args.task == '6':
        if args.udid:
            top_ten = get_also_likes(file_data, args.udid)
            plot_also_likes(top_ten, args.udid)
        else:
            print("A unique document id is required to run this function, please provide that after the -u tag or --udid tag")
    elif args.task == '7':
        gui()
    # If no task is given let the user know what was wrong and the tasks they can implement.
    else:
        print("Please input a flag to denote task, either -t or --task followed by:")
        print("2a, 2b, 3a, 3b, 4, 5d, 6, or 7")


# Set the default state of the program to check what is being requested and run default operations accordingly
if __name__ == "__main__":
    # Run the main function
    main()

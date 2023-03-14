"""
utils has as goal to put in place a set of utils functions useful to transform relational database into graph
In utils, we can found function such as Load that allow us to load the log file
"""

import csv
import os
import time
import typing

import pandas as pd
from neo4j import GraphDatabase


class Preprocessor:
    def __init__(
        self,
        inputPath: str,
        outputPath: str,
        fileName: str,
        outputFileName: str,
        timestamp_format: str = "%Y.%m.%d %H:%M:%S",
    ) -> None:
        self.inputPath = inputPath
        self.outputPath = outputPath
        self.fileName = fileName
        self.outputFileName = outputFileName
        self.timestamp_format = timestamp_format

    def Preprocess(self) -> None:

        csvLog = pd.read_csv(
            filepath_or_buffer=os.path.realpath(self.inputPath + self.fileName),
            keep_default_na=True,
        )  # Load log from csv
        header = csvLog.columns
        csvLog.drop_duplicates(
            keep="first", inplace=True
        )  # remove duplicates from the dataset
        csvLog = csvLog.reset_index(
            drop=True
        )  # renew the index to close gaps of removed duplicates

        # Create a dict instance eg: {"event":"", "time" : ""}
        columnNewcolumn = {}
        for item in header:
            columnNewcolumn[item] = ""

        # Replace "" by the right column name
        for item in header:
            firstWord = " Choose the appropriate column name using the  Multidimentional process mining methode"
            print(f" Column : {item}")
            response = input(
                f"{firstWord} \n Choose the appropriate number \n 1 - Case \n 2 - Activity \n 3 - Timestamp , \n 4 - Actor \n 0 - default \n"
            )

            if response == "1":
                columnNewcolumn[item] = "Case"
            elif response == "2":
                columnNewcolumn[item] = "Activity"
            elif response == "3":
                columnNewcolumn[item] = "Timestamp"
            elif response == "4":
                columnNewcolumn[item] = "Actor"
            else:
                list_word = item.split(" ")
                singleWord = "_".join(list_word)
                columnNewcolumn[item] = singleWord.capitalize()
            print(len(firstWord) * "-")

        if "Timestamp" in list(columnNewcolumn.values()):

            # Rename columns with white spaces and columns that refer to time, actors and activities.
            csvLog = csvLog.rename(columns=columnNewcolumn)

            # the following loop allows to pre-process individual event records in the data
            sampleList = (
                []
            )  # create a list (of lists) for the sample data containing a list of events for each of the selected cases
            for index, row in csvLog.iterrows():
                rowList = list(row)  # add the event data to rowList
                sampleList.append(
                    rowList
                )  # add the extended, single row to the sample dataset

                # create dataframe for default timestamp formatting (YYYY-MM-DD HH:MM:SS.ms)
            header = list(csvLog)  # save the updated header data

            logSamples = pd.DataFrame(
                sampleList, columns=header
            )  # create pandas dataframe and add the samples
            logSamples["Timestamp"] = pd.to_datetime(
                logSamples["Timestamp"], format=self.timestamp_format
            )

            logSamples.fillna(0)
            # sort all events by time, add a second column if data contains events with identical timestamps to ensure canonical ordering
            logSamples["Timestamp"] = logSamples["Timestamp"].map(
                lambda x: x.strftime("%Y-%m-%dT%H:%M:%S.%f")[0:-3] + "+0100"
            )
            logSamples.sort_values(["Timestamp"], inplace=True)

            # and write dataframe to CSV file sorted by time
            if not os.path.isdir(self.outputPath):
                os.mkdir(self.outputPath)
            logSamples.to_csv(self.outputPath + self.outputFileName, index=False)
        else:
            print("Choose right dataframe, This type of table don't follow MPMM rule")

    def Load(self, filePath: str):

        eventTitle = []
        event = []
        numberEvent = 0

        with open(filePath, mode="r") as f:
            row = csv.reader(f)

            if numberEvent == 0:

                eventTitle.extend(list(row))
                numberEvent += 1
            else:

                event.append(row)

        log = pd.DataFrame(event, columns=eventTitle)

        return eventTitle, log

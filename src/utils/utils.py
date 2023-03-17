"""
utils has as goal to put in place a set of utils functions useful to transform to extract trace in to data provides by third paerson
In utils, we can found function such as Load that allow us to load the log file
"""

import csv
import os
import time
import typing

import pandas as pd
import pm4py as pm
from pm4py.objects.log.importer.xes import importer as xes_importer


class Preprocessor:
    def __init__(
        self,
        inputPath: str,
        outputPath: str,
        fileName: str,
        outputFileName: str,
        timestamp_format: str = "%Y.%m.%d %H:%M:%S",
    ) -> None:
        self.section = ""
        self.inputPath = inputPath
        self.outputPath = outputPath
        self.fileName = fileName
        self.outputFileName = outputFileName
        self.timestamp_format = timestamp_format

    def Preprocess(self) -> None:
        if self.section == "":
            self.section = input(
                "write your avatar name for enable section:  \n Avatar : "
            )
            print(60 * "-")

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
            firstWord = (
                " Choose the appropriate column name useful for trace extracting"
            )
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

            log = pd.DataFrame(
                sampleList, columns=header
            )  # create pandas dataframe and add the samples
            log["Timestamp"] = pd.to_datetime(
                log["Timestamp"], format=self.timestamp_format
            )

            log.fillna(0)
            # sort all events by time, add a second column if data contains events with identical timestamps to ensure canonical ordering
            log["Timestamp"] = log["Timestamp"].map(
                lambda x: x.strftime("%Y-%m-%dT%H:%M:%S.%f")[0:-3] + "+0100"
            )
            log.sort_values(["Timestamp"], inplace=True)

            # Sample of log for PM
            logSamples = log[["Case", "Activity", "Timestamp"]].copy()
            logSamples["Case"] = logSamples["Case"].apply(lambda _: str(_))
            logSamples["Activity"] = logSamples["Activity"].apply(lambda _: str(_))
            logSamples["Timestamp"] = pd.to_datetime(
                logSamples["Timestamp"], format="%Y-%m-%dT%H:%M:%S.%f"
            )
            logSamples.rename(
                columns={
                    "Case": "case:concept:name",
                    "Activity": "concept:name",
                    "Timestamp": "time:timestamp",
                },
                inplace=True,
            )

            # and write dataframe to CSV file sorted by time
            if not os.path.isdir(os.path.join(self.outputPath, self.section)):
                os.mkdir(os.path.join(self.outputPath, self.section))

            logSamples.to_csv(
                os.path.join(
                    os.path.join(self.outputPath, self.section), self.outputFileName
                ),
                index=False,
            )
        else:
            print(
                "Choose right dataframe, This type of table don't follow PM rule for trace extrating"
            )

    def traceScraper(self):

        # self.Preprocess()
        self.section = "essai"

        logSamples = pd.read_csv(
            os.path.realpath(
                os.path.join(
                    os.path.join(self.outputPath, self.section), self.outputFileName
                )
            )
        )
        logSamplesPm = pm.format_dataframe(
            logSamples,
            case_id="case:concept:name",
            activity_key="concept:name",
            timestamp_key="time:timestamp",
        )
        traces = []
        Case = []
        # Extract traces from event log
        log = pm.convert_to_event_log(logSamplesPm)
        for caseConceptName in range(len(log)):

            trace = ""
            for conceptName in range(len(log[caseConceptName])):
                trace = trace + log[caseConceptName][conceptName]["concept:name"] + " "
            # trace = trace.split(" ")
            # unique_chars = set(trace)
            # unique_string = " ".join(unique_chars)
            traces.append(trace.strip())
            Case.append(caseConceptName)

        pd.DataFrame({"case:concept:name": Case, "Trace": traces}).to_csv(
            os.path.join(
                os.path.join(self.outputPath, self.section),
                self.outputFileName + "Trace.csv",
            )
        )

        return logSamplesPm

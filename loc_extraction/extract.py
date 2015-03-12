#!/usr/bin/python
# -*-coding:Utf-8 -*-

import os
import sys
import time
import json
import datetime
from ast import literal_eval
from operator import itemgetter

from extract_data import extract_infos_from_pic
import useful_functions
import filters

#if __name__ == "__main__":
def test():

    print "Content-Type: text/event-stream"
    print

    with open("../data/searchedBoat.txt", "r") as file:
        searchParams = file.read().splitlines()

    boatName = searchParams[0]
    searchLoc = searchParams[1]
    searchInfos = searchParams[2]

    rawDataFile = "../data/Raw_data/" + boatName.title() + ".json"

    searchName = boatName.replace(" ", "+")

    if searchLoc == "true":
        minDate =  "2013-01-01 00:00:00"
        rawData, extractionTime, notExtractedPics = extract_infos_from_pic(searchName, minDate)

        rawData = sorted(rawData, key=itemgetter(2))
        with open(rawDataFile, "w") as file:
            json.dump(rawData, file)

#       if len(notExtractedPics) > 0:
#            print("Problem with the extraction of " + str(len(notExtractedPics)) + " pictures informations :")
#           for IDpic in notExtractedPics:
#               print("- " + IDpic)

        procData = filters.apply_filters(rawData)
        processedDataFile = "../data/" + boatName.title() + ".json"
        with open(processedDataFile, "w") as file:
            json.dump(procData, file)

        with open("../data/listBoats.txt","a") as file:
            file.write(boatName.title() + "\n")

    return 0

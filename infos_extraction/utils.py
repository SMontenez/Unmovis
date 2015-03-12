#!/usr/bin/python
# -*-coding:Utf-8 -*-

from difflib import ndiff

def dictToCsv(dictInfos, sites):
    csv = "Site;"
    for category in dictInfos.keys():
        csv += category.split("/")[0] + ";"
    csv += "\n"

    for site in sites.keys():
        csv += site.split("/")[1] + ";"
        for category in dictInfos.keys():
            value = dictInfos[category][site.split("/")[0]]
            csv += dictInfos[category][site.split("/")[0]] + ";"
        csv += "\n"

    return csv


def get_most_common(dictInfos):
    numericalInfos = ["Length", "Beam", "Draught", "GT", "Speed"]
    mostCommonDict = {}
    for category in dictInfos.keys():
        values = []
        for site in dictInfos[category].keys():
            value = dictInfos[category][site].decode("utf8")
            if value != "":
                values.append(value)
        cat = category.split("/")[0]
        if cat not in numericalInfos:
            compare_and_equals(values)
        if len(values) != 0:
            mostCommonDict[cat] = most_common(values)
        else:
            mostCommonDict[cat] = ["No value"]
    return str(mostCommonDict).replace("[u'", "['").replace(", u'", ", '")


def compare_and_equals(listValues):
    for i,value in enumerate(listValues):
        for j in range(i):
            compValue = listValues[j]
            minus = 0
            plus = 0
            for diff in ndiff(value, compValue):
                if diff[0] == "-":
                    minus += 1
                elif diff[0] == "+":
                    plus += 1
            if minus + plus < 4:
                if minus >= plus:
                    listValues[j] = value
                else:
                    listValues[i] = compValue


def most_common(listValues):
    countList = [listValues.count(i) for i in listValues]
    maxCount = max(countList)
    mostCommonValues = set([listValues[i] for i in [i for i,x in enumerate(countList) if x == maxCount]])
    return list(mostCommonValues)

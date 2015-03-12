#!/usr/bin/python
# -*-coding:Utf-8 -*-

from difflib import ndiff
from copy import deepcopy

def unify(dictInfos):
    uniDict = deepcopy(dictInfos)
    distance = ["Length", "Draught", "Beam"]

    for inf in uniDict.keys():
        info = inf.split("/")[0]
        for site in uniDict[inf].keys():
            normalizedValue = uniDict[inf][site].encode("utf8")
            if normalizedValue != "":
                if info in distance:
                    normalizedValue = normalizeDistance(normalizedValue)
                elif info == "GT":
                    normalizedValue = normalizeGT(normalizedValue)
                if normalizedValue != 0:
                    uniDict[inf][site] = normalizedValue

    return uniDict


# Distances are converted to the format "xxx m"
def normalizeDistance(distance):
    parts = distance.strip().replace(",", ".").split(" ")
    if len(parts) == 1:
        parts = distance.replace("m", " m").replace("ft", " ft").split(" ")
        if len(parts) == 1:
            print("Problem normalizing " + distance)
            return 0

    if len(parts) == 2:
        try:
            value = int(parts[0])
        except ValueError:
            try:
                value = float(parts[0])
            except ValueError:
                print("1st part not number in " + str(parts))
                return 0
        if parts[1] == "m":
            parts[0] = suppEndZero(str(round(value, 1)))
            return " ".join(parts)
        elif parts[1] == "ft":
            parts[0] = suppEndZero(str(round(value*0.3048,1)))
            parts[1] = "m"
            return " ".join(parts)
        else:
            print("Unit not known in " + str(parts))
            return 0

    else:
        return 0


def normalizeGT(GT):
    gt = GT.replace(".", "").replace(",", "")
    lon = len(gt)

    for l in range(lon, 0, -1):
        possibilities = lon + 1 - l
        for n in range(possibilities):
            try:
                normGT = int(gt[n:n+l])
                return str(normGT)
            except ValueError:
                pass

    print("Couldn't normalize Gt : " + GT)
    return 0


def suppEndZero(number):
    if number[-1] == "0":
        if number[-2] == ".":
            return number[:-2]
        else:
            return number[:-1]
    else:
        return number

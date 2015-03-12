#!/usr/bin/python
# -*-coding:Utf-8 -*-

import ast
import urllib
import useful_functions
import time

from datetime import datetime
from operator import itemgetter

def apply_filters(data):
    #print("\n----- DEDUPLICATION -----")
    newData, dedupTime = deduplicate(data)
    print "id: newNum"
    print "data: " + str(len(newData)) + "\n"
    #print("\n----- ON LAND DETECTION -----")
    onLandTime = on_land(newData)
    #print("\n----- OUTLIERS DETECTION -----")
    outliersTime = outliers(newData)
    #print("\n----- IMPOSSIBLE JOURNEYS DETECTION -----")
    impJourneysTime = impossible_journeys(newData, "passenger ship")

    #print("- Deduplication => " + str(dedupTime) + "s" )
    #print("- On-land detection => " + str(onLandTime) + "s" )
    #print("- Outliers detection => " + str(outliersTime) + "s" )
    #print("- Impossible journeys detection => " + str(impJourneysTime) + "s" )

    return newData



# Deduplicates all elements in the rawData list (same date (+- 10 hours) and same user)
def deduplicate(rawData):
    startTime = time.time()
    newData = list(rawData)

    sorted(newData, key=itemgetter(2))
    picList = list(newData)
    for i,pic1 in enumerate(picList):
        print "id: dedup"
        print "data: " + str(i) + "\n"
        for index in range(i+1, len(picList)):
            pic2 = picList[index]
            diffDate = useful_functions.diffDate(pic1[2], pic2[2])
            if pic1[1] == pic2[1] and abs(diffDate.total_seconds()) < 18000:
                newData[newData.index(pic2)][3][0] += pic1[3][0]
                for urls in pic1[3][1:]:
                    newData[newData.index(pic2)][3].append(urls)
                newData.remove(pic1)
                break

    return newData, time.time() - startTime



# Determine if a location is into a sea or an ocean, using the Geonames webservice
def in_sea_Geonames(lat, lon):
    listNumbers = [0, 0.01, 0.02, 0.03, 0.04, 0.05, 0.06, 0.07, 0.08, 0.09, 0.1,-0.01, -0.02, -0.03, -0.04, -0.05, -0.06, -0.07, -0.08, -0.09, -0.1]
    listOfPossibilities = []

    for i in listNumbers:
        for j in listNumbers:
            listOfPossibilities.append((float(lat) + i, float(lon) + j))
    print(listOfPossibilities)

    for lat, lon in listOfPossibilities:

        url = 'http://api.geonames.org/oceanJSON?lat=' + str(lat) + '&lng=' + str(lon) +'&username=projetbateau'
        result = urllib.urlopen(url).read().decode('utf-8')
        print(result)

        if 'status' in result:
            pass
        else:
            seaName = ast.literal_eval(result)['ocean']['name']
            return (True, seaName)

    return (False, '')



# Return the dict without the pictures that aren't located
# on water, and a dict containing only the ones which are
def on_land(data):
    startTime = time.time()
    listPolygones, listLines = useful_functions.create_list_polygones_lines()

    for i,pic in enumerate(data):
        print "id: onLand"
        print "data: " + str(i) + "\n"
        inSea = point_in_sea(pic[-2], listPolygones)

        if inSea == False:
            distMinFromSea = distance_min_from_sea(pic[-2], listPolygones)
            if distMinFromSea < 5 :
                pic[-1][0] = 0
            else:
                pic[-1][0] = int(distMinFromSea)

    return time.time() - startTime


# Determines if a point is in one of the polygones contained
# in the list of polygones given as parameters
def point_in_sea(location, listPolygones):
    inSea = False
    over = False
    lat = location[0]
    lon = location[1]

    for polygone in listPolygones:

        # If the polygone definition describes only 1 polygone without any hole
        if len(polygone) == 1:
            inSea = useful_functions.point_inside_polygon(lon, lat, polygone[0])
            if inSea == True:
                over = True

        # If length is more than 1, it means that the polygon contains holes
        else :
            for (j, poly) in enumerate(polygone):
                inPolygon = useful_functions.point_inside_polygon(lon, lat, poly)
                if inPolygon == True:
                    if j == 0:
                        inSea = True
                    over = True
                    break

        if over == True:
            break

    return inSea

# Return the minimum distance between the location and all the polygones
def distance_min_from_sea(location, listPolygones):
    minDist = 10000
    lat = location[0]
    lon = location[1]
    for polygone in listPolygones:
        if len(polygone) == 1:
            poly = polygone[0]
            n = len(poly)
            for i in range(n-1):
                #distFromPoly = useful_functions.distance(location, poly[i])
                if poly[i] != poly[i+1]:
                    distFromPoly = useful_functions.min_distance((lon, lat), (poly[i], poly[i+1]))
                if distFromPoly < minDist:
                    minDist = distFromPoly
        else:
            for (i, poly) in enumerate(polygone):
                n = len(poly)
                for i in range(n-1):
                    #distFromPoly = useful_functions.distance(location, poly[i])
                    if poly[i] != poly[i+1]:
                        distFromPoly = useful_functions.min_distance((lon, lat), (poly[i], poly[i+1]))
                    if distFromPoly < minDist:
                        minDist = distFromPoly
    return minDist



# For a specific picture, we determine a temporal cluster around it specified by the window tw (+- 1 week), and then we check if the pic is an outlier in this cluster
def outliers(data):
    startTime = time.time()

    tw = 7 * 24 * 3600  # time window in seconds

    for i,pic in enumerate(data):
        print "id: outlier"
        print "data: " + str(i) + "\n"
        timeCluster = []
        for otherPic in data:
            if useful_functions.diffDate(pic[2], otherPic[2]).total_seconds() < tw :
                timeCluster.append(otherPic)

        useful_functions.is_outlier(pic, timeCluster)

    return time.time() - startTime



# Delete all the impossible journeys considering the speed parameter
# (either a speed in km/h, or a string representing the type of boat)
def impossible_journeys(data, speed):
    startTime = time.time()
    if type(speed) != int :
        speed = useful_functions.get_max_speed(speed)

    picsToCheck = len(data) - 1

    for i in range(picsToCheck):
        print "id: farFetched"
        print "data: " + str(i) + "\n"
        pic1 = data[i]
        pic2 = data[i+1]

        if useful_functions.check_journey_feasibility(pic1, pic2, speed) == False:
            pic1[-1][1] += 1
            pic2[-1][1] += 1

    return time.time() - startTime


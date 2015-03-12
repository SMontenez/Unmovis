#!/usr/bin/python
# -*-coding:Utf-8 -*-

import math
import json
import trans
import math
import os

from datetime import datetime

# ------------ GENERAL FUNCTIONS -------------


# Reads a boat name from the command and transform it into a string
def read_command_line(argv):
    if len(argv) != 3:
        return "Command line has to be : python main.py 'extract/update/re-process' 'listOfBoatsFile/boatName'\n"
    else:
        command = argv[1]
        boat = argv[2]

        if command not in ["extract", "re-process", "update"]:
            return "'command' has to be 'extract', 're-process' or 'update'\n"
        elif os.path.isfile(boat) == False:
            return command, 1, boat
        else:
            return command, 2, boat

# Encode the string to convert every national character into normal character (example : 'æ' becomes 'ae')
def normalize_nat_char(string):
    if type(string) != unicode:
        string = string.decode("utf8")
    return string.encode('trans')


# Return the distance (in km) between the two locations ([lat, lon])
def distance(loc1, loc2):
    lat1 = loc1[0]*(math.pi/180)
    lon1 = loc1[1]*(math.pi/180)
    lat2 = loc2[0]*(math.pi/180)
    lon2 = loc2[1]*(math.pi/180)

    # As sometimes there can be round up issues
    a = math.sin(lat1)*math.sin(lat2) + math.cos(lat1)*math.cos(lat2)*math.cos(lon2-lon1)
    if a>1:
        a=1
    elif a<-1:
        a=-1

    a = 6371*math.acos(a)

    return abs(a)


# Return the difference (in the datetime.timedelta shape) between the two dates (in the format described by dateFormat)
def diffDate(date1, date2):
    dateFormat = "%Y-%m-%d %H:%M:%S"
    return (datetime.strptime(date1, dateFormat) - datetime.strptime(date2,  dateFormat))





# ------------  API EXTRACTION -------------

# Return whether the searched keyword has been found in the picture tags, title or description
def find_keyword(keyword, dic):
    for tag in dic['tags']['tag']:
        tagContent = normalize_nat_char(tag['_content'])
        if keyword.lower().replace(' ', '') == tagContent :
            return 'tag'
    title = normalize_nat_char(dic['title']['_content'])
    if keyword.lower() in title.lower():
        return 'title'
    else:
        return 'description'


# Find the source url of a Flickr picture when extracted from the api
def find_source(picData):
    wantedSizes = ['Medium', 'Small 320', 'Medium 640', 'Small']
    for wantedSize in wantedSizes:
        for picSize in picData:
            if picSize['label'] == wantedSize:
                return picSize['source']
    return ''





# ------------  'OUTLIERS DETECTION' -------------

# A pic is an outlier in a time cluster if it is farther from the centroid of the cluster than K times the maximum distance between ALL the other points of the cluster
def is_outlier(pic, timeCluster):

    K = 5 # application-specific constant

    nbPics = len(timeCluster)
    centerLat = 0
    centerLon = 0
    for _pic in timeCluster:
        centerLat += _pic[5][0]
        centerLon += _pic[5][1]
    center = [centerLat/nbPics, centerLon/nbPics]

    dMax = 0
    for i in range(nbPics):
        if i != timeCluster.index(pic) and i+1 < nbPics:
            loc1 = timeCluster[i][5]
            for j in range(i+1, nbPics):
                loc2 = timeCluster[j][5]
                dMax = max(dMax, distance(loc1, loc2))

    if distance(center, pic[5]) >= K*dMax:
        pic[-1][2] = 1




# ------------  'IMPOSSIBLE JOURNEYS' -------------


# Returns whether the journey described by the two pics is possible or not (considering the given speed)
def check_journey_feasibility(pic1, pic2, speed):
    journeyDuration = diffDate(pic2[2], pic1[2]).total_seconds() / 3600
    journeyDistance = distance(pic1[-2], pic2[-2])
    return (journeyDuration > journeyDistance/speed)


# Return the maximum possible speed (in km/h) given the type of boat
def get_max_speed(typeOfBoat):
    if typeOfBoat.lower() in ['passenger ship', 'passengers ship', 'cruise ship', 'container ship', 'cargo ship']:
        return 30*1.852
    elif typeOfBoat.lower() in ['war ship', 'war vessel']:
        return 40*1.852
    else:
        return 50*1.852





# ------------ 'LOCATION ON LAND' -------------

# Returns a list of polygons corresponding to all the seas, oceans and
# lakes of earth, and a list of lines corresponding to all the rivers
def create_list_polygones_lines():
    # Extraction of the oceans and seas
    with open('/home/montenez/Documents/Geodatas/ne_10m_ocean.json', 'r') as fichier:
        dicOceans = json.loads(fichier.read())
        listPolygones = dicOceans['features'][0]['geometry']['coordinates']

    # Extraction of the lakes
    """
    with open('/home/montenez/Documents/Geodatas/ne_10m_lakes.json', 'r') as fichier:
        dicLakes = json.loads(fichier.read().decode('utf-8', 'ignore'))
        for lake in dicLakes['features']:
        if lake['geometry']['type'] == 'Polygon':
                listPolygones.append(lake['geometry']['coordinates'])
            elif lake['geometry']['type'] == 'MultiPolygon':
                for poly in lake['geometry']['coordinates']:
                    #listPolygones.append(poly)
    """

    # Extraction of the rivers
    with open('/home/montenez/Documents/Geodatas/ne_10m_rivers_lake_centerlines.json', 'r') as fichier:
        dicRivers = json.loads(fichier.read().decode('utf-8', 'ignore'))

    listLines = []
    for feature in dicRivers['features']:
        if feature['geometry']['type'] == 'LineString':
            listLines.append(feature['geometry']['coordinates'])
        else:
            for subListLines in feature['geometry']['coordinates']:
                listLines.append(subListLines)

    return listPolygones, listLines


# Ray casting algorithm
def point_inside_polygon(x, y, poly):
    n = len(poly)
    inside = False
    p1x,p1y = poly[0]
    for i in range(n+1):
        p2x,p2y = poly[i%n]
        if y > min(p1y, p2y) and y <= max(p1y, p2y):
            if x <= max(p1x, p2x):
                xinters = (y-p1y)*(p2x-p1x)/(p2y-p1y)+p1x
                if p1x == p2x or x <= xinters:
                    inside = not inside
        p1x,p1y = p2x,p2y

    return inside


# Return true if the point(x,y) is on a line determined by a random number of vertices,
# which is if the point is on any segment delimited by two consecutive vertices
def point_on_line(x, y, line):
    n = len(line)
    onLine = False

    p1x,p1y = line[0]
    for i in range(n):
        p2x,p2y = line[i]
        if x <= max(p1x,p2x) and x >= min(p1x,p2x):
            if y <= max(p1y,p2y) and y >= min(p1y,p2y):
                onLine = ((x-p1x)*(p1y-p2y) == (y-p1y)*(p1x-p2x))
                if onLine == True:
                    break
                else:
                    p1x,p1y = p2x,p2y

    return onLine


# Execute the given function on points located on a circle centered on the given location
def check_around(function, location, *params):
    lat = location[0]
    lon = location[1]

    listPossibilities = []
    for i in range(0,11):
        nbToAdd = float(i)/100
        x1 = lat + nbToAdd
        x2 = lat - nbToAdd
        y1 = lon + math.sqrt(0.01 + math.pow(nbToAdd,2))
        y2 = lon - math.sqrt(0.01 + math.pow(nbToAdd,2))
        listPossibilities.append([x1, y1])
        listPossibilities.append([x2, y1])
        listPossibilities.append([x1, y2])
        listPossibilities.append([x2, y2])


    for i,possibility in enumerate(listPossibilities):
        result = function(possibility, *params)
        if result == True:
            break
    return result


class Vector(object):
    def __init__(self, point):
        (self.x, self.y) = point

    def norm(self):
        return math.sqrt(self.x**2 + self.y**2)

    def normalize(self):
        norm = self.norm()
        normed = (self.x/norm, self.y/norm)
        return Vector(normed)

    # Get the distance in kilometers with x and y being a latitude and a longitude
    def real_length(self):
        return distance((0,0), (self.y, self.x))

    def __add__(self, other):
        added = (self.x + other.x, self.y + other.y)
        return Vector(added)

    def __sub__(self, other):
        subbed = (self.x - other.x, self.y - other.y)
        return Vector(subbed)

    def __mul__(self, other):
        if type(other) == int or type(other) == float:
            product = (self.x * other, self.y * other)
            return Vector(product)
        elif type(other) == type(self):
            return self.x * other.x + self.y * other.y

    def __repr__(self):
        return "(" + str(self.x) + ", " + str(self.y) + ")"


def min_distance(point, segment):
    p1, p2 = segment
    seg_a = Vector(p1)
    seg_b = Vector(p2)
    pos = Vector(point)

    seg_v = seg_b - seg_a
    pt_v = pos - seg_a

    proj_v = pt_v * seg_v.normalize()
    if proj_v < 0:
        closest = seg_a
    elif proj_v > seg_v.norm():
        closest = seg_b
    else:
        proj_v = seg_v.normalize() * proj_v
        closest = seg_a + proj_v

    dist_v = pos - closest
    minDist = distance((pos.y, pos.x), (closest.y, closest.x))
    return minDist


# Implements the resolution found at http://doswa.com/2009/07/13/circle-segment-intersectioncollision.html
def seg_intersects_circle(p1, p2, center, radius):
    min_dist = min_distance(center, (p1, p2))
    if min_dist <= radius:
        return True
    else:
        return False

#!/usr/bin/python
# -*-coding:Utf-8 -*-

import sys
import urllib
import urllib2
import requests
import time
import os

import normalization_utils
import wikipedia_utils
import parsers
import unification
import utils


def extract_from_Wikipedia(boatName, infos):
    wikiBoatName = boatName

    infosWanted = infos.keys()
    del(infosWanted[infosWanted.index("Name")])

    # Here we try to see if the given boat name is in a list of Wikipedia
    # boat names extracted from Yago, and if so we give to the boat the name
    # found in the list that corresponds to the article name on Wikipedia
    with open("./Wiki_boats_name/boats.txt", "r") as file:
        boatsNameList = file.read().split('\n')
    for name in boatsNameList:
        if boatName.lower() in name.lower():
            wikiBoatName = name
            break

    # If the boat name hasn't been found in the list extracted from
    # YAGO, we try to see if the API call works with the raw name
    # If it doesn't we create a fake result that will allow to skip
    # the informations extraction part and return an empty result
    try:
        revisionTemplates = wikipedia_utils.ParseTemplates(wikipedia_utils.GetWikipediaArticle(wikiBoatName)["text"])
    except IndexError:
        try:
            revisionTemplates = wikipedia_utils.ParseTemplates(wikipedia_utils.GetWikipediaArticle(wikiBoatName.capitalize())["text"])
            wikiBoatName = wikiBoatName.capitalize()
        except IndexError:
            try:
                revisionTemplates = wikipedia_utils.ParseTemplates(wikipedia_utils.GetWikipediaArticle(wikiBoatName.title())["text"])
                wikiBoatName = wikiBoatName.title()
            except IndexError:
                revisionTemplates = {"templates":[[""]], "flattext":""}

    redirected = False
    # If the page result redirects to another page we try to reach this other page
    if "#REDIRECT" in revisionTemplates["flattext"]:
        redirected = True
        oldBoatName = wikiBoatName
        wikiBoatName = revisionTemplates["flattext"].split("#REDIRECT")[1].strip()
        revisionTemplates = wikipedia_utils.ParseTemplates(wikipedia_utils.GetWikipediaArticle(wikiBoatName)["text"])

    # We list the possible section names that we can find in our extraction result
    isShip = ["Infobox ship begin", "Infobox Ship begin", "Infobox ship Begin", "Infobox Ship Begin"]
    career = ["Infobox ship career", "Infobox Ship career", "Infobox Ship Career", "Infobox ship Career"]
    characteristics = ["Infobox ship characteristics", "Infobox Ship characteristics", "Infobox Ship Characteristics", "Infobox ship Characteristics"]

    # If the result actually corresponds to a ship we can begin the informations
    # extraction, if not we fill the result dict with blank fields except for the name
    if len(set(isShip) & set([elt[0] for elt in revisionTemplates["templates"]])) != 0:
        infos["Name"]["Wikipedia"] = wikiBoatName
        infoFound = False
        for elt in revisionTemplates["templates"]:
            if elt[0] in career or elt[0] in characteristics:
                infoboxInfos = normalization_utils.normalize(elt[1])
                for infoWanted in infosWanted:
                    for key, value in infoboxInfos.items():
                        key = key.title().split(" ")
                        for infoW in infoWanted.split("/"):
                            if infoW in key and value != "":
                                infos[infoWanted]["Wikipedia"] = " ".join(value.split())
                                infoFound = True
                            elif infoW in value:
                                info = " ".join(value[value.index(infoW):].split())
                                infoFound = True
                                try:
                                    beginning = info.index(":") + 1
                                except ValueError:
                                    try:
                                        beginning = info.index(" ") + 1
                                    except ValueError:
                                        infoFound = False
                                if infoFound == True:
                                    info = info[beginning:].strip()
                                    try:
                                        end = info.index(" ,")
                                        infos[infoWanted]["Wikipedia"] = info[:end].strip()
                                    except ValueError:
                                        try:
                                            end = info.index("br")
                                            infos[infoWanted]["Wikipedia"] = info[:end].strip()
                                        except ValueError:
                                            try:
                                                end = info.index(" ")
                                                infos[infoWanted]["Wikipedia"] = info[:end].strip()
                                            except ValueError:
                                                infos[infoWanted]["Wikipedia"] = info.strip()
                            if infoFound == True:
                                break
                        if infoFound == True:
                            break
                    if infoFound == False and "Wikipedia" not in infos[infoWanted]:
                        infos[infoWanted]["Wikipedia"] = ""
                    infoFound = False
    else:
        if redirected == True:
            infos["Name"]["Wikipedia"] = oldBoatName
        else:
            infos["Name"]["Wikipedia"] = wikiBoatName.title()
        infos["Name"]["Wikipedia"] += " (No page found)"
        for infoWanted in infosWanted:
            infos[infoWanted]["Wikipedia"] = ""


def extract_from_ShipSpotting(boatName, infos):
    urlListPics = "http://www.shipspotting.com/gallery/search.php?query=" + boatName
    page = urllib.urlopen(urlListPics).read()
    page = page[page.find("http://www.shipspotting.com/gallery/photo.php?lid="):]
    url = page[:page.find("\">")]
    page = urllib.urlopen(url).read()

    SSParser = parsers.ShipSpottingParser(infos)
    SSParser.feed(page)

    add_infos(SSParser.infos, infos, "ShipSpotting", boatName)

    return (boatName, infos["IMO"]["ShipSpotting"], infos["MMSI"]["ShipSpotting"])


def extract_from_MarineTraffic(boatID, infos):
    if boatID[1] != "":
        url = "http://www.marinetraffic.com/en/ais/details/ships/" + boatID[1]
    elif boatID[2] != "":
        url = "http://www.marinetraffic.com/en/ais/details/ships/" + boatID[2]

    hdr = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11', 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8', 'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3', 'Accept-Encoding': 'none', 'Accept-Language': 'en-US,en;q=0.8', 'Connection': 'keep-alive'}
    req = urllib2.Request(url, headers=hdr)
    page = urllib2.urlopen(req).read()

    MTParser = parsers.MarineTrafficParser(infos)
    MTParser.feed(page)

    add_infos(MTParser.infos, infos, "MarineTraffic", boatID[0])

    return page


def extract_from_ShippingExplorer(boatID, infos):
    loginUrl = "http://www.shippingexplorer.net/en/users/login"
    if boatID[1] != "":
        url = "http://www.shippingexplorer.net/en/vessels/search?s=" + boatID[1]
    elif boatID[2] != "":
        url = "http://www.shippingexplorer.net/en/vessels/search?s=" + boatID[2]
    else:
        url = "http://www.shippingexplorer.net/en/vessels/search?s=" + boatID[0]
    payload = {"Username":"Siboustier", "Password":"noireau"}
    with requests.Session() as s:
        s.post(loginUrl, data=payload)
        r = s.get(url)
        page = r.text

    SEParser = parsers.ShippingExplorerParser(infos)
    SEParser.feed(page)

    if SEParser.infos["Name"] == "Advanced Vessel Search":
        SEParser.infos["Name"] = ""

    add_infos(SEParser.infos, infos, "ShippingExplorer", boatID[0])

    if boatID[2] == "":
        return (boatID[0], boatID[1], infos["MMSI"]["ShippingExplorer"])
    else:
        return boatID


def extract_from_GrossTonnage(boatID, infos):
    if boatID[1] != "":
        url = "http://www.grosstonnage.com/?code=RESUL&str=" + boatID[1]
    elif boatID[2] != "":
        url = "http://www.grosstonnage.com/?code=RESUL&str=" + boatID[2]
    else:
        url = "http://www.grosstonnage.com/?code=RESUL&str=" + boatID[0]

    page = urllib.unquote(urllib.urlopen(url).read())
    page = page[page.find("A4Iwrite")+10:]
    page = page[:page.find("\");</script>")]
    page = page.replace("&nbsp", " ").replace(";", "")

    # Au cas où il y aurait plusieurs résultats pour le mot clé recherché, on
    # réduit la chaine de caractère traitée au code concernant le bateau voulu
    for elt in page.split("</tr>"):
        if boatID[0] + "</b></a>" in elt:
            page = page[0] + elt
            break

    GTParser = parsers.GrossTonnageParser(infos)
    GTParser.feed(page)

    add_infos(GTParser.infos, infos, "GrossTonnage", boatID[0])

    if boatID[1] == "":
        return (boatID[0], infos["IMO"]["GrossTonnage"], boatID[2])
    else:
        return boatID


# Add the informations extracted from the parser to the general informations
# about the boat into a specific section determined by the site name
def add_infos(parserInfos, boatInfos, siteName, boatName):
    for infoWanted in boatInfos.keys():
        try:
            if parserInfos[infoWanted] == "-" or parserInfos[infoWanted] == "N/A":
                parserInfos[infoWanted] = ""
            if parserInfos["Name"] == "":
                parserInfos["Name"] = boatName.title() + "(No page found)"
            boatInfos[infoWanted][siteName] = " ".join(parserInfos[infoWanted].split())
        except KeyError:
            if infoWanted == "Name":
                boatInfos[infoWanted][siteName] = boatName.title() + "(No page found)"
            else:
                boatInfos[infoWanted][siteName] = ""


# We extract informations from each source separately and add
# these informations to the dictionnary that recaps everything
def extract_infos(boatName, infos):
    boatID = extract_from_ShipSpotting(boatName, infos)
    boatID = extract_from_GrossTonnage(boatID, infos)
    boatID = extract_from_ShippingExplorer(boatID, infos)
    extract_from_MarineTraffic(boatID, infos)
    extract_from_Wikipedia(boatName, infos)


if __name__ == "__main__" :
    arg = sys.argv[1]
    if os.path.isfile(arg):
        with open("./" + fileName, "r") as file:
            listBoats = file.read().splitlines()
    else:
        listBoats = [arg]


    # All the informations that we want to extract from each site
    boatInfos = {"Name": {}, "IMO": {}, "MMSI": {}, "Build/Completed/Launched/Year": {}, "Owner": {}, "Flag/Registry/Country": {}, "Type": {}, "GT/Gross Tonnage": {}, "Length": {}, "Beam/Breadth/Width": {}, "Draught/Draft": {}, "Speed": {}}
    # All the sites we want to extract informations from
    sites = {"Wikipedia/Wiki":"",  "GrossTonnage/GT":"", "ShippingExplorer/SE":"", "ShipSpotting/SS":"", "MarineTraffic/MT":""}

    for i,boatName in enumerate(listBoats):
        print(boatName)
        print("Boat n°" + str(i+1) + " / " + str(len(listBoats)))
        infosBoat = {}
        for category in boatInfos.keys():
            infosBoat[category] = {}

        success = 0
        while success<3:
            try:
                extract_infos(boatName, infosBoat)
                success = 4
            except:
                print(infosBoat)
                print("\n----------  Waiting  ----------\n")
                success += 1
                time.sleep(20)

        if success == 4:
            uniInfosBoat = unification.unify(infosBoat)
            uniResult = utils.dictToCsv(uniInfosBoat, sites)
            with open("./boatsInfos/" + boatName.title() + ".csv", "w") as file:
                file.write(uniResult)

            mostCommonResult = utils.get_most_common(uniInfosBoat)
            with open("./boatsInfos/" + boatName.title() + "_simplified.json", "w") as file:
                file.write(mostCommonResult)

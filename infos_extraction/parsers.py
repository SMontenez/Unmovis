#!/usr/bin/python
# -*-coding:Utf-8 -*-

import urllib
import socket
from HTMLParser import HTMLParser

class MarineTrafficParser(HTMLParser):
    def __init__(self, infosWanted):
        HTMLParser.__init__(self)
        self.infos = {}
        self.infosWanted = infosWanted.keys()
        self.inDetails = False
        self.readName = False
        self.readTypeOfInfo = False
        self.read = False
        self.readInfo = False
        self.readInfo1 = False
        self.readInfo2 = False
        self.lastInfo = False

    def handle_starttag(self, tag, attrs):
        if tag == "h1":
            self.readName = True
        elif tag == "div" and ("class", "panel details-panel details-panel-1") in attrs:
            self.inDetails = True
        elif self.inDetails == True:
            if tag == "span":
                self.readTypeOfInfo = True
            elif tag == "b" and (self.readInfo == True or self.readInfo1 == True or self.readInfo2 == True):
                self.read = True


    def handle_endtag(self, tag):
        if tag == "h1":
            self.readName = False
        elif self.readTypeOfInfo == True and tag == "span":
            self.readTypeOfInfo = False
        elif self.read == True and tag == "b":
            self.read = False
            self.readInfo = False
            self.readInfo1 = False
            self.readInfo2 = False
        elif self.lastInfo == True and tag == "div":
            self.inDetails = False
            self.lastInfo = False

    def handle_data(self, data):
        if self.readName:
            self.infos["Name"] = data.title()
        elif self.readTypeOfInfo:
            if data.split(":")[0] == "Status":
                self.lastInfo = True
            for infoWanted in self.infosWanted:
                for infoW in infoWanted.split("/"):
                    if len(data.split("x")) == 1:
                        if infoW in data.split(":")[0]:
                            self.readInfo = True
                            self.info = infoWanted
                    else:
                        if infoW in data.split(" x ")[0]:
                            self.readInfo1 = True
                            self.info1 = infoWanted
                        if infoW in data.split(" x ")[1]:
                            self.readInfo2 = True
                            self.info2 = infoWanted

        elif self.read and data != "-" and data != "N/A":
            if self.readInfo:
                self.infos[self.info] = data
            else :
                if self.readInfo1:
                    self.infos[self.info1] = data.split(" x ")[0]
                if self.readInfo2:
                    self.infos[self.info2] = data.split(" x ")[1]


class ShipSpottingParser(HTMLParser):
    def __init__(self, infosWanted):
        HTMLParser.__init__(self)
        self.infos = {}
        self.infosWanted = infosWanted.keys()
        self.readTypeOfInfo = False
        self.infoOk = False
        self.readInfo = False

    def handle_starttag(self, tag, attrs):
        if tag == "td" and ("class", "inbox_title") in attrs:
            self.readTypeOfInfo = True
        elif tag == "td" and self.infoOk:
            self.readInfo = True


    def handle_data(self, data):
        if self.readTypeOfInfo:
            for infoWanted in self.infosWanted:
                for infoW in infoWanted.split("/"):
                    if infoW.title() in data.title().replace(":", "").split(" ") or data.title().replace(":", "") in infoW.title():
                        self.info = infoWanted
                        self.infoOk = True
            self.readTypeOfInfo = False
        elif self.readInfo:
            self.infos[self.info] = data
            self.readInfo = False
            self.infoOk = False


class ShippingExplorerParser(HTMLParser):
    def __init__(self, infosWanted):
        HTMLParser.__init__(self)
        self.infos = {}
        self.infosWanted = infosWanted.keys()
        self.infoFound = []
        self.readH2 = False
        self.readH3 = True
        self.readTypeOfInfo = False
        self.infoOk = False
        self.readInfo = False
        self.readName = False

    def handle_starttag(self, tag, attrs):
        if tag == "h2":
            self.readH2 = True
        elif (tag == "h3" and self.readH3 == True) or tag == "b":
            self.readTypeOfInfo = True
        elif tag == "td" and self.infoOk:
            self.readInfo = True
        elif tag == "h1":
            self.readName = True


    def handle_data(self, data):
        if self.readH2 == True:
            if data == "Current Position":
                self.readH3 = False
            self.readH2 = False
        elif self.readTypeOfInfo:
            self.readTypeOfInfo = False
            for infoWanted in self.infosWanted:
                if infoWanted not in self.infoFound:
                    for infoW in infoWanted.split("/"):
                        if infoW.title() in data.title().replace(";", "").split(" ") or data.title().replace(":", "") in infoW.title():
                            self.info = infoWanted
                            self.infoOk = True
                            self.infoFound.append(infoWanted)
        elif self.readInfo:
            if data == "-":
                self.infoFound.remove(self.info)
            else:
                self.infos[self.info] = data.strip()
            self.readInfo = False
            self.infoOk = False
        elif self.readName:
            self.infos["Name"] = data.strip()
            self.readName = False


class GrossTonnageParser(HTMLParser):
    def __init__(self, infosWanted):
        HTMLParser.__init__(self)
        self.infos = {}
        self.infosWanted = infosWanted.keys()
        self.typesOfInfo = []
        self.readTypeOfInfo = False
        self.readInfo = False
        self.count = 0
        self.over = False

    def handle_starttag(self, tag, attrs):
        if self.over == False:
            if tag == "p" and (("class", "t9") in attrs or ("class", "t10") in attrs) :
                if self.count < 6:
                    self.readTypeOfInfo = True
                else:
                    self.readInfo = True
            elif tag == "img" and self.count > 7:
                for elt in attrs:
                    if elt[0] == "alt":
                        self.infos[self.typesOfInfo[self.count-6]] = elt[1].strip().title()
                        self.over = True
                        break

    def handle_data(self, data):
        if self.readTypeOfInfo:
            self.readTypeOfInfo = False
            data = data.strip()
            for infoWanted in self.infosWanted:
                for infoW in infoWanted.split("/"):
                    if data in infoW or data.title() in infoW or infoW in data.title():
                        self.info = infoWanted
                        self.typesOfInfo.append(infoWanted)
                        self.count +=1
        elif self.readInfo:
            self.readInfo = False
            self.infos[self.typesOfInfo[self.count-6]] = data.strip().title()
            self.count +=1

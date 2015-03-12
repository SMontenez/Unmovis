#!/usr/bin/python
# -*-coding:Utf-8 -*-

import os
import datetime
import re
import urllib
import xml.etree.ElementTree as ET

urlapi =  "http://en.wikipedia.org/w/api.php"

# needs also to handle redirects and marking up symbols and spaces
def GetWikipediaArticle(name):
    params = { "format":"xml", "action":"query", "prop":"revisions", "rvprop":"timestamp|user|comment|content"}
    params["titles"] =  urllib.quote(name.encode('utf8'))
    qs = "&".join("%s=%s" % (k, v)  for k, v in params.items())
    url = "%s?%s" % (urlapi, qs)
    tree = ET.parse(urllib.urlopen(url))
    normalizedname = name
    normn = tree.findall('.//normalized/n')
    if normn:
        normalizedname = normn[0].attrib["to"]
    rev = tree.findall('.//rev')[0]
    dicoRev = {"name":normalizedname, "text":rev.text,"timestamp":rev.attrib.get("timestamp"), "user":rev.attrib.get("user"), "comment":rev.attrib.get("comment") }

    return dicoRev


def ParseTemplates(text):
    "Extract all the templates/infoboxes from the text into a list"
    res = { "templates":[ ], "categories":[ ], "images":[ ], "wikilinks":[ ], "flattext":[ ] }
    templstack = [ ]
    for tt in re.split("(\{\{\{|\}\}\}|\{\{|\}\}|\[\[|\]\]|\|)", text):
        if tt in ["{{{", "{{", "[["]:
            templstack.append([tt, [ [ ] ] ])
        elif templstack and tt in ["}}}", "}}", "]]"]:
            templstack[-1][1][-1] = "".join(templstack[-1][1][-1])
            templstack[-1].append(tt)
            if len(templstack) == 1:
                if templstack[-1][0] == "{{":
                    ltempl = [ ]
                    for i, param in enumerate(templstack[-1][1]):
                        k, e, v = param.partition("=")
                        if e:
                            ltempl.append((k.strip(), v.strip()))
                        else:
                            ltempl.append((i, k.strip()))
                    if ltempl:
                        res["templates"].append((ltempl[0][1], dict(ltempl)))
                elif templstack[-1][0] == "[[":
                    llink = templstack[-1][1]
                    if llink:
                        llink0, cllink, cllink1 = llink[0].partition(":")
                        try:
                            if llink[0][0] == ':':   # eg [[:Category:something]]
                                res["wikilinks"].append(llink[-1])
                                res["flattext"].append(llink[0][1:])  # the [[what you see|actual link]]
                            elif cllink:
                                if llink0 == "Category":
                                    res["categories"].append(cllink1.strip())
                                elif llink0 in ["Image", "File"]:
                                    res["images"].append(cllink1.strip())
                                elif len(llink0) == 2:
                                    pass  # links to other languages
                                else:
                                    pass #print("Unrecognized", llink)
                            else:
                                res["wikilinks"].append(llink[-1])
                                res["flattext"].append(llink[0])  # the [[what you see|actual link]]
                        except IndexError:
                            pass
            else:
                templstack[-2][1][-1].append(templstack[-1][0])
                templstack[-2][1][-1].append("|".join(templstack[-1][1]))
                templstack[-2][1][-1].append(templstack[-1][2])
            del templstack[-1]
        elif tt == "|" and templstack:
            templstack[-1][1][-1] = "".join(templstack[-1][1][-1])
            templstack[-1][1].append([ ])
        elif templstack:
            templstack[-1][1][-1].append(tt)
        else:
            res["flattext"].append(tt)
    res["flattext"] = "".join(res["flattext"])
    return res

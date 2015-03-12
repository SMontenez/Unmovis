#!/usr/bin/python
# -*-coding:Utf-8 -*-


def normalize(dicoSection):
    tagsList = []
    for bal in dicoSection.keys():
        tagsList.append(bal)
    contentsList = []
    for cont in dicoSection.values():
        contentsList.append(cont)
    #listeUnitesDeMesure = ['Mm', 'km', 'm', 'cm', 'mm', 'mi', 'nmi', 'yd', 'ft', 'in', 'km2', 'm2', 'cm2', 'mm2', 'sqft', 'acre', 'sqyd', 'sqin', 'm3', 'cm3', 'kl', 'l', 'cl', 'cuft', 'cuin', 'm/s', 'km/h', 'mph', 'ft/s', 'kn', 'MN', 'kN', 'N', 'mN', 'C', 'R', 'F', 'K', 'kg', 'g', 'mg', 'ug', 'LT', 'ST', 'st', 'lb', 'oz', 'dram', 'gr', 'MPa', 'kPa', 'hPa', 'Pa', 'bar', 'l/km', 'km/l', 'mpgus']

    indToDelete = []
    for i,elt in enumerate(tagsList):
        if type(elt) != str and type(elt) != unicode:
            indToDelete.append(i)
        elif 'Ship' not in elt and 'ship' not in elt:
            indToDelete.append(i)
        else:
            #elt = elt.replace('Ship ', '')
            tagsList[i] = elt.title()
            #œtagsList[i] = elt.replace(' ', '_')

    indToDelete.reverse()
    for ind in indToDelete:
        del(tagsList[ind])
        del(contentsList[ind])


    for i,elt in enumerate(contentsList):
        elt = elt.replace('&nbsp;',' ')
        elt = elt.replace('{{nbsp}}',' ')
        contentsList[i] = correct(elt)

    return dict(zip(tagsList, contentsList))


def correct(string):
    j = 0
    newContent = ''
    while j < len(string):
        carac = string[j]

        # Gérer les templates contenant des braces
        if carac == '{':
            if j != len(string)-1:
                if string[j+1] == '{':
                    if string[j+2:j+9] == 'convert' or string[j+2:j+9] == 'Convert':
                        result = convert(j, string)
                    elif string[j+2:j+11] == 'Plainlist' or string[j+2:j+11] == 'plainlist':
                        result = plainlist(j, string)
                    elif string[j+2:j+4] == 'br':
                        result = ('', j+6)
                    else:
                        result = braces(j, string)
                else:
                    result = ('', j+1)
            else:
                result = ('', j+1)

        # Gérer les templates contenant des brackets
        elif carac == '[':
            if string[j+1] == '[':
                if string[j+2:j+6] == 'File':
                    result = file(j, string)
                elif string[j+2:j+7] == 'Image':
                    result = image(j, string)
                else:
                    result = bracket(j, string)
            else:
                result = ('', j+1)

        elif carac == '<':
            if string[j+1:j+4] == 'ref':
                result = ref(j, string)
            elif string[j+1:j+3] == 'br':
                result = br(j, string)
            else:
                result = balise(j, string)

        elif carac in ['{', '}', ']', '\'']:
            result = ('', j+1)

        elif carac in ['\n', ';']:
            result = (' ', j+1)

        else:
            result = (carac, j+1)

        newContent += result[0]
        j = result[1]

    if "present:" in newContent:
        newContent = newContent.split("present:")[1].strip()

    return newContent


# Permet de lire les templates 'convert'
def convert(ind, string):
    tempString = string[ind:]
    end = ind + tempString.find('}}') + 2
    tempString = string[ind+10:end-2]

    valuesList = []
    notOver = True
    while notOver:
        sep = tempString.find('|')
        if sep == -1:
            notOver = False
            value = tempString
        else:
            value = tempString[:sep]
        if '=' not in value:
            valuesList.append(value)
        tempString = tempString[sep+1:]

    indTest = len(valuesList) - 1
    if (indTest > 1 and '-' not in valuesList) or indTest > 3:
        try:
            float(valuesList[indTest])
            indTest -= 2
            try:
                float(valuesList[indTest])
                indTest += 1
            except ValueError:
                pass
        except ValueError:
            indTest -= 1
            try:
                int(valuesList[indTest])
                indTest -= 1
            except ValueError:
                pass

    tempString = ''
    for j in range(0, indTest+1):
        tempString += valuesList[j]
        if valuesList[j] != '-' and j < indTest and valuesList[j+1] != '-':
            tempString += ' '

    return correct(tempString), end


def plainlist(ind, string):
    tempString = string[ind:]
    sep = tempString.find('|')
    end = ind + sep + 1

    return '', end


def braces(ind, string):
    tempString = string[ind:]
    braceEnd = tempString.find('}}')
    takeLastPart = False

    autreAcc = tempString[2:braceEnd].find('{{')
    if autreAcc != -1:
        braceFakeEnd = braceEnd
        braceEnd = braceFakeEnd + 2 + tempString[braceFakeEnd+2:].find('}}')
        tempString = tempString[2:autreAcc+2] + '|' + tempString[braceFakeEnd+2:braceEnd]
        takeLastPart = True
    else:
        tempString = tempString[2:braceEnd]

    end = ind + braceEnd + 2
    nb = tempString[:tempString.find('}}')].count('|')

    if nb != 0:
        sep = tempString.find('|')
        try:
            float(tempString[sep+1:].replace(',','.'))
            tempString = tempString.replace('|', ' : ')
        except ValueError:
            tempString = tempString[sep+1:]
            if nb == 2:
                sep = tempString.find('|')
                if takeLastPart:
                    tempString = tempString[sep+1:]
                else:
                    tempString = tempString[:sep]

    return correct(tempString), end


def file(ind, string):
    tempString = string[ind:]
    bracketEnd = tempString.find(']]')
    tempString = tempString[2:bracketEnd]

    end = ind + bracketEnd + 2
    sep = tempString.find('|')

    return correct(tempString[:sep].replace('File:', '')), end


def image(ind, string):
    tempString = string[ind:]
    bracketEnd = tempString.find(']]')
    tempString = tempString[2:bracketEnd]

    end = ind + bracketEnd + 2
    sep = tempString.find('|')

    return correct(tempString[:sep].replace('Image:', '')), end


def bracket(ind, string):
    tempString = string[ind:]
    bracketEnd = tempString.find(']]')
    tempString = correct(tempString[2:bracketEnd])

    end = ind + bracketEnd + 2
    nb = tempString.count('|')

    if nb != 0:
        sep = tempString.find('|')
        if nb == 1:
            tempString = tempString[sep+1:]
        elif nb == 2:
            tempString = tempString[:sep]
        else:
            print('ERREUR : double bracket non traité !')
    return correct(tempString), end


def ref(ind, string):
    tempString = string[ind:]
    openClosingTag = tempString.find('/>')
    closingTag = tempString.find('</ref>')
    if openClosingTag == -1 and closingTag == -1:
        closingTag = tempString.find('>')
        if closingTag == -1:
            end = len(string)
        else:
            end = ind + closingTag + 1
    elif openClosingTag == -1 and closingTag != -1:
        end = ind + closingTag + 6
    elif openClosingTag != -1 and closingTag == -1:
        end = ind + openClosingTag + 2
    else:
        if openClosingTag < closingTag :
            end = ind + openClosingTag + 2
        else:
            end = ind + closingTag + 6
    return '', end


def br(ind, string):
    tempString = string[ind:]
    end = ind + tempString.find('>') + 1
    return ' ', end


def balise(ind, string):
    tempString = string[ind:]
    openingTagEnd = tempString.find('>')
    closingTagStart = tempString.find('</')

    if closingTagStart == -1:
        if openingTagEnd == -1:
            return '', len(string)
        else:
            end = ind + openingTagEnd + 1
            return '', end
    else:
        end = ind + closingTagStart + tempString[closingTagStart:].find('>') + 1
        tempString = tempString[openingTagEnd+1:closingTagStart]
        return correct(tempString), end

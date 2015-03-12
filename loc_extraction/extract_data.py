#!/usr/bin/python
# -*-coding:Utf-8 -*-

import apiblender
import time
import useful_functions

def extract_infos_from_pic(keyword, minDate):

    startTime = time.time()

    target_blender= apiblender.Blender()

    target_blender.load_server('flickr')
    target_blender.load_interaction('photos_search')
    target_blender.set_url_params({'text': keyword, 'min_taken_date': minDate})

    ids = set()

    nbPages = target_blender.blend()["loaded_content"]["photos"]["pages"]
    print(nbPages)

    for p in range(1, nbPages+1):
        target_blender.set_url_params({'page': p})
        results = target_blender.blend()
        for photo in results['loaded_content']['photos']['photo']:
            ids.add(photo['id'])
    print str(len(ids))

    # data will be a list of lists, each innner list will describe the infos
    # about 1 picture this way => [picId, userId, date, [nbOfPic, listOfPicUrls], keywordPosition, location, filtersResult]

    probExtraction = []
    data = []

    for i, _id in enumerate(ids):
        print(str(i) + "/" + str(len(ids)))
        try:
            picData = []
            picData.append(_id)

            target_blender.load_interaction('photo_informations')
            target_blender.set_url_params({'photo_id': _id})
            result = target_blender.blend()

            infos = result['loaded_content']['photo']
            picData.append({"userID":infos['owner']['nsid'], "username":infos['owner']['username']})
            picData.append(infos['dates']['taken'])
            picData.append([1, {"page": infos['urls']['url'][0]['_content']}])
            picData.append(useful_functions.find_keyword(keyword.replace('+', ' '), infos))

            target_blender.load_interaction('photo_source')
            target_blender.set_url_params({'photo_id': _id})
            result = target_blender.blend()

            picData[3][1]['source'] = useful_functions.find_source(result['loaded_content']['sizes']['size'])

            target_blender.load_interaction('photo_location')
            target_blender.set_url_params({'photo_id': _id})
            result = target_blender.blend()
            picData.append([result['loaded_content']['photo']['location']['latitude'], result['loaded_content']['photo']['location']['longitude']])

            # The filtersResult part consists of 3 values, for the onLand,
            # impossibleJourney and outliersRemoval filters
            picData.append([0,0,0])
            data.append(picData)

        except:
            probExtraction.append(_id)

    duration = time.time() - startTime

    return data, duration, probExtraction

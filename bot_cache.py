import requests
import urllib.parse
import json
import time

from PIL import Image
import io

import nflfive as nfl5

import logging

class BotCache:
    paniniCardImageCache = {}
    paniniCardImageCacheStats = {'cacheHit': 0, 'cacheMiss': 0}
    paniniCardImageFetchStats = {'fetchCount': 0, 'fetchFailures': 0, 'timeFetching': 0}

    imageCache = {}
    imageCacheStats = {'cacheHit': 0, 'cacheMiss': 0}
    imageFetchStats = {'fetchCount': 0, 'fetchFailures': 0, 'timeFetching': 0}

    logger = logging.getLogger()

    def __init__(self):
        theVariable = 0

    #Get the card image url from paninigames.com or the cache
    def fetchCardImageURLWithCache(self, the_card_number, the_card_type, the_card_set, the_card_special_text):
        theCardImageUrl = nfl5.generateUrl(the_card_number, the_card_type, the_card_set, the_card_special_text)
        theCardImage = None
        
        cacheKey = f"{the_card_number}{the_card_set}"
        print(f"Cache check on '{theCardImageUrl}'")
        if(cacheKey not in self.paniniCardImageCache):
            print(f"Cache MISS locating '{theCardImageUrl}'")
            self.paniniCardImageCacheStats['cacheMiss'] = self.paniniCardImageCacheStats['cacheMiss'] + 1
            theCardImage = self.fetchCardImage(theCardImageUrl)
            print(f"Caching data with Key {cacheKey}")
            self.paniniCardImageCache[cacheKey] = theCardImage

        else:
            print(f"Cache HIT pulling data with Key {cacheKey}")
            self.paniniCardImageCacheStats['cacheHit'] = self.paniniCardImageCacheStats['cacheHit'] + 1
            theCardImage = self.paniniCardImageCache[cacheKey]

        return theCardImage

    def fetchCardImage(self, theCardImageUrl):
        print(f"Attempting to fetch image from: {theCardImageUrl}")
        cardImage = Image.new('RGBA', (1, 1))

        startTime = time.time()

        self.imageFetchStats['fetchCount'] = self.imageFetchStats['fetchCount'] + 1

        imageDataResults = requests.get(theCardImageUrl, stream=True)
        if(imageDataResults.status_code == requests.codes.ok):
            print(f"got data from a request to {theCardImageUrl}")
            cardImage = Image.open(imageDataResults.raw)
        else:
            self.imageFetchStats['fetchFailures'] = self.imageFetchStats['fetchFailures'] + 1
            cardImage = Image.new('RGBA', (1, 1))

        endTime = time.time()
        print(f"Image Fetch of {theCardImageUrl} took {endTime-startTime:.5f}s")
        self.imageFetchStats['timeFetching'] = self.imageFetchStats['timeFetching'] + (endTime - startTime)

        return cardImage
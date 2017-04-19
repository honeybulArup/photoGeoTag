import exifread 
import os 
import numpy as np 
import re 
import sys
import json
import ast
from PIL import Image 
from PIL.ExifTags import TAGS
from pymongo import MongoClient
from geojson import Feature, Point, FeatureCollection

def fns(root_dir='public/', dir_names=['sitevisitCatherine/']):
    fnames = []
    for dir_name in dir_names:
        fns = os.listdir(root_dir + dir_name)
        for f in fns:
            if f.endswith('.jpg') or f.endswith('.png') or f.endswith('.JPG') or f.endswith('.PNG'):
                fnames.append((root_dir + dir_name, f))
    return fnames

def process_file(fn, dir_name):
    tags = exifread.process_file(open(dir_name + fn, 'rb'))
    return tags     

def get_geo_tags(tags, fname, dirname):

    photoData = {}
    photoData['image'] = dirname + fname
    i = Image.open(dirname + fname)
    info = i._getexif()
    for tag, value in info.items():
        decoded = TAGS.get(tag, tag)
        if decoded == 'GPSInfo':
            
            lat = value[2]

            d0 = lat[0][0]
            d1 = lat[0][1]
            d = float(d0) / float(d1)

            m0 = lat[1][0]
            m1 = lat[1][1]
            m = float(m0)/ float(m1)

            s0 = lat[2][0]
            s1 = lat[2][1]
            s = float(s0) / float(s1)

            latitude = d + (m / 60.0) + (s / 3600.0)

            lng = value[4]

            d0 = lng[0][0]
            d1 = lng[0][1]
            d = float(d0) / float(d1)

            m0 = lng[1][0]
            m1 = lng[1][1]
            m = float(m0)/ float(m1)

            s0 = lng[2][0]
            s1 = lng[2][1]
            s = float(s0) / float(s1)

            longitude = d + (m / 60.0) + (s / 3600.0)

            photoData['Lat'] = latitude 
            photoData['Long'] = longitude 

        if decoded == 'DateTime':
            photoData['time_taken'] = str(value) 
    dataToJSON(photoData, fname, dirname)
    return photoData 
         
def dataToJSON(data, fname, dirname):
    with open('dataDicts/' + re.sub('/','',dirname) + '-' + fname.split('.')[0] + '.json', 'w') as f:
        json.dump(data, f, indent=2)

def removeCurrentFiles(dirname='dataDicts/'):
    fns = os.listdir(dirname)
    for fn in fns:
       os.remove(dirname + fn)

def toGeoJSON(dict):
    featureColl = []
    for d in dict:
        featureColl.append(Feature(geometry=Point((d['Long'],-d['Lat'])), properties = {'time_taken' : d['time_taken'], 'image': d['image']}))
    with open('public/geojson/data.geojson', 'wb') as f:
        json.dump(FeatureCollection(featureColl), f, indent=2)

def main():
    fnames = fns()
    removeCurrentFiles()
    Dictionary = []
    for i, dTuple in enumerate(fnames):
        dirname, fname = dTuple
        progress = float(i) * 100 / len(fnames)
        tags = process_file(fname, dirname)
        dict_ii = get_geo_tags(tags, fname, dirname)
        if dict_ii:
            Dictionary.append(dict_ii)
    toGeoJSON(Dictionary)

if __name__ == '__main__':
    main()
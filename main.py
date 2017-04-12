import exifread 
import os 
import numpy as np 
import re 
import sys
import json
import ast
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
    if 'GPS GPSLongitude' in tags and 'GPS GPSLatitude' in tags:
        Long = json.loads(str(tags['GPS GPSLongitude']).replace("/",","))
        longArr = [Long[0], Long[1], float(Long[2])/Long[3]]
        longitude = longArr[0] + (longArr[1] + float(longArr[2]) / 60) / 100
        photoData['Long'] = longitude
        
        Lat = json.loads(str(tags['GPS GPSLatitude']).replace("/",","))
        latArr = [Lat[0], Lat[1], float(Lat[2])/Lat[3]]
        latitude = latArr[0] + (latArr[1] + float(latArr[2]) / 60) / 100
        photoData['Lat'] = latitude

        photoData['image'] = dirname + fname

        time_taken = str(tags['Image DateTime'])
        photoData['time_taken'] = time_taken
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
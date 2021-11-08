#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Nov  3 11:01:46 2021

@author: qdimarellis-adc
"""
import json
import argparse


def get_args():
    parser = argparse.ArgumentParser(description='')
    parser.add_argument("-f", "--file-path", default=None, type=str, help="chemin vers le fichier à modifier")
    parser.add_argument("-i", "--index", default=None, type=str, help="nom de l'index dans lequel le fichier doit être chargé")
    parser.add_argument("-o", "--outfile", default=None, type=str, help="fichier dans lequel sauvegarder la requête bulk")
    args = parser.parse_args()
    return args.file_path, args.index, args.outfile


def main():
    file, index, out = get_args()
    with open(file) as fp:
        geojson = json.load(fp)
    
    index = {"index":{"_index":index}}
    
    with open(out, mode="a") as fp:
        for feature in geojson["features"]:
            json.dump(index, fp)
            fp.write('\n')
            json.dump(feature, fp)
            fp.write('\n')
        fp.write('\n\n')

if __name__ == "__main__":
    main()

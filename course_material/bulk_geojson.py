#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Nov  3 10:22:19 2021

@author: qdimarellis-adc
"""
import json
import elasticsearch.helpers
import ssl
import argparse

def export_file_into_elastic(file, indice, config):
    es = get_es_instance(config)

    actions = ({"_index": indice,
                 "_source": feature} for feature in file["features"])
    success, failed, errors = 0, 0, []
    for ok, item in elasticsearch.helpers.streaming_bulk(es, actions, raise_on_error=False):
        if not ok:
            errors.append(item)
            failed += 1
        else:
            success += 1
    print(f"{success} successfully inserted into {indice}")
    if errors:
        print(f"{failed} errors detected\nError details : {errors}")
        
def get_es_instance(conf):
    """Instanciates an Elasticsearch connection instance based on connection parameters from the configuration"""
    _host = (conf.get("user"), conf.get("pwd"))
    if _host == (None, None):
        _host = None
    if "cafile" in conf:
        _context = ssl.create_default_context(cafile=conf["cafile"])
        es_instance = elasticsearch.Elasticsearch(
            conf.get("host", "localhost"),
            http_auth=_host,
            use_ssl=True,
            scheme=conf["scheme"],
            port=conf["port"],
            ssl_context=_context,
        )
    else:
        es_instance = elasticsearch.Elasticsearch(
            conf.get("host", "localhost"),
            http_auth=_host,
        )
    return es_instance

def get_args():
    parser = argparse.ArgumentParser(description='')
    parser.add_argument("-f", "--file-path", default=None, type=str, help="")
    parser.add_argument("-i", "--index", default=None, type=str, help="")
    args = parser.parse_args()
    return args.file_path, args.index

def main():
    try:
        with open("./conf/config.json") as f:
            config = json.load(f)
    except FileNotFoundError:
        config = {}
    file_path, indice = get_args()
    with open(file_path) as fp:
        file = json.load(fp)
    export_file_into_elastic(file, indice, config)


if __name__ == "__main__":
    main()

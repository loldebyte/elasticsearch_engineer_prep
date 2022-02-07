# General Tips
All code snippets are taken from Kibana's `Dev Tools` console, unless stated otherwise.

Try to come up with a solution before opening any "spoilers" in this document ! This also applies to the code snippets provided for testing !

## Recommended reads
This [webinar](https://www.youtube.com/watch?v=9UpB-s_ZfNE) for details about the exam environment and a few exercices.

[This article](https://www.linkedin.com/pulse/elastic-certified-engineer-exam-my-experience-how-i-surbhi-mahajan) for its concrete experience and recommendations.

The official [documentation](https://www.elastic.co/guide/en/elasticsearch/reference/7.15/elasticsearch-intro.html). Familiarity with the documentation is crucial.

# Credits
Sincere thanks to Guido Lena Cota for
[his excellent article](https://medium.com/kreuzwerker-gmbh/exercises-for-the-elastic-certified-engineer-exam-store-data-into-elasticsearch-cbce230bcc6)
whose exercises are included almost as-is, and was a major inspiration for the present document.

# Table of Contents

## [Practical Guide](#practical_guide)

## Exam exercises

### [Data Management](#data_management)

### [Searching Data](#searching_data)

### [Developing Search Applications](#search_application)

### [Data Processing](#data_processing)

### [Cluster Management](#cluster_management)

# <a id="practical_guide"></a>Practical Guide

REQUIRED SETUP:
 - create an indice `hamlet-raw`

<details>
  <summary>Create hamlet-raw</summary>

```
PUT halmet-raw
```
</details>

## Add a document to `hamlet-raw`, so that the document (i) has id "1", (ii) has default type, (iii) has one field named `line` with value "To be, or not to be: that is the question"
<details>
    <summary>Solution</summary>

```json
PUT hamlet-raw/_doc/1
{
    "line": "To be, or not to be: that is the question"
}
```
</details>

## Add a new document to `hamlet-raw`, so that the document (i) has  the id automatically assigned by Elasticsearch, (ii) has  default type, (iii) has a field named `text_entry` with value "Whether tis nobler in the mind to suffer", (iv) has a field  named `line_number` with value "3.1.66"

<details>
    <summary>Solution</summary>

```json
POST hamlet-raw/_doc
{
  "text_entry": "Whether tis nobler in the mind to suffer",
  "line_number": "3.1.66"
}

```
</details>

## Remove from `hamlet` the documents that have either `"KING CLAUDIUS"` or `"LAERTES"` as the value of `speaker`
[Delete by Query](https://www.elastic.co/guide/en/elasticsearch/reference/7.15/docs-delete-by-query.html)\
[Boolean Query](https://www.elastic.co/guide/en/elasticsearch/reference/7.15/query-dsl-bool-query.html) for "OR" searches\
[Full text Query](https://www.elastic.co/guide/en/elasticsearch/reference/7.15/full-text-queries.html)
<details>
    <summary>Solution</summary>

```json
POST hamlet/_delete_by_query
{
  "query": {
    "bool": {
      "should": [
        {"match": { "speaker": "KING CLAUDIUS"}},
        {"match": {
          "speaker": "LAERTES"
        }}
        ],
      "minimum_should_match": 1
    }
  }
}
```
</details>

## Index a geoJSON without using kibana's UI
In this exercise, we will learn how to index a geojson file into elasticsearch with two methods :
 - Using `cURL`
 - Using python's `elasticsearch` package

The geoJSON we will work on is `carte_judiciaire.geojson` in `./course_material`.

First, try to directly upload the file into the `carte_judicaire` index. Lets not worry about mappings yet, even though as you may know geographic data will usually require an explicit mapping. You might want to have a look [there](https://www.elastic.co/guide/en/elasticsearch/reference/7.15/docs-index_.html).

<details>
    <summary>curl command to index into carte_judiciaire</summary>

```bash
curl -H 'Content-Type: application/x-ndjson' -XPOST '127.0.0.1:9200/carte_judiciaire/_doc' --data-binary @carte_judiciaire.geojson
```
</details>

/!\ IMPORTANT : if you have activated security on your local instance do not forget to include credentials : `-u elasticsearch_username:elasticsearch_password` /!\

When you've managed to do that, investigate the outcome : what does the mapping look like ? What does the data loaded in it look like ?

<details>
    <summary>What you should notice</summary>

We only have a single document, because we used the `_doc` endpoint, and it can index only a single document. We want to have a document per polygon !
</details>

I encourage you to try to fiddle around with the json file, curl and kibana's devtools console. When you feel stuck or feel like you're about to do a drastic change, open the following spoiler.

<details>
    <summary>The problem</summary>

This geojson is a collection of `features`, ie its a JSON containing a list of other JSONs. We want to index the JSONs in the list, individually.\
Therefor, we have to change the source file itself !\
The example provided will be doing this in python, but you are free to do it otherwise.\
`> But you said we'd learn how to do it with curl !!`\
Yes, we will _index_ the document with curl, but we still need to change it, and i will do that in python. In the real world, this is useful because you may not be able to connect to your ES instance in python.
</details>

Since we want to index multiple documents, we will want to use the [bulk API](https://www.elastic.co/guide/en/elasticsearch/reference/7.15/docs-bulk.html).\
It is much more important that you understand what needs to be done rather than actually implement it, so do think about how you would create a bulkable ndjson from the original `carte_judiciaire.geojson` file.

<details>
    <summary>I'm stuck, what do i need to do & how ?</summary>

As said in the previous spoiler, we want to index each and every JSON in the `features` list. Indexing multiple documents requires using the `_bulk` endpoint, which expects a file in the form of :
```
action_and_meta_data\n
optional_source\n
```
This information is in the [documentation](https://www.elastic.co/guide/en/elasticsearch/reference/7.15/docs-bulk.html#docs-bulk-api-desc), and it is the crucial part for this exercise.
</details>

<details>
    <summary>Solution : bulkable format</summary>

Our reformatted geojson will look like :
```json
{"index": {"_index": "carte_judiciaire"}}
{<first element in the features list>}
{"index": {"_index": "carte_judiciaire"}}
{<second element in the features list>}
...
```
</details>


<details>
    <summary>Solution : example script</summary>

```python
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
            json.dump(index, fp)  # the action metadata
            fp.write('\n')  # _bulk expects a ndjson
            json.dump(feature, fp)  # the action, ie field/value pair(s).
            fp.write('\n')
        fp.write('\n')

if __name__ == "__main__":
    main()
```
</details>

Now, reformat your geojson using the script :
```bash
python ./create_bulkable_geojson.py -f carte_judiciaire.geojson -i carte_judiciaire -o bulkable_carte_judiciaire.ndjson
```
This snipped is included as an example, you're free to use whatever arguments you want. We now want to index the newly created `bulkable_carte_judicaire.ndjson`, using curl.\
If you have no idea how to do that, then you haven't read the [bulk API](https://www.elastic.co/guide/en/elasticsearch/reference/7.15/docs-bulk.html) docs carefully enough !

<details>
    <summary>bulk op</summary>

What needs to be done here is simply to curl onto the `_bulk` endpoint :
```bash
curl -H 'Content-Type: application/x-ndjson' -XPOST 'localhost:9200/_bulk' --data-binary @bulkable_carte_judiciaire.ndjson
```
This request only works on a local elasticsearch instance with no security enabled. Dont forget to change `bulkable_carte_judiciaire.ndjson` if you need to !
</details>

Now that this is done, you may think we've just done it, but in fact we've one last obstacle to overcome : check the index's mapping.

<details>
    <summary>Solution</summary>

To get the mapping :
```json
GET carte_judiciaire/_mapping
```
Which should output :
```json
{
  "carte_judiciare" : {
    "mappings" : {
      "properties" : {
        "geometry" : {
          "properties" : {
            "coordinates" : {
              "type" : "float"
            },
            "type" : {
              "type" : "text",
              "fields" : {
                "keyword" : {
                  "type" : "keyword",
                  "ignore_above" : 256
                }
              }
            }
          }
        },
        "properties" : {
          "properties" : {
            "nom" : {
              "type" : "long"
            }
          }
        },
        "type" : {
          "type" : "text",
          "fields" : {
            "keyword" : {
              "type" : "keyword",
              "ignore_above" : 256
            }
          }
        }
      }
    }
  }
}
```
Which should look bad to you !
</details>

Looks like elasticsearch's [dynamic mapping](https://www.elastic.co/guide/en/elasticsearch/reference/7.15/dynamic-mapping.html) didnt understand `geometry` nor `coordinates` as [Spatial Data Types](https://www.elastic.co/guide/en/elasticsearch/reference/7.15/mapping-types.html#spatial_datatypes). The default dynamic mapping is really hesistant about parsing data as spacial data, so you will likely need to provide an explicit mapping or an [index_template](#index_template).\
In general, i would suggest staying as far away as possible from dynamic mapping, but this is to be discussed elsewhere.\
What we need to do now : change the mapping, delete the index, and bulk once more. Obviously in production you would have to create the mapping beforehands.\
To change the mapping i suggest copying the return from `GET carte_judicaire/_mapping` and start from there.\
When you're stuck or think you've made it, check the correction below.

<details>
    <summary>Mapping</summary>

```json
PUT carte_judiciaire
{
  "mappings" : {
      "properties" : {
        "geometry" : {
            "type": "geo_shape"
        },
        "properties" : {
          "properties" : {
            "nom" : {
              "type" : "long"
            }
          }
        },
        "type" : {
          "type" : "text",
          "fields" : {
            "keyword" : {
              "type" : "keyword",
              "ignore_above" : 256
            }
          }
        }
      }
    }
}
```
> Why use `geo_shape` and not `type X` ?

Because our data is polygons, we cannot use `point` or `geo_point`. But `shape` is much trickier. In the [documentation](https://www.elastic.co/guide/en/elasticsearch/reference/7.15/shape.html) one can read that :
 > In GeoJSON and WKT, and therefore Elasticsearch, the correct coordinate order is (X, Y) within coordinate arrays. This differs from many Geospatial APIs (e.g., **geo_shape**) that typically use the colloquial latitude, longitude (Y, X) ordering.

 Our data uses the (Y, X) ordering, and thus, the correct type is `geo_shape` !
</details>

To assert everything works as intended, you can create a map layer that shows the french jurisdiction areas.

Now let's see how we could've done the bulk operation in python.\
First of all, create an index `carte_judiciaire2` with the exact same mapping as `carte_judiciare`.\
Now using the elasticsearch python package, connect to your local elasticsearch using [Elasticsearch](https://elasticsearch-py.readthedocs.io/en/v7.15.1/api.html#elasticsearch) and then use [streaming_bulk](https://elasticsearch-py.readthedocs.io/en/v7.15.1/helpers.html) to bulk the documents.\
Because this is not a python tutorial and this is not a trivial task _and_ the logic has already been explained, i'll just provide you with a script that does it, but i encourage you to try to write one on your own !

<details>
    <summary>bulk_into_elasticsearch.py</summary>

```python
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
```
This script requires a configuration file in a subdirectory `"./conf/config.json"` that specifies the elasticsearch connection parameters, but it can be omitted if you use a local elasticsearch without security. It takes two arguments : `-f` to specify the file to bulk from, in our case `carte_judiciaire.geojson`, and `-i` to specify the index to load into, in our case `carte_judiciaire2`.
</details>

Once again, creating a map layer is a good way to test out the results.

## Changing an index's _dynamic_ settings

### Set the number of replicas of the index `hamlet` to 0
There are many reasons why you would want to do this : maybe the index is not used much anymore and availability is not as huge a concern anymore, maybe you're about to do a (chain of) big operation(s) and replicating those makes little sense, etc...
You probably want to check out [the related documentation](https://www.elastic.co/guide/en/elasticsearch/reference/7.15/indices-update-settings.html)

<details>
    <summary>Solution</summary>

```json
PUT hamlet/_settings
{
  "number_of_replicas": 0
}
```
</details>

### Make the `lorem-ipsum` index read-only
REQUIRED SETUP:
 - an existing index in the cluster named `lorem-ipsum`

<details>
    <summary>Solution</summary>

```json
  PUT lorem-ipsum/_settings
  {
    "index.blocks.write": false
  }
```
</details>

There is also a [dedicated endpoint](https://www.elastic.co/guide/en/elasticsearch/reference/7.15/index-modules-blocks.html) for `blocks` operation !

<details>
    <summary>Using _block</summary>

```
PUT /lorem-ipsum/_block/write
```
</details>


# **Exam Objectives**
## <a id="data_management">Data Management</a>
### <a id="create_index_with_settings">Define an index that satisfies a given set of requirements</a>
<details>
    <summary>Defining an index:</summary>

```json
PUT <index_name>
{
    "settings": {
        "index": {
            "number_of_shards": 3
        }
    }
}
```
équivalent à :
```json
PUT <index_name>
{
    "settings": {
        "index.number_of_shards": 3
    }
}
```
</details>

#### Create the index `hamlet-raw` with 1 primary shard and 3 replicas
<details>
    <summary>Solution</summary>

```json
PUT hamlet-raw
{
    "settings": {
        "index.number_of_replicas": 3
    }
}
```
car `number_of_shards` vaut 1 par défaut.
</details>

#### Create the index `multitype` with (i) a `geoloc` field of type `geo_point` (ii) an `id` field of type `keyword` (iii) a field `phrase` of type `text` with the analyzer `french` (iv) a field `ip` of type `ip` and (v) an alias field to `phrase` named `french`.

If you wonder about any of these types, see [mapping types](https://www.elastic.co/guide/en/elasticsearch/reference/7.15/mapping-types.html)

<details>
    <summary>Solution</summary>

```json
PUT multitype
{
  "mappings": {
    "dynamic": "strict",
    "properties": {
      "geoloc": {
        "type": "geo_point"
      },
      "id": {
        "type": "keyword"
      },
      "phrase": {
        "type": "text",
        "analyzer": "french"
      },
      "ip": {
        "type": "ip"
      },
      "french": {
        "type": "alias",
        "path": "phrase"
      }
    }
  }
}
```
</details>
  
### Use the Data Visualizer to upload a text file into Elasticsearch

[TODO]: # (ajouter example)
[Documentation](https://www.elastic.co/guide/en/machine-learning/7.15/ml-gs-visualizer.html)

### <a id="index_template">Define and use an index template for a given pattern that satisfies a given set of requirements</a>
REQUIRED SETUP:
 - a running Elasticsearch cluster with at least one node and a Kibana instance,
 - the cluster has no index with name `hamlet`, 
 - the cluster has no template that applies to indices starting by `hamlet`
#### Create the index template `hamlet_template`, so that the template (i) matches any index that starts by "hamlet_" or "hamlet-", (ii) allocates one primary shard and no replicas for each matching index 

 
 [Index Template](https://www.elastic.co/guide/en/elasticsearch/reference/7.15/index-templates.html)
<details>
    <summary>Create the index template</summary>

```json
PUT _index_template/hamlet_template
{
  "index_patterns": ["hamlet_*", "hamlet-*"], 
  "template": {
    "settings": {
      "number_of_replicas": 0
    }
  }
}
```
Note that `"index_pattern"` here refers to a pattern matching indices, not a kibana index pattern
</details>

You should be able to create indices and check their configuration by now, if not, check the [practical guide](#practical_guide)

#### Update `hamlet_template` by defining a mapping for the type "_doc", so that (i) the type has three fields, named `speaker, `line_number`, and `text_entry`, (ii) `text_entry` uses an "english" analyzer

<details>
    <summary>Solution</summary>

```json
PUT _index_template/hamlet_template
{
  "index_patterns": ["hamlet_*", "hamlet-*"],
  "template": {
    "settings": {
      "number_of_replicas": 0
    },
    "mappings": {
      "properties": {
        "speaker": {
          "type": "text"
        },
        "line_number": {
          "type": "text"
        },
        "text_entry": {
          "type": "text",
          "analyzer": "english"
        }
      }
    }
  }
}
```
</details>
Note index templates apply at index creation only, so `hamlet_test` will not have its mapping changed.

#### Create the index `hamlet-1` and add some documents by running the following `_bulk` command, then verify its mapping follows the one from `hamlet_template`
<details>
    <summary>bulk command</summary>

```json
PUT hamlet-1/_doc/_bulk
{"index":{"_index":"hamlet-1","_id":0}}
{"line_number":"1.1.1","speaker":"BERNARDO","text_entry":"Whos there?"}
{"index":{"_index":"hamlet-1","_id":1}}
{"line_number":"1.1.2","speaker":"FRANCISCO","text_entry":"Nay, answer me: stand, and unfold yourself."}
{"index":{"_index":"hamlet-1","_id":2}}
{"line_number":"1.1.3","speaker":"BERNARDO","text_entry":"Long live the king!"}
{"index":{"_index":"hamlet-1","_id":3}}
{"line_number":"1.2.1","speaker":"KING CLAUDIUS","text_entry":"Though yet of Hamlet our dear brothers death"}
```
</details>
To search

#### Update `hamlet_template` so as to reject any document having a field that is not defined in the mapping & verify that you cannot index the following document in `hamlet-1`
<details>
    <summary>This document should get rejected</summary>

```json
POST hamlet-1/_doc 
{ 
  "author": "Shakespeare" 
}
```
</details>


[dynamic mapping](https://www.elastic.co/guide/en/elasticsearch/reference/7.15/dynamic.html)
<details>
    <summary>Update template</summary>

```json
PUT _index_template/hamlet_template
{
  "index_patterns": ["hamlet_*", "hamlet-*"],
  "template": {
    "settings": {
      "number_of_replicas": 0
    },
    "mappings": {
      "properties": {
        "speaker": {
          "type": "text"
        },
        "line_number": {
          "type": "text"
        },
        "text_entry": {
          "type": "text",
          "analyzer": "english"
        }
      },
      "dynamic": "strict"
    }
  }
}

```
</details>

### Define and use a dynamic template that satisfies a given set of requirements

#### Update `hamlet_template` so as to (i) allow dynamic mapping again, (ii) dynamically map to an integer any field that starts by "number_" and (iii) dynamically map to unanalysed text any string field & create the index `hamlet-2` and add a document by running the following command

<details>
    <summary>Execute this after updating your template</summary>

```json
POST hamlet-2/_doc/4
{
  "text_entry": "With turbulent and dangerous lunacy?",
  "line_number": "3.1.4",
  "number_act": "3",
  "speaker": "KING CLAUDIUS"
}
```
</details>

[Dynamic template](https://www.elastic.co/guide/en/elasticsearch/reference/7.15/dynamic-templates.html)
<details>
    <summary>Update template</summary>

```json
PUT _index_template/hamlet_template
{
  "index_patterns": ["hamlet_*", "hamlet-*"],
  "template": {
    "settings": {
      "number_of_replicas": 0
    },
    "mappings": {
      "properties": {
        "speaker": {
          "type": "text"
        },
        "line_number": {
          "type": "text"
        },
        "text_entry": {
          "type": "text",
          "analyzer": "english"
        }
      },
      "dynamic": "true",
      "dynamic_templates": [
        {
          "number_prefixed_as_integers": {
            "match": "number_*",
            "mapping": {
              "type": "long"
            }
          }
        },
        {
          "unanalyze_strings": {
            "match_mapping_type": "string",
            "mapping": {
              "type": "text",
              "analyzer": "keyword"
            }
          }
        }
      ]
    }
  }
}
```
</details>

Now inspect the newly created index's mapping to assert the mapping follows the template's.


### Define an index template that creates a new data stream

[TODO]: # (https://www.elastic.co/guide/en/elasticsearch/reference/7.15/set-up-a-data-stream.html)

### Define an Index Lifecycle Management policy for a time-series index

[TODO]: # (https://www.elastic.co/guide/en/elasticsearch/reference/current/getting-started-index-lifecycle-management.html)
using a data stream & an index template

## <a id="searching_data">Searching Data</a>
REQUIRED SETUP:
 - the cluster has an index with name `multitype`
 - the `multitype` index's mapping matches the one from the [index creation](#create_index_with_settings) section

### Write and execute a search query for terms and/or phrases in one or more fields of an index
[Search your Data](https://www.elastic.co/guide/en/elasticsearch/reference/7.15/search-your-data.html)

#### Simple search on a string field
Lets search for all documents containing `"composition"` in their `french` field.

<details>
    <summary>Solution</summary>

```json
GET multitype/_search
{
  "query": {
    "match": {
      "french": "composition"
    }
  }
}
```
</details>

#### Exact search on a string field



#### Simple search on multiple fields

[Disjunction max](https://www.elastic.co/guide/en/elasticsearch/reference/7.15/query-dsl-dis-max-query.html) aka `dis_max`.

We'll start by searching for documents containing "Beethoven" or matching the following ip : 127.0.0.0/31.
<details>
    <summary>Solution</summary>

```json
GET multitype/_search
{
  "query": {
    "dis_max": {
      "queries": [
        {"match": {
          "phrase": "Beethoven"
        }},
        {
          "match": {
            "ip": "127.0.0.0/31"
          }
        }
        ]
    }
  }
}
```
</details>

Now, we'll search only for documents matching both these queries.
<details>
    <summary>Solution</summary>

```json
GET multitype/_search
{
  "query": {
    "bool": {
      "must": [
        {"match": {
          "phrase": "Beethoven"
        }},
        {
          "match": {
            "ip": "127.0.0.0/31"
          }
        }
      ]
    }
  }
}

```
</details>

Before the next step, we will add a couple documents to our index :
<details>
    <summary>Execute before continuing</summary>

```json
POST _bulk
{"index":{"_index":"multitype"}}
{"id": "Beethoven", "phrase": "Lorem ipsum"}
{"index":{"_index":"multitype"}}
{"phrase": "Beethoven est génial", "id": "Beethoven"}
```
</details>


Now, we will search for documents containing `"Beethoven"` in either the `french` or the `id` fields.
<details>
    <summary>Solutions</summary>

Using [Multi-match](https://www.elastic.co/guide/en/elasticsearch/reference/current/query-dsl-multi-match-query.html)
```json
GET multitype/_search
{
  "query": {
    "multi_match": {
      "query": "Beethoven",
      "fields": ["id", "french"]
    }
  }
}
```
</details>

<details>
    <summary>Solution</summary>

Using [bool](https://www.elastic.co/guide/en/elasticsearch/reference/current/query-dsl-bool-query.html)
```json
GET multitype/_search
{
  "query": {
    "bool": {
      "should": [
        {"match": {
          "id": "Beethoven"
        }},
        {"match": {
          "french": "Beethoven"
        }}
      ]
    }
  }
}
```
</details>



### Write and execute a search query that is a Boolean combination of multiple queries and filters
REQUIRED SETUP:
 - the cluster has no index names `notes`
 - run the following query to index documents in index `notes`.


<details>
    <summary>Bulk into notes</summary>

```json
POST notes/_bulk
{"index":{"_index":"notes"}}
{"matière": "Maths", "note": 14, "id": "35"}
{"index":{"_index":"notes"}}
{"matière": "Maths", "note": 13, "id": "14"}
{"index":{"_index":"notes"}}
{"matière": "Maths", "note": 17, "id": "7"}
{"index":{"_index":"notes"}}
{"matière": "Français", "note": 12, "id": "34"}
{"index":{"_index":"notes"}}
{"matière": "Français", "note": 9, "id": "35"}
{"index":{"_index":"notes"}}
{"matière": "Français", "note": 17, "id": "9"}
{"index":{"_index":"notes"}}
{"matière": "Maths", "note": 18, "id": "4"}
{"index":{"_index":"notes"}}
{"matière": "Maths", "note": 18, "id": "4"}
```
</details>

Now we'll try to search for whatever documents that scored above 15, and rank Maths notes higher because they have a bigger weight.

<details>
    <summary>Solution</summary>

```json
GET notes/_search
{
  "query": {
    "bool": {
      "must": [
        {
          "range": {
            "note": {
              "gte": 15
            }
          }
        }
      ],
      "should": [
        {
          "term": {
            "matière.keyword": {
              "value": "Maths"
            }
          }
        }
      ]
    }
  }
}
```
</details>

### Write an asynchronous search

[documentation](https://www.elastic.co/guide/en/elasticsearch/reference/current/async-search.html)

<details>
    <summary>Solution</summary>

You simply need to change the endpoint, as such :

```json
POST multitype/_async_search
{
  "query": {
    "match_all": {}
  }
}
```
</details>

### Write and execute metric and bucket aggregations
REQUIRED SETUP:
 - the cluster has an index named `notes` that matches the one required for the boolean exercise

[terms aggregation](https://www.elastic.co/guide/en/elasticsearch/reference/current/search-aggregations-bucket-terms-aggregation.html)
[average aggregation](https://www.elastic.co/guide/en/elasticsearch/reference/current/search-aggregations-metrics-avg-aggregation.html)

Now, let's suppose we want to know the average grade. How'd you do that ?

<details>
    <summary>Result</summary>

If you have indexed no extra document, you should have 14.5.
</details>

<details>
    <summary>Solution</summary>

```json
GET notes/_search
{
  "size": 0, 
  "aggs": {
    "NAME": {
      "avg": {
        "field": "note"
      }
    }
  }
}
```
</details>

Now, we want to know the average grade in maths only.

<details>
    <summary>Result</summary>

If you have indexed no extra document, you should have 15.5 this time !
</details>
<details>
    <summary>Solution</summary>

```json
GET notes/_search
{
  "query": {
    "match": {
      "matière.keyword": "Maths"
    }
  }, 
  "size": 0, 
  "aggs": {
    "NAME": {
      "avg": {
        "field": "note"
      }
    }
  }
}

```
</details>

Finally, we want to know how many grades we have for each subject (matière).

<details>
    <summary>Result</summary>

We have 4 grades for "Maths", 3 for "Français and one for "Anglais.
</details>

<details>
    <summary>Solution</summary>

```json
GET notes/_search
{
  "aggs": {
    "NAME": {
      "terms": {
        "field": "matière.keyword",
        "size": 10
      }
    }
  }
}

```
</details>

### Write and execute aggregations that contain sub-aggregations
REQUIRED SETUP:
 - the cluster has an index named `notes` that matches the one required for the boolean exercise

[sub-aggregations](https://www.elastic.co/guide/en/elasticsearch/reference/current/search-aggregations.html#run-sub-aggs)

Now, we want to now the average grade for each subject in a single query.

<details>
    <summary>Result</summary>

If you have indexed no extra documents, your averages should be : 15.5 for Maths, 12.6 for Français & 18 for Anglais.
</details>

<details>
    <summary>Solution</summary>

```json
GET notes/_search
{
  "size": 0, 
  "aggs": {
    "subjects": {
      "terms": {
        "field": "matière.keyword",
        "size": 10
      },
      "aggs": {
        "subject_avg": {
          "avg": {
            "field": "note"
          }
        }
      }
    }
  }
}

```
</details>

### Write and execute a query that searches across multiple clusters
REQUIRED SETUP:
 - WIP

[cross cluster search](https://www.elastic.co/guide/en/elasticsearch/reference/current/modules-cross-cluster-search.html)

## <a id="search_application">Developing Search Applications</a>
### Highlight the search terms in the response of a query
REQUIRED SETUP:
 - an index named `multitype` with previously indexed documents exists in the cluster

[Highlighting](https://www.elastic.co/guide/en/elasticsearch/reference/current/highlighting.html)

Let's search for `Beethoven` in the `french` field, and highlight the results.

<details>
    <summary>Solution</summary>

```json
GET multitype/_search
{
  "query": {
    "match": {
      "french": "Beethoven"
    }
  },
  "highlight": {
    "fields": {
      "french": {}
    }
  }
}
```
</details>


### Sort the results of a query by a given set of requirements
REQUIRED SETUP:
 - the index `notes` created in the boolean exercise

[sort search results](https://www.elastic.co/guide/en/elasticsearch/reference/current/sort-search-results.html)

Let's search for every document in the `notes` index, but sort these by note without using `_score`s at all.

<details>
    <summary>Solution</summary>

```json
GET notes/_search
{
  "query": {
    "match_all": {}
  },
  "sort": [
    {
      "note": {
        "order": "desc"
      }
    }
  ]
}

```
</details>
As seen in the documentation, sorts can be much, much more complex than this.

### Implement pagination of the results of a search query
### Define and use index aliases
REQUIRED SETUP:
 - a running Elasticsearch cluster with at least one node and a Kibana instance,
 - the cluster has no index with name `hamlet`, 
 - the cluster has no template that applies to indices starting by `hamlet`

#### Create the indices `hamlet-1` and `hamlet-2`, each with two primary shards and no replicas, then, add some documents by running the following commands
<details>
    <summary>Add documents to hamlet-1</summary>

```json
PUT hamlet-1/_doc/_bulk
{"index":{"_index":"hamlet-1","_id":0}}
{"line_number":"1.1.1","speaker":"BERNARDO","text_entry":"Whos there?"}
{"index":{"_index":"hamlet-1","_id":1}}
{"line_number":"1.1.2","speaker":"FRANCISCO","text_entry":"Nay, answer me: stand, and unfold yourself."}
{"index":{"_index":"hamlet-1","_id":2}}
{"line_number":"1.1.3","speaker":"BERNARDO","text_entry":"Long live the king!"}
{"index":{"_index":"hamlet-1","_id":3}}
{"line_number":"1.2.1","speaker":"KING CLAUDIUS","text_entry":"Though yet of Hamlet our dear brothers death"}
```
</details>
<details>
    <summary>Add documents to hamlet-2</summary>

```json
PUT hamlet-2/_doc/_bulk
{"index":{"_index":"hamlet-2","_id":4}}
{"line_number":"2.1.1","speaker":"LORD POLONIUS","text_entry":"Give him this money and these notes, Reynaldo."}
{"index":{"_index":"hamlet-2","_id":5}}
{"line_number":"2.1.2","speaker":"REYNALDO","text_entry":"I will, my lord."}
{"index":{"_index":"hamlet-2","_id":6}}
{"line_number":"2.1.3","speaker":"LORD POLONIUS","text_entry":"You shall do marvellous wisely, good Reynaldo,"}
{"index":{"_index":"hamlet-2","_id":7}}
{"line_number":"2.1.4","speaker":"LORD POLONIUS","text_entry":"Before you visit him, to make inquire"}
```
</details>

If you do not know how to create an index with custom settings, please read [this section](#create_index_with_settings) of the guide first.

#### Create the alias `hamlet` that maps both `hamlet-1` and `hamlet-2` and verify that the documents grouped by `hamlet` are 8
[Alias API](https://www.elastic.co/guide/en/elasticsearch/reference/7.15/indices-aliases.html#aliases-write-index)
<details>
    <summary>Alias creation</summary>

```json
POST _aliases
{
  "actions": [
    {
      "add": {
        "index": "hamlet*",
        "alias": "hamlet"
      }
    }
  ]
}
```
</details>

Querying against an alias is just like querying against an indice. If you do not know how to do that, refer to [Searching Data](#searching_data).

#### Configure `hamlet-1` to be the write index of the `hamlet` alias, then use the alias to index a document

<details>
    <summary>Update the alias</summary>

```json
POST _aliases
{
  "actions": [
    {
      "add": {
        "index": "hamlet-1",
        "alias": "hamlet",
        "is_write_index": true
      }
    },
    {
      "add": {
        "index": "hamlet-2",
        "alias": "hamlet"
      }
    }
  ]
}
```
</details>

<details>
    <summary>Execute this, if your alias is properly configured it will work !</summary>

```json
POST hamlet/_doc/8
{
  "text_entry": "With turbulent and dangerous lunacy?",
  "line_number": "3.1.4",
  "speaker": "KING CLAUDIUS"
}
```
</details>



### Define and use a search template

## <a id="data_processing">Data Processing</a>
### Define a mapping that satisfies a given set of requirements
### Define and use a custom analyzer that satisfies a given set of requirements
### Define and use multi-fields with different data types and/or analyzers
### Use the Reindex API and Update By Query API to reindex and/or update documents
#### Update the document with id "1" by adding a field named `line_number` with value "3.1.64"
<details>
    <summary>Solution</summary>

```json
POST hamlet-raw/_doc/1
{
  "line": "To be, or not to be: that is the question",
  "line_number": "3.1.66"
}
```
`POST hamlet-raw/_update/1` wont work because of the new field, it needs to be reindexed.
</details>


#### Update the last document by setting the value of `line_number` to "3.1.65"
<details>
    <summary>Solution</summary>

```json
GET hamlet-raw/_search
POST hamlet-raw/_doc/<copy_pasted_id>/_update
{
  "doc": {
    "line_number": "3.1.65"
  }
}
```
</details>


#### In one request, update all documents in `hamlet-raw` by adding a new field named `speaker` with value `"Hamlet"`
<details>
    <summary>Solution</summary>

```json
POST hamlet-raw/_update_by_query?conflicts=proceed
{
  "script": {
    "source": "ctx._source.speaker = 'Hamlet'",
    "lang": "painless"
  }
}
```
</details>

#### Update the document with id `1` by renaming the field `line` into `text_entry`
<details>
    <summary>Solution</summary>

```json
POST hamlet-raw/_doc/1/_update
{
  "script": {
    "source": "ctx._source.text_entry = ctx._source.speaker; ctx._source.remove('line')",
    "lang": "painless"
  }
}
```
</details>

#### Create a script named `set_is_hamlet` and save it into the cluster state. The script (i) adds a field named `is_hamlet` to each document, (ii) sets the field to `true` if the document has `speaker` equals to "HAMLET", (iii) sets the field to `false` otherwise. Then, update all documents in `hamlet` by running the `set_is_hamlet` script
Run the following command to index documents in `hamlet` :
<details>
    <summary>Bulk command</summary>

```json
PUT hamlet/_doc/_bulk
{"index":{"_index":"hamlet","_id":0}}
{"line_number":"1.1.1","speaker":"BERNARDO","text_entry":"Whos there?"}
{"index":{"_index":"hamlet","_id":1}}
{"line_number":"1.1.2","speaker":"FRANCISCO","text_entry":"Nay, answer me: stand, and unfold yourself."}
{"index":{"_index":"hamlet","_id":2}}
{"line_number":"1.1.3","speaker":"BERNARDO","text_entry":"Long live the king!"}
{"index":{"_index":"hamlet","_id":3}}
{"line_number":"1.2.1","speaker":"KING CLAUDIUS","text_entry":"Though yet of Hamlet our dear brothers death"}
{"index":{"_index":"hamlet","_id":4}}
{"line_number":"1.2.2","speaker":"KING CLAUDIUS","text_entry":"The memory be green, and that it us befitted"}
{"index":{"_index":"hamlet","_id":5}}
{"line_number":"1.3.1","speaker":"LAERTES","text_entry":"My necessaries are embarkd: farewell:"}
{"index":{"_index":"hamlet","_id":6}}
{"line_number":"1.3.4","speaker":"LAERTES","text_entry":"But let me hear from you."}
{"index":{"_index":"hamlet","_id":7}}
{"line_number":"1.3.5","speaker":"OPHELIA","text_entry":"Do you doubt that?"}
{"index":{"_index":"hamlet","_id":8}}
{"line_number":"1.4.1","speaker":"HAMLET","text_entry":"The air bites shrewdly; it is very cold."}
{"index":{"_index":"hamlet","_id":9}}
{"line_number":"1.4.2","speaker":"HORATIO","text_entry":"It is a nipping and an eager air."}
{"index":{"_index":"hamlet","_id":10}}
{"line_number":"1.4.3","speaker":"HAMLET","text_entry":"What hour now?"}
{"index":{"_index":"hamlet","_id":11}}
{"line_number":"1.5.2","speaker":"Ghost","text_entry":"Mark me."}
{"index":{"_index":"hamlet","_id":12}}
{"line_number":"1.5.3","speaker":"HAMLET","text_entry":"I will."}

```
</details>
I'll let you struggle around. If you give up or want some help, here are the solutions :
<details>
    <summary>Script creation</summary>

```json
POST _scripts/set_is_hamlet
{
  "script": {
    "lang": "painless",
    "source": "if (ctx._source.speaker == 'HAMLET') {ctx._source.is_hamlet = true} else {ctx._source.is_hamlet = false}"
  }
}
```
</details>

<details>
    <summary>Use script</summary>

```json
POST hamlet/_update_by_query?conflicts=proceed
{
  "script": {
    "id": "set_is_hamlet"
  }
}
```
</details>

### Define and use an ingest pipeline that satisfies a given set of requirements, including the use of Painless to modify documents
### Configure an index so that it properly maintains the relationships of nested arrays of objects

## <a id="cluster_management">Cluster Management</a>
### Diagnose shard issues and repair a cluster's health
### Backup and restore a cluster and/or specific indices
### Configure a snapshot to be searchable
### Configure a cluster for cross-cluster search
### Implement cross-cluster replication
### Define role-based access control using Elasticsearch Security

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

# <a id="practical_guide">Practical Guide</a>

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

# **Exam Objectives**
## Data Management
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

### Use the Data Visualizer to upload a text file into Elasticsearch
### Define and use an index template for a given pattern that satisfies a given set of requirements
#### Create the index template `hamlet_template`, so that the template (i) matches any index that starts by "hamlet_" or "hamlet-", (ii) allocates one primary shard and no replicas for each matching index 
REQUIRED SETUP:
 -   a running Elasticsearch cluster with at least one node and a Kibana instance,
 -  the cluster has no index with name `hamlet`, 
 - the cluster has no template that applies to indices starting by `hamlet`
 
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

### Define and use a dynamic template that satisfies a given set of requirements
### Define an Index Lifecycle Management policy for a time-series index
### Define an index template that creates a new data stream

## <a id="searching_data">Searching Data</a>
### Write and execute a search query for terms and/or phrases in one or more fields of an index
### Write and execute a search query that is a Boolean combination of multiple queries and filters
### Write an asynchronous search
### Write and execute metric and bucket aggregations
### Write and execute aggregations that contain sub-aggregations
### Write and execute a query that searches across multiple clusters

## Developing Search Applications
### Highlight the search terms in the response of a query
### Sort the results of a query by a given set of requirements
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

## Data Processing
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

## Cluster Management
### Diagnose shard issues and repair a cluster's health
### Backup and restore a cluster and/or specific indices
### Configure a snapshot to be searchable
### Configure a cluster for cross-cluster search
### Implement cross-cluster replication
### Define role-based access control using Elasticsearch Security

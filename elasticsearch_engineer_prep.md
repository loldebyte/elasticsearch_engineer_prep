# General Tips

Tous les examples de codes sont prévus dans le cadre de la console `Dev Tools` de kibana.

Pour des détails sur l'environement de test : cf ce [webinaire](https://www.youtube.com/watch?v=9UpB-s_ZfNE),
qui contient également des examples de questions de l'exam.

La documentation officielle EST DISPONIBLE PENDANT L'EXAM ! C'est pourquoi il est nécéssaire de se familiariser avec la documentation **DE LA VERSION SUR LAQUELLE PORTE L'EXAM**, parce que certaines pages peuvent changer entre les versions.

# Exercices génériques

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
TODO


# Exam Objectives
## Data Management
### Define an index that satisfies a given set of requirements
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
### Define and use a dynamic template that satisfies a given set of requirements
### Define an Index Lifecycle Management policy for a time-series index
### Define an index template that creates a new data stream

## Searching Data
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

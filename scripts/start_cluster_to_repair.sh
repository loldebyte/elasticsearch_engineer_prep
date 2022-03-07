#! /bin/bash -e

cd "$(dirname $0)"/..

# if the docker-compose is interupted, wipe clean all containers
# trap "docker-compose -f .docker-compose.repair_cluster_health.yml down -v --remove-orphans" 0

docker-compose -f .docker-compose.repair_cluster_health.yml up &

sleep 5

while read -r line; do
   grep -q "Kibana is now available (was degraded)" && break || true  # || true required because of -e
done < <(docker logs brokenkibana -f)

curl -o /dev/null -sX PUT "localhost:9200/my-index-000001?pretty" -H 'Content-Type: application/json' -d'
{
  "settings": {
    "index": {
      "number_of_shards": 6,
      "number_of_replicas": 0,
      "routing.allocation.total_shards_per_node": 3
    }
  }
}
'

curl -o /dev/null -sX PUT "localhost:9200/my-index-000002?pretty" -H 'Content-Type: application/json' -d'
{
  "settings": {
    "index": {
      "number_of_shards": 6,
      "number_of_replicas": 2,
      "routing.allocation.total_shards_per_node": 3
    }
  }
}
'

curl -o /dev/null -sX PUT "localhost:9200/my-index-000003?pretty" -H 'Content-Type: application/json' -d'
{
  "settings": {
    "index": {
      "number_of_shards": 2,
      "number_of_replicas": 0,
      "routing.allocation.total_shards_per_node": 3
    }
  }
}
'

curl -o /dev/null -sX PUT "localhost:9200/my-index-000004?pretty" -H 'Content-Type: application/json' -d'
{
  "settings": {
    "index": {
      "number_of_shards": 6,
      "number_of_replicas": 3,
      "routing.allocation.total_shards_per_node": 3
    }
  }
}
'

curl -o /dev/null -sX PUT "localhost:9200/my-index-000005?pretty" -H 'Content-Type: application/json' -d'
{
  "settings": {
    "index": {
      "number_of_shards": 10,
      "number_of_replicas": 0,
      "routing.allocation.total_shards_per_node": 3
    }
  }
}
'

curl -o /dev/null -sX PUT "localhost:9200/my-index-000006?pretty" -H 'Content-Type: application/json' -d'
{
  "settings": {
    "index": {
      "number_of_shards": 7,
      "number_of_replicas": 1,
      "routing.allocation.total_shards_per_node": 3
    }
  }
}
'

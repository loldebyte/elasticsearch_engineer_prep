FROM elasticsearch:7.17.1

RUN mkdir /usr/share/elasticsearch/snapshots
RUN chown -R elasticsearch /usr/share/elasticsearch/snapshots

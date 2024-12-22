#!/bin/bash

set -x

DT=$(date +'%Y-%m-%d')
gsutil rm -r gs://reflect-events/export-$DT || true
gcloud firestore export gs://reflect-events/export-$DT --collection-ids=events

bq load --replace --source_format=DATASTORE_BACKUP reflect_events.events gs://reflect-events/export-$DT/all_namespaces/kind_events/all_namespaces_kind_events.export_metadata

bq extract --destination_format NEWLINE_DELIMITED_JSON 'reflect_events.events' gs://reflect-events/results.json

gcloud storage cp -r gs://reflect-events/results.json results.json

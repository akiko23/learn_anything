#!/bin/bash

docker run \
  --name pgsql-test \
  -e POSTGRES_USER=test \
  -e POSTGRES_PASSWORD=test  \
  -e POSTGRES_DB=test \
  -p 5433:5432 \
  -d postgres:16.0-alpine3.18


docker run \
  --name rabbitmq-test \
  -e RABBITMQ_DEFAULT_USER=test \
  -e RABBITMQ_DEFAULT_PASS=test  \
  -p 5673:5672 \
  -p 15673:15672 \
  -d rabbitmq:3.13.7-management

docker run \
  --name redis-test \
  --volume "/etc/learn_anything/redis/config:/usr/local/etc/redis" \
  -p 6380:6379 \
  -d redis:7.2.4-alpine \


docker run \
  --name s3-test \
  -p 9001:9000 \
  -p 9091:9090 \
  -v /etc/learn_anything/test/minio/data:/data \
  -d minio/minio:latest \
  server /data --console-address ":9090"

sleep 10

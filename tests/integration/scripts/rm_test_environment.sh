#!/bin/bash

docker rm -f pgsql-test
docker rm -f rabbitmq-test
docker rm -f redis-test
docker rm -f s3-test
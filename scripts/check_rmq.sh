#!/bin/bash

if [[ ! -n $(docker ps | grep learn_anything-rabbitmq) ]]; then
	docker start learn_anything-rabbitmq
else
	echo 'Rmq is running!'
fi

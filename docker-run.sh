#!/bin/bash

docker stop rmu-api-attack

docker rm rmu-api-attack

docker rmi labcabrera/rmu-api-attack:latest

docker build -t labcabrera/rmu-api-attack:latest .

docker run -d -p 8000:8000 --network rmu-network --name rmu-api-attack -h rmu-api-attack \
  -e RMU_MONGO_ATTACK_URI='mongodb://admin:admin@rmu-mongo:27017/rmu-attack?authSource=admin' \
  -e PORT='8000' \
  labcabrera/rmu-api-attack:latest

docker logs -f rmu-api-attack
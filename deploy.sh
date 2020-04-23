#!/usr/bin/env bash

vol_name=mongo_test
container_name=mongo_db_test

# Creacion del volumen para compatir datos
docker volume create $vol_name
sleep 2
# Creacion del contenedor
docker run --name $container_name -p 27017:27017 --rm -v $vol_name:/data/db -d mongo

printf "\n## The container $container_name has been created, check it with: docker ps -a | grep $container_name \n"
sleep 2
printf "\n## All Python dependencies will be installed \n"
sleep 1
pipenv install
printf "USERNAME_IG=\nPASSWORD_IG=" >> .env
printf "\n## All python dependencies has been installed, now you can run the script with this command: pipenv run python index.py \n"

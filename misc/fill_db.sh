#!/bin/bash

trap 'kill $(jobs -p)' EXIT SIGINT SIGTERM

#pkill -f mongod
#rm -rf db
#mkdir -p db
#mongod --quiet --dbpath db &

sleep 5
echo 
mongoimport -d munerator -c gamemaps --file misc/gamemaps.json
mongoimport -d munerator -c players --file misc/players.json

echo
munerator trans &
munerator context &
munerator store &

jobs
sleep 3

#munerator wrap 'tail -n 100000 misc/openarena.log'&
munerator wrap 'tail -n 40000 misc/games.log'

echo done

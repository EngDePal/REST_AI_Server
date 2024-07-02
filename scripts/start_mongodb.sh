#!/bin/bash
# Start MongoDB
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
"$DIR/../mongodb/macos/bin/mongod" --dbpath "$DIR/../data" --logpath "$DIR/../logs/mongodb.log" --fork
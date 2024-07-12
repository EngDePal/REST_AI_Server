#!/bin/bash
# Stop MongoDB
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
MONGOD_PID=$(pgrep -f "$DIR/../mongodb/macos/bin/mongod")
if [ -n "$MONGOD_PID" ]; then
  kill $MONGOD_PID
  echo "MongoDB server stopped"
else
  echo "MongoDB server not running"
fi
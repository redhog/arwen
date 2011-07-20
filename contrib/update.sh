#! /bin/bash

ROOT="$(cd "$(dirname $0)/.."; pwd)"

git pull origin master

mkdir -p "$ROOT/libs"
cd "$ROOT/libs"
while read giturl; do
  name="$(basename "$giturl" .git)"
  echo "Updating dependency $name..."
  if [ -e "$name" ]; then
    (cd "$name"; git pull origin master; )
  else
    git clone "$giturl"
  fi
done < "$ROOT/.dependencies"

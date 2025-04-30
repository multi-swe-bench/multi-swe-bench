#!/bin/bash
set -e

cd /home/jackson-databind
git reset --hard
bash /home/check_git_changes.sh
git checkout 23551ecf0240486c87af36b00a41f8eebf51ecfd
bash /home/check_git_changes.sh

file="/home/jackson-databind/pom.xml"
old_version="2.16.2-SNAPSHOT"
new_version="2.16.3-SNAPSHOT"
sed -i "s/$old_version/$new_version/g" "$file"

mvn clean test -Dmaven.test.skip=false -DfailIfNoTests=false || true

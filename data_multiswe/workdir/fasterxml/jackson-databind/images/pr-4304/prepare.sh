#!/bin/bash
set -e

cd /home/jackson-databind
git reset --hard
bash /home/check_git_changes.sh
git checkout 56356fe15bec52f18f0c05b59aa0aafa9ee8e8bf
bash /home/check_git_changes.sh

file="/home/jackson-databind/pom.xml"
old_version="2.15.4-SNAPSHOT"
new_version="2.15.5-SNAPSHOT"
sed -i "s/$old_version/$new_version/g" "$file"

mvn clean test -Dmaven.test.skip=false -DfailIfNoTests=false || true

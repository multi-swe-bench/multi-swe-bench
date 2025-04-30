#!/bin/bash
set -e

cd /home/jackson-databind
git reset --hard
bash /home/check_git_changes.sh
git checkout 5d4eb514820a7cfc7135e4b515dd9531ebdd523a
bash /home/check_git_changes.sh

file="/home/jackson-databind/pom.xml"
old_version="2.15.0-rc2-SNAPSHOT"
new_version="2.15.5-SNAPSHOT"
sed -i "s/$old_version/$new_version/g" "$file"

mvn clean test -Dmaven.test.skip=false -DfailIfNoTests=false || true

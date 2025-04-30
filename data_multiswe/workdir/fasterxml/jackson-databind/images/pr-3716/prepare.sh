#!/bin/bash
set -e

cd /home/jackson-databind
git reset --hard
bash /home/check_git_changes.sh
git checkout 0020fcbe578f40810f8e6dea1c89ad48f5e70c15
bash /home/check_git_changes.sh

file="/home/jackson-databind/pom.xml"
old_version="2.14.2-SNAPSHOT"
new_version="2.14.4-SNAPSHOT"
sed -i "s/$old_version/$new_version/g" "$file"

mvn clean test -Dmaven.test.skip=false -DfailIfNoTests=false || true

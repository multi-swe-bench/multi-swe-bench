#!/bin/bash
set -e

cd /home/jackson-core
git reset --hard
bash /home/check_git_changes.sh
git checkout d14acac9536939886e432d7145670a9210f54699
bash /home/check_git_changes.sh

file="/home/jackson-core/pom.xml"
old_version="2.17.0-SNAPSHOT"
new_version="2.17.4-SNAPSHOT"
sed -i "s/$old_version/$new_version/g" "$file"

mvn clean test -Dmaven.test.skip=false -DfailIfNoTests=false || true

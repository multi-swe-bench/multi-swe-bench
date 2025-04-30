#!/bin/bash
set -e

cd /home/jackson-databind
git reset --hard
bash /home/check_git_changes.sh
git checkout 7690a33de90f0c24f21fdac071f7cc0c5a94b825
bash /home/check_git_changes.sh

file="/home/jackson-databind/pom.xml"
old_version="2.13.5-SNAPSHOT"
new_version="2.13.6-SNAPSHOT"
sed -i "s/$old_version/$new_version/g" "$file"

mvn clean test -Dmaven.test.skip=false -DfailIfNoTests=false || true

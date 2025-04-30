#!/bin/bash
set -e

cd /home/jackson-dataformat-xml
git reset --hard
bash /home/check_git_changes.sh
git checkout b782f4b9559ece1b6178cbeafa8acffb0ab9d0f0
bash /home/check_git_changes.sh

file="/home/jackson-dataformat-xml/pom.xml"
old_version="2.17.0-SNAPSHOT"
new_version="2.17.4-SNAPSHOT"
sed -i "s/$old_version/$new_version/g" "$file"

mvn clean test -Dmaven.test.skip=false -DfailIfNoTests=false || true

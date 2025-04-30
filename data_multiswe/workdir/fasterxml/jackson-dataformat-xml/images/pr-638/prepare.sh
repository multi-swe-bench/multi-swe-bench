#!/bin/bash
set -e

cd /home/jackson-dataformat-xml
git reset --hard
bash /home/check_git_changes.sh
git checkout ac00d648e9b424f4b6c4d7aaaa23abf50adc1b5a
bash /home/check_git_changes.sh

file="/home/jackson-dataformat-xml/pom.xml"
old_version="2.17.0-SNAPSHOT"
new_version="2.17.4-SNAPSHOT"
sed -i "s/$old_version/$new_version/g" "$file"

mvn clean test -Dmaven.test.skip=false -DfailIfNoTests=false || true

#!/bin/bash
set -e

cd /home/jackson-databind
git reset --hard
bash /home/check_git_changes.sh
git checkout ef6564c5cf03144ad9689b1444d3654c6f18eb15
bash /home/check_git_changes.sh

file="/home/jackson-databind/pom.xml"
old_version="2.14.0-SNAPSHOT"
new_version="2.14.4-SNAPSHOT"
sed -i "s/$old_version/$new_version/g" "$file"

mvn clean test -Dmaven.test.skip=false -DfailIfNoTests=false || true

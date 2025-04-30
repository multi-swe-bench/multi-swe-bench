#!/bin/bash
set -e

cd /home/jackson-databind
git reset --hard
bash /home/check_git_changes.sh
git checkout 6b738ac6540556ede1cc0d4ea8e268ab7094918f
bash /home/check_git_changes.sh

file="/home/jackson-databind/pom.xml"
old_version="2.16.2-SNAPSHOT"
new_version="2.16.3-SNAPSHOT"
sed -i "s/$old_version/$new_version/g" "$file"

mvn clean test -Dmaven.test.skip=false -DfailIfNoTests=false || true

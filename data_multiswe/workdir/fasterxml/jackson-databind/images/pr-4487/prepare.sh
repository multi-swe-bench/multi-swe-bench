#!/bin/bash
set -e

cd /home/jackson-databind
git reset --hard
bash /home/check_git_changes.sh
git checkout a479197ec08b50dfe01521c95d9d9edcef228395
bash /home/check_git_changes.sh

file="/home/jackson-databind/pom.xml"
old_version="2.18.0-SNAPSHOT"
new_version="2.18.4-SNAPSHOT"
sed -i "s/$old_version/$new_version/g" "$file"

mvn clean test -Dmaven.test.skip=false -DfailIfNoTests=false || true

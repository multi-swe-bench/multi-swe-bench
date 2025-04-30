#!/bin/bash
set -e

cd /home/jackson-databind
git reset --hard
bash /home/check_git_changes.sh
git checkout 866f95fc0198a5b8beb4f25976125697b115e236
bash /home/check_git_changes.sh

file="/home/jackson-databind/pom.xml"
old_version="2.15.4-SNAPSHOT"
new_version="2.15.5-SNAPSHOT"
sed -i "s/$old_version/$new_version/g" "$file"

mvn clean test -Dmaven.test.skip=false -DfailIfNoTests=false || true

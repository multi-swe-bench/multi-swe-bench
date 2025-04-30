#!/bin/bash
set -e

cd /home/jackson-databind
git reset --hard
bash /home/check_git_changes.sh
git checkout c6fd21152af31357f68de2d6344e99b4aab36d7c
bash /home/check_git_changes.sh

file="/home/jackson-databind/pom.xml"
old_version="2.16.1-SNAPSHOT"
new_version="2.16.3-SNAPSHOT"
sed -i "s/$old_version/$new_version/g" "$file"

mvn clean test -Dmaven.test.skip=false -DfailIfNoTests=false || true

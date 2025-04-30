#!/bin/bash
set -e

cd /home/jackson-databind
git reset --hard
bash /home/check_git_changes.sh
git checkout f6d2f949c96ed378202c462ebdbaa9ae26a1ec4a
bash /home/check_git_changes.sh

file="/home/jackson-databind/pom.xml"
old_version="2.17.0-SNAPSHOT"
new_version="2.17.4-SNAPSHOT"
sed -i "s/$old_version/$new_version/g" "$file"

mvn clean test -Dmaven.test.skip=false -DfailIfNoTests=false || true

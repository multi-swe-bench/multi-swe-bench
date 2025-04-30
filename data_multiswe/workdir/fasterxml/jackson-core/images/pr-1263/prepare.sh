#!/bin/bash
set -e

cd /home/jackson-core
git reset --hard
bash /home/check_git_changes.sh
git checkout 9ed17fc7e9df9203f11ccb17819009ab0a898aa3
bash /home/check_git_changes.sh

file="/home/jackson-core/pom.xml"
old_version="2.18.0-SNAPSHOT"
new_version="2.18.4-SNAPSHOT"
sed -i "s/$old_version/$new_version/g" "$file"

mvn clean test -Dmaven.test.skip=false -DfailIfNoTests=false || true

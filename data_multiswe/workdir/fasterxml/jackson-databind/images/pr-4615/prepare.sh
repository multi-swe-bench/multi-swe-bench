#!/bin/bash
set -e

cd /home/jackson-databind
git reset --hard
bash /home/check_git_changes.sh
git checkout bed90645e269d30b0b94d446f821a3a0f45ce07b
bash /home/check_git_changes.sh

file="/home/jackson-databind/pom.xml"
old_version="2.18.0-SNAPSHOT"
new_version="2.18.4-SNAPSHOT"
sed -i "s/$old_version/$new_version/g" "$file"

mvn clean test -Dmaven.test.skip=false -DfailIfNoTests=false || true

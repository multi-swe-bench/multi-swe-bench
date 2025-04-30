#!/bin/bash
set -e

cd /home/jackson-databind
git reset --hard
bash /home/check_git_changes.sh
git checkout cc6a1ae3a01a5e68387338a3d25c7ba5aa0f30b9
bash /home/check_git_changes.sh

file="/home/jackson-databind/pom.xml"
old_version="2.16.2-SNAPSHOT"
new_version="2.16.3-SNAPSHOT"
sed -i "s/$old_version/$new_version/g" "$file"

mvn clean test -Dmaven.test.skip=false -DfailIfNoTests=false || true

#!/bin/bash
set -e

cd /home/jackson-databind
git reset --hard
bash /home/check_git_changes.sh
git checkout e71e1a227e796abd8a55e8135044133667d6555e
bash /home/check_git_changes.sh

file="/home/jackson-databind/pom.xml"
old_version="2.17.1-SNAPSHOT"
new_version="2.17.4-SNAPSHOT"
sed -i "s/$old_version/$new_version/g" "$file"

mvn clean test -Dmaven.test.skip=false -DfailIfNoTests=false || true

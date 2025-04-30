#!/bin/bash
set -e

cd /home/jackson-core
git reset --hard
bash /home/check_git_changes.sh
git checkout 287ec3223b039f24d2db99809ae04a333b287435
bash /home/check_git_changes.sh

file="/home/jackson-core/pom.xml"
old_version="2.15.0-SNAPSHOT"
new_version="2.15.5-SNAPSHOT"
sed -i "s/$old_version/$new_version/g" "$file"

mvn clean test -Dmaven.test.skip=false -DfailIfNoTests=false || true

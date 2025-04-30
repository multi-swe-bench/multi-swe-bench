#!/bin/bash
set -e

cd /home/jackson-databind
git reset --hard
bash /home/check_git_changes.sh
git checkout 5e94cb1b29a5948737d86f5fe7eaeda318b74910
bash /home/check_git_changes.sh

file="/home/jackson-databind/pom.xml"
old_version="2.16.0-SNAPSHOT"
new_version="2.16.3-SNAPSHOT"
sed -i "s/$old_version/$new_version/g" "$file"

mvn clean test -Dmaven.test.skip=false -DfailIfNoTests=false || true

#!/bin/bash
set -e

cd /home/jackson-databind
git reset --hard
bash /home/check_git_changes.sh
git checkout 04daeaba75614f0eec89ec180d3268b1a2f3301d
bash /home/check_git_changes.sh

file="/home/jackson-databind/pom.xml"
old_version="2.16.1-SNAPSHOT"
new_version="2.16.3-SNAPSHOT"
sed -i "s/$old_version/$new_version/g" "$file"

mvn clean test -Dmaven.test.skip=false -DfailIfNoTests=false || true

#!/bin/bash
set -e

cd /home/jackson-core
git reset --hard
bash /home/check_git_changes.sh
git checkout 0de50fbc6e9709d0f814fd6e30b6595905f70e63
bash /home/check_git_changes.sh

file="/home/jackson-core/pom.xml"
old_version="2.15.0-rc3-SNAPSHOT"
new_version="2.15.5-SNAPSHOT"
sed -i "s/$old_version/$new_version/g" "$file"

mvn clean test -Dmaven.test.skip=false -DfailIfNoTests=false || true

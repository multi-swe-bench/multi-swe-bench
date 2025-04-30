#!/bin/bash
set -e

cd /home/jackson-databind
git reset --hard
bash /home/check_git_changes.sh
git checkout b332a4268d25d69ac4603e008d90701cd62d6e4c
bash /home/check_git_changes.sh

file="/home/jackson-databind/pom.xml"
old_version="2.16.0-SNAPSHOT"
new_version="2.16.3-SNAPSHOT"
sed -i "s/$old_version/$new_version/g" "$file"

mvn clean test -Dmaven.test.skip=false -DfailIfNoTests=false || true

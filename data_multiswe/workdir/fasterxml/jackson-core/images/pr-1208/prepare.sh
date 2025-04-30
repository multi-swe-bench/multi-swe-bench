#!/bin/bash
set -e

cd /home/jackson-core
git reset --hard
bash /home/check_git_changes.sh
git checkout 9438a5ec743342ccd04ae396ce410ef75f08371b
bash /home/check_git_changes.sh

file="/home/jackson-core/pom.xml"
old_version="2.17.0-SNAPSHOT"
new_version="2.17.4-SNAPSHOT"
sed -i "s/$old_version/$new_version/g" "$file"

mvn clean test -Dmaven.test.skip=false -DfailIfNoTests=false || true

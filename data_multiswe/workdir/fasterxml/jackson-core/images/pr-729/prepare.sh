#!/bin/bash
set -e

cd /home/jackson-core
git reset --hard
bash /home/check_git_changes.sh
git checkout 4465e7a383b4ca33f9a011e1444d67d7f58fca1c
bash /home/check_git_changes.sh

file="/home/jackson-core/pom.xml"
old_version="2.14.0-SNAPSHOT"
new_version="2.14.4-SNAPSHOT"
sed -i "s/$old_version/$new_version/g" "$file"

mvn clean test -Dmaven.test.skip=false -DfailIfNoTests=false || true

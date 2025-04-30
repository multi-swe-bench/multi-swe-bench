#!/bin/bash
set -e

cd /home/jackson-databind
git reset --hard
bash /home/check_git_changes.sh
git checkout 960b91c981fed3ea3ce9901e31954b76809ead2f
bash /home/check_git_changes.sh

file="/home/jackson-databind/pom.xml"
old_version="2.14.1-SNAPSHOT"
new_version="2.14.4-SNAPSHOT"
sed -i "s/$old_version/$new_version/g" "$file"

mvn clean test -Dmaven.test.skip=false -DfailIfNoTests=false || true

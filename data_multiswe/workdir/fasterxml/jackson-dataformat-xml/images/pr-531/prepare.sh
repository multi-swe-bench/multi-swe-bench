#!/bin/bash
set -e

cd /home/jackson-dataformat-xml
git reset --hard
bash /home/check_git_changes.sh
git checkout f406e23f5e15efb3d930e826204c06e00a23f8e3
bash /home/check_git_changes.sh

file="/home/jackson-dataformat-xml/pom.xml"
old_version="2.14.0-SNAPSHOT"
new_version="2.14.4-SNAPSHOT"
sed -i "s/$old_version/$new_version/g" "$file"

mvn clean test -Dmaven.test.skip=false -DfailIfNoTests=false || true

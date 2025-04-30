#!/bin/bash
set -e

cd /home/jackson-dataformat-xml
git reset --hard
bash /home/check_git_changes.sh
git checkout 6c03760102474a0e38f0f52cdaef2a88e7133598
bash /home/check_git_changes.sh

file="/home/jackson-dataformat-xml/pom.xml"
old_version="2.14.0-SNAPSHOT"
new_version="2.14.4-SNAPSHOT"
sed -i "s/$old_version/$new_version/g" "$file"

mvn clean test -Dmaven.test.skip=false -DfailIfNoTests=false || true

#!/bin/bash
set -e

cd /home/jackson-dataformat-xml
git reset --hard
bash /home/check_git_changes.sh
git checkout a18b8cd98e94660dcac19bd2cd11f376705d7745
bash /home/check_git_changes.sh

file="/home/jackson-dataformat-xml/pom.xml"
old_version="2.15.0-rc3-SNAPSHOT"
new_version="2.15.5-SNAPSHOT"
sed -i "s/$old_version/$new_version/g" "$file"

mvn clean test -Dmaven.test.skip=false -DfailIfNoTests=false || true

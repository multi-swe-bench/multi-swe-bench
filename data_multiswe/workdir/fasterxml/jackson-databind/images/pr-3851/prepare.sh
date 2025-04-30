#!/bin/bash
set -e

cd /home/jackson-databind
git reset --hard
bash /home/check_git_changes.sh
git checkout cf7c15a3ddf8fa6df5c8961cb57e97e12ee9728a
bash /home/check_git_changes.sh

file="/home/jackson-databind/pom.xml"
old_version="2.15.0-rc3-SNAPSHOT"
new_version="2.15.5-SNAPSHOT"
sed -i "s/$old_version/$new_version/g" "$file"

mvn clean test -Dmaven.test.skip=false -DfailIfNoTests=false || true

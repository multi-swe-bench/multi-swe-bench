#!/bin/bash
set -e

cd /home/jackson-core
git reset --hard
bash /home/check_git_changes.sh
git checkout f42556388bb8ad547a55e4ee7cfb52a99f670186
bash /home/check_git_changes.sh

file="/home/jackson-core/pom.xml"
old_version="2.15.0-rc2-SNAPSHOT"
new_version="2.15.5-SNAPSHOT"
sed -i "s/$old_version/$new_version/g" "$file"

mvn clean test -Dmaven.test.skip=false -DfailIfNoTests=false || true

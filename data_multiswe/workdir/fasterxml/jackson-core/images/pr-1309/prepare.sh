#!/bin/bash
set -e

cd /home/jackson-core
git reset --hard
bash /home/check_git_changes.sh
git checkout 449ed86748bf672b0a65f13e7f8573298b543384
bash /home/check_git_changes.sh

file="/home/jackson-core/pom.xml"
old_version="2.17.2-SNAPSHOT"
new_version="2.17.4-SNAPSHOT"
sed -i "s/$old_version/$new_version/g" "$file"

mvn clean test -Dmaven.test.skip=false -DfailIfNoTests=false || true

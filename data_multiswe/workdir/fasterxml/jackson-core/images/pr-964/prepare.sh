#!/bin/bash
set -e

cd /home/jackson-core
git reset --hard
bash /home/check_git_changes.sh
git checkout 2b53cce78c6ca037938e6f26d6935c5f9b8c07dd
bash /home/check_git_changes.sh

file="/home/jackson-core/pom.xml"
old_version="2.15.0-rc2-SNAPSHOT"
new_version="2.15.5-SNAPSHOT"
sed -i "s/$old_version/$new_version/g" "$file"

mvn clean test -Dmaven.test.skip=false -DfailIfNoTests=false || true

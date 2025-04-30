#!/bin/bash
set -e

cd /home/jackson-core
git reset --hard
bash /home/check_git_changes.sh
git checkout 315ac5ad2ad5228129a3df50623570d9bc2d7045
bash /home/check_git_changes.sh

file="/home/jackson-core/pom.xml"
old_version="2.16.0-SNAPSHOT"
new_version="2.16.3-SNAPSHOT"
sed -i "s/$old_version/$new_version/g" "$file"

mvn clean test -Dmaven.test.skip=false -DfailIfNoTests=false || true

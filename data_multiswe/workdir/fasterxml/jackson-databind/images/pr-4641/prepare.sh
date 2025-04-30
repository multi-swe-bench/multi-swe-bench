#!/bin/bash
set -e

cd /home/jackson-databind
git reset --hard
bash /home/check_git_changes.sh
git checkout 3ed7f4572534383e54f9fd0d2521131f64283410
bash /home/check_git_changes.sh

file="/home/jackson-databind/pom.xml"
old_version="2.18.0-SNAPSHOT"
new_version="2.18.4-SNAPSHOT"
sed -i "s/$old_version/$new_version/g" "$file"

mvn clean test -Dmaven.test.skip=false -DfailIfNoTests=false || true

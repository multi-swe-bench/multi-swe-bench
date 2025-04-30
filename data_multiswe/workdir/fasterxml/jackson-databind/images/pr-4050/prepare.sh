#!/bin/bash
set -e

cd /home/jackson-databind
git reset --hard
bash /home/check_git_changes.sh
git checkout 035fba39559386e16a5017060a6047e733b18599
bash /home/check_git_changes.sh

file="/home/jackson-databind/pom.xml"
old_version="2.16.0-SNAPSHOT"
new_version="2.16.3-SNAPSHOT"
sed -i "s/$old_version/$new_version/g" "$file"

mvn clean test -Dmaven.test.skip=false -DfailIfNoTests=false || true

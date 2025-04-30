#!/bin/bash
set -e

cd /home/jackson-databind
git reset --hard
bash /home/check_git_changes.sh
git checkout e7ab4559e75c38eae89adcc74b8c54bd053a049f
bash /home/check_git_changes.sh

file="/home/jackson-databind/pom.xml"
old_version="2.14.0-SNAPSHOT"
new_version="2.14.4-SNAPSHOT"
sed -i "s/$old_version/$new_version/g" "$file"

mvn clean test -Dmaven.test.skip=false -DfailIfNoTests=false || true

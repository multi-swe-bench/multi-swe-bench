#!/bin/bash
set -e

cd /home/gson
git reset --hard
bash /home/check_git_changes.sh
git checkout 3f4ac29f9112799a7374a99b18acabd0232ff075
bash /home/check_git_changes.sh

mvn clean test -Dmaven.test.skip=false -DfailIfNoTests=false || true

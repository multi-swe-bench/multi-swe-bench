#!/bin/bash
set -e

cd /home/gson
git reset --hard
bash /home/check_git_changes.sh
git checkout 0aaef0fd1bb1b9729543dc40168adfb829eb75a4
bash /home/check_git_changes.sh

mvn clean test -Dmaven.test.skip=false -DfailIfNoTests=false || true

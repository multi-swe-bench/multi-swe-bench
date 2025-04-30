#!/bin/bash
set -e

cd /home/gson
git reset --hard
bash /home/check_git_changes.sh
git checkout 6d2557d5d1a8ac498f2bcee20e5053c93b33ecce
bash /home/check_git_changes.sh

mvn clean test -Dmaven.test.skip=false -DfailIfNoTests=false || true

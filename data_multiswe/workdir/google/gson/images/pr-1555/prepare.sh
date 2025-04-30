#!/bin/bash
set -e

cd /home/gson
git reset --hard
bash /home/check_git_changes.sh
git checkout aa236ec38d39f434c1641aeaef9241aec18affde
bash /home/check_git_changes.sh

mvn clean test -Dmaven.test.skip=false -DfailIfNoTests=false || true

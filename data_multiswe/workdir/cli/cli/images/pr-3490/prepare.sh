#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout 5821065ac0e7e52fc688e249a99210ec85773fe6
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true


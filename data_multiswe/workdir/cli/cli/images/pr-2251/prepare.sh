#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout 2afc462cd0d7f9526ee3cbe90cae56121b815b1b
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true


#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout fd4f2c9c1f76cd66a26322ce640894a4f2deaff7
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true


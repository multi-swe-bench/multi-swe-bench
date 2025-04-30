#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout 3f37d7e372857c17141f290aeac404babc0282cc
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true


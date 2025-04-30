#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout 8288011149e71d5658b80ebef393522ba2d0e7cc
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true


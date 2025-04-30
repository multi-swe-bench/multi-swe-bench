#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout cbd6569cb477be4b5425502f2dbc7eb6f1b976e4
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true


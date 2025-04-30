#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout 74a2a241045d9e6df3bbe288f81911b4361871cd
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true


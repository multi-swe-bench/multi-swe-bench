#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout 7d317a81bea0bf6770f9572909ea1c9d5f3f0907
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true


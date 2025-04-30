#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout 2ec473ff2ff6ee17bce0fd4e33402b40e20f1e0a
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true


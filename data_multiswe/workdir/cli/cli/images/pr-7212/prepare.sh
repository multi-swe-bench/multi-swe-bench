#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout 1fc98f6808728cb72bffb6642c81e47632b7cb54
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true


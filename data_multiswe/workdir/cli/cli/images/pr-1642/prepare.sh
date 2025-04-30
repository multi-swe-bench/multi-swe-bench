#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout 5a8df475b98b45f77c2b893b0a98b19ba65f346c
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true


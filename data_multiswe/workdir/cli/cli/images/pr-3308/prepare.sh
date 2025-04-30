#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout 6dba073a23f1a055b618a1311242686c59d299e7
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true


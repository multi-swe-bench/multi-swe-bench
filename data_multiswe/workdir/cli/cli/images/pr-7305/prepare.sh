#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout fe5b142233396ddcfda1cf72c037d8c8ede274e2
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true


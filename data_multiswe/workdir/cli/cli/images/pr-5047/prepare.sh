#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout 583af3e54c506fa1c0e6bc673c2c62a7e6303660
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true


#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout 8cd9641284879610b553061cff0b1297fc8d22ba
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true


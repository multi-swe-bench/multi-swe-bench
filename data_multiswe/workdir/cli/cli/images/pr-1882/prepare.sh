#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout 5430728a0ab3c0351c39732cf2523a64891aba5a
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true


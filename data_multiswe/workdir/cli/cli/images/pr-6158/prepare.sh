#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout ac036c1c5b54800527a6e6eeda4f113fdbca8e59
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true


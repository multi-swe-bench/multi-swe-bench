#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout f02a73b4ccf88a3a4cdd1c54285a013196101b4b
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true


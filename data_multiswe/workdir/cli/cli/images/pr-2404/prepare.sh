#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout c87deab14a0b9782e0853d90b63d7143d49e9250
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true


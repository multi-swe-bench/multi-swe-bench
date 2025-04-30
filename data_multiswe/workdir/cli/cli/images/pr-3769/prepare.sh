#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout 548a91f0cda256ec35fa5aefa61e222d8e2c01cf
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true


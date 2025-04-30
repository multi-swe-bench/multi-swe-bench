#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout 32256d38bf1524aec04f0e0ae63138f87e3458b8
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true


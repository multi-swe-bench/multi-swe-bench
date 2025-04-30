#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout 3fe5026d39f1cb4dacec3793ef45bbe2f416c987
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true


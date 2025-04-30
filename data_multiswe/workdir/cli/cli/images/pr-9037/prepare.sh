#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout f11f0966959080169dfa7604d8a1a3a60170f417
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true


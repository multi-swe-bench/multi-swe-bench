#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout 40ccd2ef9204cc4f9c82755673b35a0f899a6a86
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true


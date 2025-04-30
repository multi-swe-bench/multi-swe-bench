#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout 5023b619099ffdd5dc0d57c0b7f4718706c249b0
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true


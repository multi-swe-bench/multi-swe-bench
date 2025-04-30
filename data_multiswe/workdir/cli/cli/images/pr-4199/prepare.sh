#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout 1af6a669e342e7b5853c561710a9817bdd5d88bd
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true


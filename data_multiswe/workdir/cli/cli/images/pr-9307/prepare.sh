#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout ca1f2a4c48fb84c22ef91994ca6ded011b12d874
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

